## 3.2 LangGraph中的事件流

&emsp;&emsp;对于上述使用的`.stream()`或`.astream()`仅流式传输链中最后一步的输出，这对于一些对话聊天类的应用程序来说基本就足够了，但是当我们的`AI Agent`是一个使用了多个大模型调用的更复杂的链时，我们有时希望在最终输出中也使用到一些中间值。例如，在构建RAG对话应用程序时，很多场景都是最终生成的响应 + 检索到的源文档一起返回给用户，例如：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241030125431836.png" width=100%></div>

&emsp;&emsp;如果想获取到这样的中间事件和步骤，可以使用`LangGraph`框架中的 `astream_events `方法，注意：此方法仅支持异步。用来访问自定义事件和中间输出。使用该方法运行图时，可以得到如下相关事件：

> LangChain CallBack：https://python.langchain.com/docs/concepts/callbacks/

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241029114040337.png" width=100%></div>

&emsp;&emsp;如下代码可以打印包含流式聊天模型输出的事件，其中 version="v2" 参数是指定使用 测试版 API 的版本，现在必须指定。 


```python
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    kind = event["event"]
    print(f"{kind}: {event['name']}")```

&emsp;&emsp;这个过程明确标识了`Agent`执行的每个阶段。从`on_chain_start: LangGraph `开始，写入`__start__`节点，启动`call_model`节点（ on_chain_start: call_model ）。然后开始聊天模型调用（ on_chat_model_start: ChatOpenAI ), 按`token`的增量流式返回 ( on_chat_model_stream: ChatOpenAI ），直到聊天模型（ on_chat_model_end: ChatOpenAI ）输出完全部内容后停止。继而将结果写回通道（ ChannelWrite<call_model,messages> ），再次回到`call_model`节点做决策，最终完成整个图的运行流程。

&emsp;&emsp;我们可以从中提取具体的某个 `event`（事件），比如：

```python
events = []
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    events.append(event)```

```python
events[0]```

```python
events[10]```

&emsp;&emsp;所有事件都会包含`event` 、 `name`和`data`字段，其中：
- event ：正在发出的事件类型。
- name ：这是事件的名称
- data ：这是与事件关联的数据。

&emsp;&emsp;基于此就可以按照`name`、`tags`或`type`等不同的字段来进行事件过滤，比如我们现在选择仅包含聊天模型的输出：

```python
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event, end="|", flush=True)```

&emsp;&emsp;每种类型的事件都包含不同格式的数据。而其中`data`是一个非常重要的，包含此事件的实际数据。在`on_chat_model_stream`事件中，就是需要响应的流式`Token`，如上图所示是一个 `AIMessageChunk`，其中包含消息的`content`以及`id` ,提取的代码就非常简单了，和我们上面实现的方式一致，即直接采用如下代码：

```python
first = True
async for msg, metadata in graph.astream({"messages": ["你好，请你介绍一下你自己"]}, stream_mode="messages"):
    if msg.content and not isinstance(msg, HumanMessage):
        print(msg.content, end="|", flush=True)

    if isinstance(msg, AIMessageChunk):
        if first:
            gathered = msg
            first = False
        else:
            gathered = gathered + msg

        if msg.tool_call_chunks:
            print(gathered.tool_calls)```

&emsp;&emsp;stream_mode="messages"模式是直接做的格式化提取的实现过程，当然，理解了上述事件流，我们也可以直接在当前的流程下自定义数据流，比如：

```python
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="|", flush=True)```

&emsp;&emsp;由此可见，在处理事件流中的信息时，我们可以根据实际需求灵活地选择输出和展示的内容格式。这种灵活性正是在复杂业务流程中引入事件流的核心原因。

&emsp;&emsp;至此，我们就完整实现了在`LangGraph`中`ReAct`自治代理的完整构建，对于这个预构建的`ReAct`组件，它是集成了外部工具、记忆和规划三个核心概念，所以除了我们可以自定义外部工具以外，还可以给它制定不同的步骤规划方式，即`Planning`，以及通过`Memory`去赋予`Agent`多轮对话的能力，而这两部分的内容，我们将在下一节课程中展开详细的探讨和实践。
