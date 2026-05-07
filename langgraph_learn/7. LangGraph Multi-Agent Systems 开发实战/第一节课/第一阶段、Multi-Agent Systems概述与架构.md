## <center>第一阶段、Multi-Agent Systems概述与架构</center>

&emsp;&emsp;本节课我们将围绕 `LangGraph` 框架中的多智能体系统`Multi-Agent Systems`展开学习和应用的实践。

&emsp;&emsp;`Agent`到底应该如何去定义？ 什么样的应用程序能算的上一个`Agent`？ 到现在仍然没有特别一个明确的说法和界定。有的人认为只要应用程序中集成了能够处理全领域知识查询的大模型，它就可被视为一个`Agent`，而更多的一部人则认为这还远不够，他们会觉得只有当一个应用程序能像人类一样思考并自主处理复杂任务时，才真正符合 `Agent` 的标准。大家应该都听过这样一种观点：大模型的发展使得人工通用智能（AGI）在未来成为现实的可能性也越来越大。在这个过程中，基础的`Agent`扮演关键角色。那么，什么样的`Agent`最符合未来的发展趋势呢？

&emsp;&emsp;我们来看看大模型行业巨头`OpenAI`对`AI Agent`的理解。

&emsp;&emsp;**在2024年7月初，`OpenAI` 的领导层在全体内部员工会议上的分享中，定义了 `AI` 的五个不同阶段，共同去努力实现构建通用人工智能的最终目标**。这五个阶段涵盖了从基本的聊天机器人到能够完成整个组织工作的高级系统，而第五个阶段所需要具备的能力就是可以构造出一种智能且能够执行与人类相同的所有工作的 `AI` 。各个阶段如下所示：

![AI发展阶段图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411121340521.png)

- **Stage 1. Chatbots**

&emsp;&emsp;`AI`的第一阶段称为**聊天机器人**。`OpenAI` 自己的 `ChatGPT` 就是这个阶段的最佳例子，它在 `2022` 年底发布时以其用自然语言交谈的能力震惊了世界。我们可以使用聊天机器人来提高其内部生产力，这些聊天机器人乍一看似乎非常聪明，但是**通常会充满信心地编造和呈现虚假信息**，所以如果它们不能有效的融入私人/企业的数据，没有太多的商业用途。

- **Stage 2: Reasoners**

&emsp;&emsp;`OpenAI` 定义的`AI`第二阶段为推理者。**推理者是可以完成基本问题解决任务的系统，不需要借助任何工具，通过改进推理增强大模型处理各种任务的能力**，这包括从做出重大科学发现到规划和构建新的软件应用程序。正如 OpenAI 发布的 `o1-preview`。

![推理者示例图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411121348836.png)

- **Stage 3: Agents**

&emsp;&emsp;`AI`的第三个阶段，`OpenAI` 认为是`AI Agent`，它是可以代表用户采取行动的系统。而这个阶段也就是我们目前一直在学习的相关内容，如`LangGraph`的`Router Agent`、`Tool Calling Agent`以及`ReAct`，我们通过工作流的编排去让应用程序自主完成一些特定的用户需求和任务目标，整个过程不需要任何的人工介入。

- **Stage 4: Innovators**

&emsp;&emsp;第四个阶段的创新者是指：**可以帮助发明的人工智能。这类应用帮助人们产生想法、编写代码和进行创作，它们以专门开发的 `AI` 系统的形式出现，以帮助原型、构建和制造物理产品**。而我们在2023年第一期的《大模型技术实战课》中，就为大家研发并详细介绍了用`AI`开发`AI`的落地案例，感兴趣的小伙伴可以进行学习和实践。

![创新者示例图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411121409231.png)

- **Stage 5: Organizations**

&emsp;&emsp;**在 `OpenAI` 提出的人工智能的最后阶段：`AI` 系统将变得足够先进和智能，可以完成整个组织的工作，并将组织归类为智能路线图的最后一步。**

&emsp;&emsp;随着本期课程中`Agent`模块学习进度的推进，大家已经顺利的迈入了`Stage 3: Agents` 阶段。无论是从零到一去构建`ReAct`，还是借助`Assistant API`、`langGraph`框架去实现完全自主循环代理，大家已经能够借助大模型的能力，让其在个人的工作/学习中解放人力的同时提升效率。而接下来的`Stage 4 ~ Stage 5` 两个阶段，我可能有一万种理由去解释为什么现在学习到的知识点还不能够去匹配和适应这两个更高阶段的需求。

### 1. Single-Agent 架构的局限

&emsp;&emsp;就我们目前正在探讨的`LangGraph`框架，`Stage 5：Organizations` 阶段特别强调的`AI`是一个组织，**组织的概念大家应该都比较清楚，它大到一个国家，小到两个人的团队，但它绝不仅仅是一个个体**。但我们之前所学习的，强如完全自主循环代理`ReAct`，它其实做的都是在尝试去打造更强的独立个体，我们通过给它传递更多工具（Tool Calling），赋予上下文的记忆（Memory）等等多种方式让其能够处理越来越发展的任务需求。但随着需求越来越复杂，能够预想到的以下几个非常关键的问题是：

- **`Agent` 有太多工具可供使用，会导致对下一步调用哪个工具做出了混乱的决定。**
- **上下文变得过于复杂，无法清晰的跟踪并传递有效信息。**
- **系统中需要多个专业领域（例如规划师、研究人员、数学专家等），单一的角色背景设定没有办法匹配不同的需求。**

&emsp;&emsp;上面这三个问题很现实的摆在我们面前，行之有效的解决的办法就是：**调整 `Agent` 的架构**。变成如下图所示的一样：

![多代理系统架构图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411121553038.png)

&emsp;&emsp;多代理系统其实就可以非常简单的理解为：**将原本的应用程序拆分成多个较小的独立代理，从而组合而成的系统。这些小的独立代理可以是简单的大模型交互代理，也可以是复杂的 `ReAct` 代理**。举个比较热门的案例，假设我们需要建立一个用于数据分析的`Agent`，则可以设计代理配置：`Agent 1`作为用户意图识别代理，集成大模型用来解析用户的查询和指令，理解其意图和需求，并将用户输入转化为具体的任务。`Agent 2`作为数据分析代理，集成大模型并绑定若干个处理不同数据和需求的工具，提供统计分析、趋势预测和数据可视化服务。当任务涉及到代码生成时，`Agent 3`，即代码执行代理，会接收用户输入的代码，在安全的Python环境中执行这些代码，并返回运行结果，用于代码测试、执行特定算法或自动化任务。

&emsp;&emsp;由此能感受到的是多智能体系统 （MAS） 是通过多个单代理之间的协作来解决复杂的任务，其中多代理系统中集成的每个单代理，都有特定的背景身份和独有的技能。其显著的优势则包含如下三个方面：

- **专业化：当一个系统中可以创建多个专注于特定领域的专家代理，能实现处理更复杂的应用的`AI`系统**。
- **模块化：单独的代理开发模式对于开发、测试和维护完整代理系统是更加容易的**。
- **控制度：显式地控制代理的通信方式，而不仅仅是依赖函数调用**

&emsp;&emsp;**通过`langGraph`前面知识点的学习，我们已经完全掌握了构建`Multi-Agent Systems`三个优势点中的前两个中涉及的方法，即专业化和模块化**。我们知道如何去在`langGraph`中给某个节点（Node）中的大模型赋予特殊的身份背景，这可以通过`SystemMessage`来做到。同样也知道如何去基于`Router Agent`、 `ToolCalling Agent` 或者`ReAct`去构建具备诸如数据分析代理、代码执行代理等完整的构建思路和流程。

&emsp;&emsp;**唯一还欠缺的知识点只有：如何去建立起不同`Agent`之间的通信连接。在`Single-Agent`架构中，我们是通过节点和边去构建图的结构，但在`Multi-Agent`，当简单的节点由复杂的`Agent`来替代，那么如何去建立起不同`Agent`之间的通信关系，就是我们在构建多代理系统时唯一需要关注的事情**。如下图所示：

![代理间通信连接图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411121718908.png)

&emsp;&emsp;在多代理架构中，对于子代理的数量以及应如何连接它们时，没有严格的规则或准则，可以完全依赖开发者的思路和实际的业务场景进行自定义编排。我们要做的是：在功能设计上将较大的目标分解为较小的任务，并创建单独的代理来处理这些任务中的每一个。每个代理都拥有自己的系统提示和身份设定、大模型的接入支持、工具和自定义代码，从而形成多智能实体的协作交互。

### 2. Multi-agent architectures 架构

&emsp;&emsp;继续深入探讨 `Multi-Agent`概念。`LangGraph`利用基于图的结构来定义代理并在它们之间建立连接。在此框架中，每个代理都表示为图中的一个节点，并通过边链接到其它代理。每个代理通过接收来自其他代理的输入并将控制权传递给下一个代理来执行其指定的操作。在`LangGraph` 框架的设计中，主要通过如下几种方法来建立各个子代理之间的通信连接：

- NetWork（网络）：每个代理都可以与其他每个代理通信。任何代理都可以决定接下来要呼叫哪个其他代理。
- Supervisor（主管）：每个代理都与一个 `Supervisor` 代理通信。由 `Supervisor` 代理决定接下来应调用哪个代理。
- Supervisor （tool-calling）： `Supervisor` 架构的一个特例。每个代理都是一个工具。由`Supervisor`代理通过工具调用的方式来决定调用哪些子代理执行任务，以及要传递给这些代理程序的参数
- Hierarchical（分层）：定义具有 `supervisor` 嵌套 `supervisor`多代理系统。这是 `Supervisor` 架构的一种泛化，允许更复杂的控制流。

&emsp;&emsp;各个多代理架构的通信方式如下图所示：

![多代理架构通信方式图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411111115580.png)

&emsp;&emsp;`LangGraph` 非常适合创建多代理工作流，因为它允许将两个或多个代理作为图连接。每个代理都是一个独立的参与者，代理之间的连接由边表示。每个连接边都可以有一个控制条件，用于将信息从一个代理中引导到另一个代理中，并且每个代理都有一个状态，可以在每个流期间使用信息进行更新。

&emsp;&emsp;但是，在具体实践各个不同多代理架构下的具体应用方法之前，我们需要结合`LangGraph`构建图的机制去思考一个问题：**通过`State`可以让一个图中的所有节点共享全局的信息，那么在多代理架构中，当每一个图变成了一个节点，那么不同图之间的状态，应该怎么传递？**

![状态传递问题图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131500079.png)

&emsp;&emsp;在上图所示的架构中，每个子代理（例如Agent 1、Agent 2、Agent 3）由多个内部节点组成，各自通过独立的`State`维护内部节点间的消息传递。举个例子，假设`Agent 1`是一个数据分析师，负责接收并整理关键数据；`Agent 2`则负责进行精细化的计算。在这个过程中，如何有效地在`Agent 1`和`Agent 2`之间传递数据成为了一个关键问题。`Agent 1`需要将数据传递给`Agent 2`进行处理，之后`Agent 2`需要将计算结果返回给`Agent 1`。但是当前的涉及是不支持在代理间传递状态的，即在`Agent 2`的执行过程中无法访问`Agent 1`中的状态。

&emsp;&emsp;因此，如果想让不同`Agent`之间能够做到消息共享，则需要了解 `LangGraph`框架中的`Subgraphs`（子图）相关的概念和使用方法。

### 3. Subgraphs

&emsp;&emsp;`Subgraphs`（子图）指的是能够用作另一个图中的节点的图。**简单理解就是：把一个已经编译好的图，嵌入到另一个已经编译好的图中，并且两个独立图的中的状态可以信息共享**。一个典型的应用就是构建多代理系统架构。它所做的事情是：当把每个独立的`Agent`图结构定义为一个子图时，只要遵守子图的接口（输入和输出模式）规范，那么子图中定义的共享状态就可以在父图中进行使用。如下图所示：

![子图示意图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131619712.png)

&emsp;&emsp;添加子图主要解决的问题就是解决各`Single-Agent`之间的通信问题，即它们如何在图执行期间在彼此之间传递状态。这主要有两种情况：
- **父、子图的状态模式中有共同的键（通道）。**
- **父、子图的状态模式中没有共同的键。（通道）**

&emsp;&emsp;如何理解这两种情况？我们就分别用实际的案例来帮助大家理解这个过程。首先来看第一种情况：**如果父、子图节点中定义的状态模式有共同的键，比如下述情况所示**：

![共享状态键示意图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131857901.png)

&emsp;&emsp;在这个图结构中，`final_answer`作为父图的全局共享状态，被`Sub Graph `子图访问。这个子图通过共享状态键`final_answer`进行交互，同时各自自己独立的内部状态键`summary_answer`。这种设计允许父图与子图之间通过共享状态键`final_answer`进行通信，同时保持各自的状态独立性，实现数据隔离与信息共享的平衡。

&emsp;&emsp;接下来我们设计一个实际应用场景去构建如上图所示的父图与子图相结合的状态图系统。具体来说，我们设计一个评分系统，分为两个主要部分：父图负责处理初步的用户输入，并生成响应，而子图则进一步处理这些响应，进行内容精简和质量评估。以下是具体的代码实现：

- **Step 1. 定义用于构建Agent的大模型实例**

&emsp;&emsp;之前的案例中我们一直使用`GPT`模型构建`Agent`，当然`LangGraph`也支持本地开源模型的接入，所以接下来我们提供两种模型的接入代码供大家结合自己的实际情况进行选择。首先，如果大家在实践时仍然选用`GPT`模型，依然使用如下代码进行`GPT`模型的实例化。

```python
import getpass
import os
from langchain_openai import ChatOpenAI

# 如果GPT模型，用这段代码
# if not os.environ.get("OPENAI_API_KEY"):
#     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# llm = ChatOpenAI(model="gpt-4o-mini")
```

&emsp;&emsp;而如何想要使用本地部署的开源大模型，可以用`LangChain`进行高效的接入。如下代码所示，我们使用`langChain`的`ChatOllama`第三方的集成方法接入本地启动的`Qwen-2.5:72B`模型。

&emsp;&emsp;注意：在执行如下代码之前，需要在本地/云服务器上使用`Ollama`部署并启动对应的模型。

> 关于如何使用`Ollama`启动大模型的详细教程，请查看《开源大模型模块-【Qwen2.5】Qwen2.5介绍与部署流程》课件

```python
# ! pip install  langchain-ollama

# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)
```

&emsp;&emsp;测试一下 `qwen2.5:72b` 模型的连通性，代码如下：

```python
print(llm.invoke("你好，请你介绍一下你自己。").content)
```

- **Step 2. 定义父图的状态模式**

&emsp;&emsp;父图的作用是接收来自用户的输入，这些输入可能是问题、请求或任何形式的查询，使用大模型处理用户输入，生成一个详细的响应。所以涉及两个状态键：用户的输入和大模型针对用户输入的响应。因此定义如下：

```python
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应
```

- **Step 3. 定义父图的节点逻辑**

&emsp;&emsp;节点的功能就是使用大模型处理用户输入，并生成响应。

```python
def parent_node(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}
```

- **Step 4. 定义子图的状态模式**

&emsp;&emsp;对于子图来说，父图生成的响应会传递到子图，子图的第一个节点负责将这个响应缩减为一个简洁的总结。然后在子图的第二个节点，对完整的响应及其总结进行评分。因此涉及的状态模式就如下图所示：

```python
# 定义子图中的状态
class SubgraphState(TypedDict):
    # 这个 key 是和 父图（ParentState）共享的，
    final_answer: str
    # 这个key 是 子图 (subgraph) 中独享的
    summary_answer:str
```

&emsp;&emsp;其中`final_answer`用来接收父图传递过来的响应，`summary_answer`用来接收子图对父图传递过来的响应的总结。

- **Step 5. 定义子图的节点逻辑**

&emsp;&emsp;第一个节点用来将 父图生成一个不超过10个单词的简短总结，第二个节点根据完整的响应及其总结进行综合的评分，代码如下：

```python
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

def subgraph_node_1(state: SubgraphState):
    system_prompt = """
    Please summary the content you receive to 50 words or less
    """
    messages = state['final_answer']  # 这里接收父图传递过来的响应
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"summary_answer": response}

def subgraph_node_2(state: SubgraphState):
    # final_answer 仅能在 子图中使用
    messages = f"""
    This is the full content of what you received：{state["final_answer"]} \n
    This information is summarized for the full content:{state["summary_answer"]}
    Please rate the text and summary information, returning a scale of 1 to 10. Note: Only the score value needs to be returned.
    """

    response = llm.invoke([HumanMessage(content=messages)])

    # 发送共享状态密钥（'user_input'）的更新
    return {"final_answer": response.content}
```

&emsp;&emsp;接下来要明确的是：如果我们希望子图与父图在共享状态键的情况下可以进行通信，需要执行如下两个步骤：

1. **定义子图工作流程并对其进行编译。**

2. **在定义父图工作流时，将编译的子图传递给 `.add_node` 方法。**

- **Step 6. 定义子图的图结构并且进行编译**

```python
from langgraph.graph import START, StateGraph

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()
```

- **Step 7. 定义父图的图结构，并将子图作为节点添加至父图**

```python
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node)

# 将编译后的子图作为一个节点添加到父图中
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()
```

- **Step 8. 可视化完整的图结构**

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

```python
async for chunk in graph.astream({"user_input": "我现在想学习大模型，应该关注哪些技术？"}, stream_mode='values'):
    print(chunk)
```

&emsp;&emsp;当一个图中添加了子图，按照常规的调用方法可以看到父图的最终输出包括子图调用的结果（即字符串 "final_answer"）。如果想进一步查看子图的输出，可以在流式传输时指定 `subgraphs=True`。如下代码所示：

```python
async for chunk in graph.astream({"user_input": "如何理解RAG？"}, stream_mode='values', subgraphs=True):
    print(chunk)
```

&emsp;&emsp;这个案例实现的工作流就让父图和子图借助共享的状态键（通道）进行通信，这是非常常见的一种多代理架构的底层构建模式，这种通信模式要关注的点就是如何设计自己的工作流以通过父图的全局状态键进行各个子图（子代理）的有效交互和信息传递。

**接下来我们看第二种情况：父、子图节点中定义的状态模式没有共同的键的时候，怎么做？**这种情况如下图所示：

![无共享状态键示意图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131909694.png)

&emsp;&emsp;如果父图与子图是完全不同的架构，则会出现上图中无共同键可用的情况。在这种情况下如果仍然想让父图与子图之间能够以某种方式进行通信，则需要定义一个调用子图的 `node` 函数，其作用是：**在调用子图之前将输入（父）状态转换为子图状态，并在从节点返回状态更新之前将结果转换回父状态。** 我们来看下面这个案例：

```python
# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)
```

&emsp;&emsp;父图的状态和节点的逻辑均布发生变化，如下所示：

```python
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应

def parent_node_1(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}
```

&emsp;&emsp;子图中专注于处理自己内部的逻辑，无需关心父图中的状态中都定义了哪些键，如下代码所示：

```python
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

# 定义子图中的状态
class SubgraphState(TypedDict):
    # 以下三个 key 都是 子图 (subgraph) 中独享的
    response_answer: str
    summary_answer:str
    score: str

# 定义第一个节点，用于接收父图中的响应并且做文本摘要
def subgraph_node_1(state: SubgraphState):
    system_prompt = """
    Please summary the content you receive to 50 words or less
    """
    messages = state['response_answer']  # 这里接收父图传递过来的响应
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"summary_answer": response}

# 定义第二个节点：
def subgraph_node_2(state: SubgraphState):
    messages = f"""
    This is the full content of what you received：{state["response_answer"]} \n
    This information is summarized for the full content:{state["summary_answer"]}
    Please rate the text and summary information, returning a scale of 1 to 10. Note: Only the score value needs to be returned.
    """

    response = llm.invoke([HumanMessage(content=messages)])

    # 发送共享状态密钥（'user_input'）的更新
    return {"score": response.content}
```

&emsp;&emsp;正常定义子图并编译。

```python
subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()
```

&emsp;&emsp;接下来的这个函数是关键。**`parent_node_2`用来连接父图与子图之间的网络通信，它通过将父节点与子节点的状态做转化来达到此目的**。代码如下：

```python
def parent_node_2(state: ParentState):
    # 将父图中的状态转换为子图状态
    response = subgraph.invoke({"response_answer": state["final_answer"]})
    # 将子图状态再转换回父状态
    return {"final_answer": response["score"]}
```

```python
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node_1)

# 注意，我们使用的不是编译后的子图，而是调用子图的' node_2 '函数
builder.add_node("node_2", parent_node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()
```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

```python
async for chunk in graph.astream({"user_input": "我现在想学习大模型，应该关注哪些技术？"}, stream_mode='values'):
    print(chunk)
```

```python
all_chunk = []

async for chunk in graph.astream({"user_input": "什么是机器学习？"}, stream_mode='values', subgraphs=True):
    all_chunk.append(chunk)
```

```python
all_chunk[-1][1]["final_answer"]
```

&emsp;&emsp;在上面的案例中，`subgraph state` 完全独立于父 `graph state`，即两者之间没有重叠的键（通道）是最常见的，也是灵活性最高的。其中的关键点在于：**需要在调用子图之前将其输入转换为子图，然后在返回之前转换其输出**，即可正常完成父、子图之间的通信。

&emsp;&emsp;在`LangGraph`中，子图的应用主要用于多代理系统的构建，而如果理解了上面两个案例中通信状态的传递方式，就基本具备了构建多代理系统的必要条件。接下来，我们就针对`LangGraph`框架下的不同多代理架构依次展开详细的探讨和实践。

## 拓展思考

### 1. 深度概念

&emsp;&emsp;**在 Multi-Agent 系统中，如何设计高效的代理间通信协议以减少延迟？**

&emsp;&emsp;代理间通信协议的设计直接影响多代理系统的性能和响应速度。关键考虑因素包括：
- **消息队列机制**：使用异步消息队列可以避免阻塞，提高系统吞吐量
- **状态共享策略**：合理设计状态共享机制，避免不必要的数据传输
- **连接池管理**：复用连接，减少连接建立的开销

&emsp;&emsp;**Subgraph 模式在大型多代理系统中如何保证状态一致性？**

&emsp;&emsp;在复杂的多代理系统中，保证状态一致性是一个挑战。Subgraph模式通过以下方式解决：
- **共享状态通道**：父子图之间通过共享的状态键进行信息传递
- **状态转换函数**：在调用子图前进行状态转换，返回前再转换回来
- **事务性更新**：保证状态更新的原子性

&emsp;&emsp;**基于 Network 的多代理架构与 Supervisor 架构各有什么优缺点？**

| 架构类型 | 优点 | 缺点 |
|---------|------|------|
| Network | 灵活性高，任何代理都可与其他代理通信 | 难以控制通信流程，扩展性差 |
| Supervisor | 中央控制，易于管理和监控 | 可能成为瓶颈，单点故障风险 |

&emsp;&emsp;**如何在实际生产环境中监控和调试多代理系统的行为？**

&emsp;&emsp;生产环境中的监控和调试是确保系统稳定运行的关键：
- **LangSmith集成**：利用LangChain的LangSmith进行全链路追踪
- **日志结构化**：结构化日志便于问题定位和分析
- **状态可视化**：将图结构可视化，便于理解执行流程
