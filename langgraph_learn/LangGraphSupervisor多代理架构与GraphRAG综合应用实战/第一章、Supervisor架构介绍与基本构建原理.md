# 1. Supervisor 架构介绍与基本构建原理 

&emsp;&emsp;正如`Magentic-One`的内部结构一样，`LangGraph` 中的 `Supervisor`充当多代理工作流程中的中央控制器，协调各个代理之间的通信和任务分配。它的工作原理是接收一个代理的输出，解释这些消息，然后相应地指导任务流程。它在`LangGraph` 中基于图结构中的节点实现，允许随着任务的发展或新代理的集成而动态交互和灵活调整工作流程，从而优化流程的有效性和速度。其结构如下图所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411111151977.png" width=100%></div>

&emsp;&emsp;实现的思路是：将代理定义为节点，并添加一个 `supervisor` 节点来决定接下来应该调用哪些代理节点。使用条件边根据 `supervisor` 的决策将执行路由到适当的代理节点。我们通过下面的示例来了解其中间的过程：

```python
import getpass
import os
from langchain_openai import ChatOpenAI


# 如果用开源模型，可以用Ollama 接入
# from langchain_ollama import ChatOllama

# llm = ChatOllama(
#     base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
#     model="qwen2.5:72b",
# )


if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")```

&emsp;&emsp;接下来创建代理主管。需要利用`LangGraph`的`StateGraph`、`AgentState`等状态模式来定义`Supervisor`节点的行为和决策逻辑。

```python
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str```

&emsp;&emsp;然后去设置代理主管可以管理的子代理， 添加`FINISH`是为了用来标识 任务是否已经全部完成，可以返回最终的结果了。这就与 `NetWork` 网络代理不同了，`NetWork`网络代理是每一个子代理节点都可以决定是否直接返回`END`，而`supervisor`则是由主管代理节点做一切的决策，这包括是否继续执行，还是结束图的运行状态。

&emsp;&emsp;这里我们定义三个子代理节点，如下：

```python
members = ["chat", "coder", "sqler"]
options = members + ["FINISH"]```

&emsp;&emsp;接下来定义主管节点。主管节点常见的模式是接收状态模式中的相关数据，让大模型根据实时的任务进展自主决定下一步呼叫哪个代理，并通过结构化输出（例如，强制它返回带有“next_agent”字段），以维持图完整的运行状态，直至输出`__end__`，相关代码如下图所示：

```python
from typing import Literal
from typing_extensions import TypedDict
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""

    next: Literal[*options]```

&emsp;&emsp;`Literal`是`Python`的`typing`模块中的一个类型，用于定义一个变量的具体值的类型限制。当使用`Literal`时，实际上是在告诉`Python`，变量的值必须是指定的几个值中的一个。而 `next: Literal["chat", "coder", "sqler"]`意味着`next`属性只能赋予三个字符串值之一："chat"、"coder"、"sqler"或"FINISH"， 分别用来表示使用哪一个子代理来执行任务，或者直接通过`END`结束当前的图。

```python
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

def supervisor(state: AgentState):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- chat: Responds directly to user inputs using natural language.\n"
        "- coder: Activated for tasks that require mathematical calculations or specific coding needs.\n"
        "- sqler: Used when database queries or explicit SQL generation is needed.\n\n"
        "Given the following user request, respond with the worker to act next."
        " Each worker will perform a task and respond with their results and status."
        " When finished, respond with FINISH."
    )

    messages = [{"role": "system", "content": system_prompt},] + state["messages"]

    response = llm.with_structured_output(Router).invoke(messages)

    next_ = response["next"]
    
    if next_ == "FINISH":
        next_ = END
    
    return {"next": next_}```

&emsp;&emsp;接下来依次子代理，每个代理通过`Node`的形式来定义。关键在于：**每个子代理节点在执行完内部逻辑后，在更新全局状态模式的时候，要通过添加`name`= `代理名称` 的方式告诉`supervisor`代理，该信息是哪个子代理返回的数据。要与`members`中的定义保持一致。** 代码如下所示：

```python
def chat(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chat")]   # 这里要添加名称
    return {"messages": final_response}

def coder(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="coder")]   # 这里要添加名称
    return {"messages": final_response}

def sqler(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="sqler")]  # 这里要添加名称
    return {"messages": final_response}```

&emsp;&emsp;接下来定义状态图，首先添加所有节点：

```python
builder = StateGraph(AgentState)

# builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("coder", coder)
builder.add_node("sqler", sqler)```

&emsp;&emsp;然后让每个子代理在完成工作后总是向主管“汇报”，即需要构建它们之间的边。如下所示：

```python
for member in members:
    # 我们希望我们的工人在完成工作后总是向主管“汇报”
    builder.add_edge(member, "supervisor")```

&emsp;&emsp;然后在图状态中填充`next`字段，路由到具体的某个节点或者结束图的运行，从来指定如何执行接下来的任务。

```python
builder.add_conditional_edges("supervisor", lambda state: state["next"])

# 添加开始和节点
builder.add_edge(START, "supervisor")

# 编译图
graph = builder.compile()```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;编译完成后，就可以进行问答了，这里我们测试几轮不同的问题类型：

```python
for chunk in graph.stream({"messages": "你好，请你介绍一下你自己"}, stream_mode="values"):
    print(chunk)```

```python
for chunk in graph.stream({"messages": "你好，帮我生成一个二分查找的Python代码"}, stream_mode="values"):
    print(chunk)```

```python
for chunk in graph.stream({"messages": "我想查询数据库中 data 表的所有数据，"}, stream_mode="values"):
    print(chunk)```

```python
all_chunk = []

for chunk in graph.stream({"messages": "我想查询数据库中 data 表的所有数据，"}, stream_mode="values"):
    all_chunk.append(chunk)```

```python
all_chunk[-1]['messages'][-1].content```

&emsp;&emsp;如上所示，`supervisor` 的核心构建依赖于状态模式。在此模式中，通过 `next` 字段将主管与各个子代理连接起来。通过前面的示例，我们已经了解了如何构建 `supervisor`。接下来，我们将把这些节点替换成具有实际功能的 `Agent`。
