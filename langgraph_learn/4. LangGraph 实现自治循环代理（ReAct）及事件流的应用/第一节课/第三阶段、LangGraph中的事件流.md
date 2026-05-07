## <center>第三阶段、LangGraph中的事件流</center>

### 1. 流式输出概述

&emsp;&emsp;大模型的流式输出功能首次在《Ch.6 OpenAI Assistant API 高阶应用》中提到。**流式输出的作用在于，它能实时捕捉并输出任务处理过程中的状态变化。**

&emsp;&emsp;在实际应用中，流式输出尤其适用于需要快速反馈的业务场景。**大语言模型可能需要几秒钟才能生成对查询的完整响应，这远远慢于应用程序对最终用户的响应速度约为 200-300 毫秒的阈值。**

&emsp;&emsp;让应用程序感觉响应更快的关键策略是显示中间进度；即，通过 `token` 流式传输大模型`Token`的输出，以此来显著提升用户体验。

### 2. LangChain中的流式输出

&emsp;&emsp;在`LangGraph` 框架中的流式输出实现方式与`LangChain`一样通过回调系统实现。**在`LangChain`中的流式输出是：以块的形式传输最终输出，即一旦监测到有可用的块，就直接生成它。**

```python
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

chunks = []
async for chunk in llm.astream("你好，请你详细的介绍一下你自己。"):
    chunks.append(chunk)
    print(chunk.content, end="|", flush=True)
```

&emsp;&emsp;每一个块，都是一个`AIMessageChunk`对象，代表`AIMessage`对象的一部分。消息块在设计上是可加的。

### 3. LangGraph使用流输出

&emsp;&emsp;`LangGraph`框架中的流式传输涉及在各个节点请求更新时跟踪图状态的变化。调用`.stream`和`.astream`方法时可以指定几种不同的模式：

- **"values"**：在图中的每个步骤之后流式传输**状态**的完整值
- **"updates"**：在图中的每个步骤之后将更新流式传输到状态
- **"debug"**：在整个图的执行过程中流式传输尽可能多的信息
- **"messages"**：记录每个`messages`中的增量`token`
- **"custom"**：自定义流，通过`LangGraph 的 StreamWriter`方法

#### 3.1 values模式

```python
def print_stream(stream):
    for sub_stream in stream:
        message = sub_stream["messages"][-1]
        message.pretty_print()

input_message = {"messages": ["你好，南京现在的天气怎么样？"]}
print_stream(graph.stream(input_message, stream_mode="values"))
```

#### 3.2 updates模式

```python
def print_stream(stream):
    for sub_stream in stream:
        print(sub_stream)

input_message = {"messages": ["你好，天津、内蒙现在的天气怎么样？"]}
print_stream(graph.stream(input_message, stream_mode="updates"))
```

#### 3.3 异步流输出

&emsp;&emsp;在异步开发环境中，可以使用`astream`方法来实现流式传输：

```python
async for chunk in graph.astream(input={"messages": ["你好，四川的天气怎么样？"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()
```

### 4. LangGraph中的事件流

&emsp;&emsp;对于上述使用的`.stream()`或`.astream()`仅流式传输链中最后一步的输出。当我们的`AI Agent`是一个使用了多个大模型调用的更复杂的链时，我们有时希望在最终输出中也使用到一些中间值。

&emsp;&emsp;如果想获取到中间事件和步骤，可以使用`LangGraph`框架中的 `astream_events` 方法（此方法仅支持异步）。

#### 4.1 astream_events基本用法

```python
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    kind = event["event"]
    print(f"{kind}: {event['name']}")
```

&emsp;&emsp;这个过程明确标识了`Agent`执行的每个阶段：
- `on_chain_start: LangGraph`：开始
- `on_chain_end: LangGraph`：写入`__start__`节点
- `on_chat_model_start`：开始聊天模型调用
- `on_chat_model_stream`：按token的增量流式返回
- `on_chat_model_end`：聊天模型输出完全部内容后停止
- `ChannelWrite<call_model,messages>`：将结果写回通道

#### 4.2 事件数据结构

&emsp;&emsp;所有事件都会包含`event`、`name`和`data`字段：
- **event**：正在发出的事件类型
- **name**：这是事件的名称
- **data**：这是与事件关联的数据

#### 4.3 事件过滤

&emsp;&emsp;基于事件字段可以进行过滤：

```python
async for event in graph.astream_events({"messages": ["你好，请你介绍一下你自己"]}, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="|", flush=True)
```

### 5. 拓展思考

#### 5.1 流式输出的应用场景

&emsp;&emsp;流式输出在以下场景中特别有用：
1. **聊天机器人**：实时显示AI的思考过程，提升用户体验
2. **长文本生成**：让用户提前看到部分结果，减少等待焦虑
3. **调试与追踪**：详细了解Agent的执行过程
4. **实时监控**：监控工作流中各个节点的执行状态

#### 5.2 stream与astream_events的选择

&emsp;&emsp;选择建议：
- **简单场景**：只需要最终结果或最终状态的增量更新，使用`stream`或`astream`
- **复杂场景**：需要追踪Agent执行过程中的每个事件，使用`astream_events`
- **调试场景**：需要详细了解图执行过程中的状态变化，使用`stream_mode="debug"`

#### 5.3 性能考虑

&emsp;&emsp;流式输出虽然能提升用户体验，但也带来额外的开销：
- 每个事件都需要通过网络传输
- 客户端需要处理增量更新
- 可能会增加整体响应时间

&emsp;&emsp;在实际应用中，需要在用户体验和性能之间找到平衡点。