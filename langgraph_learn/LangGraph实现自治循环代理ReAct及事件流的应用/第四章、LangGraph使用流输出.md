## 3.1 LangGraph使用流输出

&emsp;&emsp;`LangGraph`框架中的工作流中由各个步骤的节点和边组成。这里的流式传输涉及在各个节点请求更新时跟踪图状态的变化。这样可以更精细地监控工作流中当前处于活动状态的节点，并在工作流经过不同阶段时提供有关工作流状态的实时更新。其实现方式也是和`LangChain`一样通过`.stream`和`.astream`方法执行流式输出，只不过适配到了图结构中。调用`.stream`和`.astream`方法时可以指定几种不同的模式，即：

- "values" ：在图中的每个步骤之后流式传输**状态**的完整值。
- "updates" ：在图中的每个步骤之后将更新流式传输到状态。如果在同一步骤中进行多个更新（例如运行多个节点），则这些更新将单独流式传输。
- "debug" ：在整个图的执行过程中流式传输尽可能多的信息，主要用于调试程序。
- "messages"：记录每个`messages`中的增量`token`。
- "custom"：自定义流，通过`LangGraph 的 StreamWriter`方法

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241028182221186.png" width=100%></div>

&emsp;&emsp;首先来看`Stream`方法，该方法返回一个迭代器，在生成输出块时同步生成它们。我们可以使用`for`循环来实时处理每个块。生成的块的类型取决于正在流式传输的组件。例如，当从大模型流式传输时，每个组件将是一个`AIMessageChunk`，但是，对于其他组件，块可能会有所不同。其`LangGraph`框架中实现的源码如下：

> LangGraph Graph stream：https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.graph.CompiledGraph.stream

```python
def stream(
    self,
    input: Union[dict[str, Any], Any],  # 图中的输入，从状态中取值
    config: Optional[RunnableConfig] = None,
    *,
    stream_mode: Optional[Union[StreamMode, list[StreamMode]]] = None,
    output_keys: Optional[Union[str, Sequence[str]]] = None,  # 流媒体的键，默认为所有非上下文通道。
    interrupt_before: Optional[Union[All, Sequence[str]]] = None,  # 中断之前的节点，默认为图中的所有节点。
    interrupt_after: Optional[Union[All, Sequence[str]]] = None,   # 中断之后的节点，默认为图中的所有节点。
    debug: Optional[bool] = None,   #  执行过程中是否打印调试信息，默认为False。
    subgraphs: bool = False,  # 是否流式传输子图
) -> Iterator[Union[dict[str, Any], Any]]:
```

- **values ：在图表的每个步骤之后流式传输状态的完整值。**

```python
def print_stream(stream):
    for sub_stream in stream:
        # print(sub_stream)  # 就是上面的示例中非流式直接调用的全部信息
        message = sub_stream["messages"][-1]
        message.pretty_print()

input_message = {"messages": ["你好，南京现在的天气怎么样？"]}
print_stream(graph.stream(input_message, stream_mode="values"))```

- **updates ：在图中的每个步骤之后将更新流式传输到状态。**

```python
def print_stream(stream):
    for sub_stream in stream:
        print(sub_stream)  # 就是上面的示例中非流式直接调用的全部信息

input_message = {"messages": ["你好，天津、内蒙现在的天气怎么样？"]}
print_stream(graph.stream(input_message, stream_mode="updates"))```

- **debug ：在整个图中的执行过程中流式传输尽可能多的信息**

```python
def print_stream(stream):
    for sub_stream in stream:
        print(sub_stream)  # 就是上面的示例中非流式直接调用的全部信息

input_message = {"messages": ["你好，天津、内蒙现在的天气怎么样？"]}
print_stream(graph.stream(input_message, stream_mode="debug"))```

&emsp;&emsp;如果在异步开发环境中，则可以使用`astream`方法来实现流式传输，是专为非阻塞工作流程而设计。可使用的模式和`stream`是一致的，只不过需要调整为异步函数的定义方法，代码如下所示：

```python
async for chunk in graph.astream(input={"messages": ["你好，四川的天气怎么样？"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()```

&emsp;&emsp;如果只想得到最终结果，可以使用相同的方法并只跟踪收到的最后一个值，代码如下：

```python
async for chunk in graph.astream(input={"messages": ["你好，四川的天气怎么样？"]}, stream_mode="values"):
    final_result = chunk```

```python
final_result["messages"][-1].pretty_print()```

```python
inputs = {"messages": [("human", "你好，乌鲁木齐的天气怎么样？")]}
async for chunk in graph.astream(inputs, stream_mode="updates"):
    for node, values in chunk.items():
        print(f"接收到的更新节点: '{node}'")
        print(values)
        print("\n\n")```

&emsp;&emsp;而如果我们想流式传输每个过程中的 `Tokens`， 代码如下：

```python
from langchain_core.messages import AIMessageChunk, HumanMessage

inputs = [HumanMessage(content="what is the weather in sf")]

first = True
async for msg, metadata in graph.astream({"messages": ["你好，帮我查询一下数据库中都有哪些城市的天气数据"]}, stream_mode="messages"):
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

&emsp;&emsp;`astream`中其他的模式大家可以自行尝试，这里不重复进行说明，总体而言，我们要理解的是，同步`stream`和异步`astream`都是流式传输的默认实现，用于流式传输链中的最终输出。
