## <center>第一阶段、Supervisor架构介绍与基本构建原理</center>

&emsp;&emsp;在多代理系统领域的众多框架中，`LangGraph` 是作为**编排代理交互**和**简化复杂工作流程**的强大底层工具而脱颖而出。 一个关键方面是它**能够促进代理主管的角色，代理主管是负责在代理团队之间管理和委派任务的关键实体**。但是，`LangGraph` 是处理多代理工作流程的最佳选择吗？大家将能够通过本节课程的学习和实践得到一个清晰的认知。

&emsp;&emsp;在具体介绍`Supervisor`架构之前，我们先来看一个以`Supervisor`为基础架构构建而成的一个最具代表性的工具：就是微软刚刚发布的`Magentic-One`多代理系统。

&emsp;&emsp;`Magentic-One` 是 `Microsoft` 推出的一种**新的通用多代理系统， 同时也是一个基于多智能体 `AI` 的解决方案**。在`Magentic-One`系统中允许多个 `AI` 代理协同工作，每个代理都充当其领域的"专家"去完成特定的功能，例如在软件开发过程中，一个代理会编写文档，另一个代理会审查代码，第三个代理执行质量测试等，通过这种方式实现协同效应，加速流程并改善结果，从而解决高度复杂的问题和任务。

&emsp;&emsp;谈论到具体的功能，`Magentic-One` 此次发布了 5 个默认智能代理，架构组成如下：

- 高级代理 `Orchestrator`：负责高级规划和任务管理的核心组件。它可以指导其他代理，跟踪进度，并在进度停滞时重新规划。
- 四个专业代理支持`Orchestrator`调度，分别是：
  - WebSurfer（网络代理）：管理用于导航和与网页交互的 Web 浏览器。 它可以基于 Chromium 浏览器运行，执行网页搜索、点击以及输入和汇总网页内容。
  - FileSurfer（文件代理）：处理本地文件管理和导航，基于 markdown 的文件预览应用程序读取本地文件。
  - Coder（编码代理）： 专门从事编写和分析代码。
  - ComputerTerminal（PC代理）：提供用于执行程序和安装库的控制台访问权限（即Shell控制台）。

&emsp;&emsp;其五个代理之间的关系如下图所示：

![Magentic-One架构图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411141040146.png)

&emsp;&emsp;这是一个具体的用户任务在`Magentic-One `中的执行过程：

![Magentic-One执行流程图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411141046082.png)

&emsp;&emsp;任务需求：`Orchestrator` 收到一个任务，用于在一个图像中提取 `Python` 代码，运行`Python`代码，处理一系列字符串，输出是一个`URL`，其中包含`C++`源代码，需要进一步编译并运行这段`C++`源代码后，返回第三和第五个整数的和。`Orchestrator` 通过以下步骤进行管理和协调完成该复杂任务：
- 第 1 步：`FileSurfer` 代理访问图像，提取 `Python` 代码。
- 第 2 步：`Coder` 代理分析 `Python` 代码。
- 第 3 步：`ComputerTerminal` 执行 `Python` 代码，为 `C++` 代码生成 `URL`。
- 第 4 步： `WebSurfer` 访问 `URL` 并提取 `C++` 代码。
- 第 5 步：另一个 `Coder` 代理分析 `C++` 代码。
- 第 6 步： `ComputerTerminal` 代理执行 `C++` 代码，计算并返回最终结果，完成任务。

&emsp;&emsp;`Magentic-One`的最大特点是可以调整和适应实时变化，使系统能够快速响应新的条件或数据。这种灵活性在客户服务等动态环境中至关重要，因为在这些环境中，查询和要求可能会不断变化。这种覆盖范围是执行需要不同类型分析和响应的复杂流程的关键。而`Supervisor`在大多数情况下，处理的都是类似的工作流编排任务。

> Magentic-One 更加详细的介绍及本地部署使用的方法，请查看《大模型与Agent开发实战课》 - Agent模块的加餐视频，已上传至小鹅通。

&emsp;&emsp;`Magentic-One` 底层是基于`AutoGen`而构建的，接下来我们就来看一下，在`LLangGraph` 中 如何通过 `Supervisor` 架构复现这样的复杂工作流。

### 1. Supervisor 架构介绍与基本构建原理

&emsp;&emsp;正如`Magentic-One`的内部结构一样，`LangGraph` 中的 `Supervisor`充当多代理工作流程中的中央控制器，协调各个代理之间的通信和任务分配。它的工作原理是接收一个代理的输出，解释这些消息，然后相应地指导任务流程。它在`LangGraph` 中基于图结构中的节点实现，允许随着任务的发展或新代理的集成而动态交互和灵活调整工作流程，从而优化流程的有效性和速度。其结构如下图所示：

![Supervisor架构图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411111151977.png)

&emsp;&emsp;实现的思路是：将代理定义为节点，并添加一个 `supervisor` 节点来决定接下来应该调用哪些代理节点。使用条件边根据 `supervisor` 的决策将执行路由到适当的代理节点。我们通过下面的示例来了解其中间的过程：

```python
import getpass
import os
from langchain_openai import ChatOpenAI

# 如果用开源模型，可以用Ollama 接入
# from langchain_ollama import ChatOllama

# llm = ChatOllama(
#     base_url = "http://192.168.110.131:11434",
#     model="qwen2.5:72b",
# )

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")
```

&emsp;&emsp;接下来创建代理主管。需要利用`LangGraph`的`StateGraph`、`AgentState`等状态模式来定义`Supervisor`节点的行为和决策逻辑。

```python
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str
```

&emsp;&emsp;然后去设置代理主管可以管理的子代理， 添加`FINISH`是为了用来标识 任务是否已经全部完成，可以返回最终的结果了。这就与 `NetWork` 网络代理不同了，`NetWork`网络代理是每一个子代理节点都可以决定是否直接返回`END`，而`supervisor`则是由主管代理节点做一切的决策，这包括是否继续执行，还是结束图的运行状态。

&emsp;&emsp;这里我们定义三个子代理节点，如下：

```python
members = ["chat", "coder", "sqler"]
options = members + ["FINISH"]
```

&emsp;&emsp;接下来定义主管节点。主管节点常见的模式是接收状态模式中的相关数据，让大模型根据实时的任务进展自主决定下一步呼叫哪个代理，并通过结构化输出（例如，强制它返回带有"next_agent"字段），以维持图完整的运行状态，直至输出`__end__`，相关代码如下图所示：

```python
from typing import Literal
from typing_extensions import TypedDict
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""

    next: Literal[*options]
```

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

    return {"next": next_}
```

&emsp;&emsp;接下来依次子代理，每个代理通过`Node`的形式来定义。关键在于：**每个子代理节点在执行完内部逻辑后，在更新全局状态模式的时候，要通过添加`name`= `代理名称` 的方式告诉`supervisor`代理，该信息是哪个子代理返回的数据。要与`members`中的定义保持一致。** 代码如下所示：

```python
def chat(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chat")]
    return {"messages": final_response}

def coder(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="coder")]
    return {"messages": final_response}

def sqler(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="sqler")]
    return {"messages": final_response}
```

&emsp;&emsp;接下来定义状态图，首先添加所有节点：

```python
builder = StateGraph(AgentState)

# builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("coder", coder)
builder.add_node("sqler", sqler)
```

&emsp;&emsp;然后让每个子代理在完成工作后总是向主管"汇报"，即需要构建它们之间的边。如下所示：

```python
for member in members:
    # 我们希望我们的工人在完成工作后总是向主管"汇报"
    builder.add_edge(member, "supervisor")
```

&emsp;&emsp;然后在图状态中填充`next`字段，路由到具体的某个节点或者结束图的运行，从来指定如何执行接下来的任务。

```python
builder.add_conditional_edges("supervisor", lambda state: state["next"])

# 添加开始和节点
builder.add_edge(START, "supervisor")

# 编译图
graph = builder.compile()
```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

&emsp;&emsp;编译完成后，就可以进行问答了，这里我们测试几轮不同的问题类型：

```python
for chunk in graph.stream({"messages": "你好，请你介绍一下你自己"}, stream_mode="values"):
    print(chunk)
```

```python
for chunk in graph.stream({"messages": "你好，帮我生成一个二分查找的Python代码"}, stream_mode="values"):
    print(chunk)
```

```python
for chunk in graph.stream({"messages": "我想查询数据库中 data 表的所有数据，"}, stream_mode="values"):
    print(chunk)
```

```python
all_chunk = []

for chunk in graph.stream({"messages": "我想查询数据库中 data 表的所有数据，"}, stream_mode="values"):
    all_chunk.append(chunk)

all_chunk[-1]['messages'][-1].content
```

&emsp;&emsp;如上所示，`supervisor` 的核心构建依赖于状态模式。在此模式中，通过 `next` 字段将主管与各个子代理连接起来。通过前面的示例，我们已经了解了如何构建 `supervisor`。接下来，我们将把这些节点替换成具有实际功能的 `Agent`。

## 拓展思考

### 1. 深度概念

&emsp;&emsp;**Supervisor架构与Network架构的核心区别？**

&emsp;&emsp;Supervisor架构采用中央控制模式，由Supervisor统一决策下一步调用哪个代理，而不像Network架构那样每个代理都可以直接与其他代理通信。这种设计有以下优势：
- **集中控制**：所有决策都通过Supervisor，避免了混乱的路由
- **简化调试**：流程更容易追踪和理解
- **易于扩展**：新增代理只需向Supervisor注册

&emsp;&emsp;**状态模式中`next`字段的作用？**

&emsp;&emsp;`next`字段是Supervisor架构的核心，它决定了图的执行路径：
- 当Supervisor决定调用某个子代理时，`next`指向该代理
- 当任务完成时，`next`指向`END`
- 通过条件边根据`next`的值路由到相应的节点

&emsp;&emsp;**为什么子代理需要添加`name`参数？**

&emsp;&emsp;子代理返回消息时添加`name`参数是为了让Supervisor能够识别消息来自哪个代理。这样Supervisor就可以根据消息内容和来源做出更好的路由决策。

&emsp;&emsp;**Supervisor架构的优缺点？**

| 优点 | 缺点 |
|------|------|
| 中央控制，流程清晰 | Supervisor可能成为瓶颈 |
| 易于调试和监控 | 依赖Supervisor的决策质量 |
| 扩展性好 | 单点故障风险 |
