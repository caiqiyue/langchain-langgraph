# 1. LangGraph底层原理介绍

&emsp;&emsp;`LangChain`发展至现在，仍然是构建大语言模型应用程序的前沿框架之一。特别是在最新发布的`v0.3`版本中，已经基本完成了由传统类到表达式语言(LCEL)的重要过渡，给开发者带来的直接利好就是**定义和执行分步操作序列（也称为链）会更加简单**。用更专业的术语来说，**使用`LangChain` 构建的是 DAG（有向无环图）**。而之所以会出现`LangGraph`框架，根本原因是在于随着AI应用（特别是AI Agent）的发展，**对于大语言模型的使用不仅仅是作为执行工具，而更多作为推理引擎的需求在日益增长**。这种转变带来的是更多的重复（循环）和复杂条件的交互需求，这就导致**基于`LCEL`的线性序列构建方式在构建更复杂、更智能的系统时显示出了明显的局限性。**如下所示的代码就是在`LangChain`中通过`LECL`表达式语言构建`Chain`的一种最简单的方式：

```python
# ! langchain==0.3.3 langchain-openai```

> LangChain ChatOpenAI：https://python.langchain.com/docs/integrations/chat/openai/

```python
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant that translates {input_language} to {output_language}."),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

chain.invoke(
    {
        "input_language": "English",
        "output_language": "Chinese",
        "input": "I love programming.",
    }
)```

&emsp;&emsp;反观`LangGraph`，顾名思义，`LangGraph` 在图这个概念上有很大的侧重，**它的出现就是`要解决线性序列的局限性问题，而解决的方法就是循环图`。**在`LangGraph`框架中，**用图取代了`LangChain`的`AgentExecutor`（代理执行器），用来管理代理的生命周期并在其状态内将暂存器作为消息进行跟踪，增加了以循环方式跨各种计算步骤协调多个链或参与者的功能。**这就与 `LangChain` 将代理视为可以附加工具和插入某些提示的对象不同，对于图来说，意味着**我们可以从任何可运行的功能或代理或链作为一个程序的起点。**

&emsp;&emsp;上面过于专业描述可能理解起来比较困难，所以这里我们通过一个简单直观的场景来详细解释。

&emsp;&emsp;在以图构建的框架中，**任何可执行的功能都可以作为对话、代理或程序的启动点**。这个启动点可以是大模型的 `API` 接口、基于大模型构建的 `AI Agent`，通过 `LangChain` 或其他技术建立的线性序列等等，即下图中的 "Start" 圆圈所示。无论哪种形式，它都首先处理用户的输入，并决定接下来要做什么。下图展示了在 `LangGraph` 概念下，最基本的一种代理模型：👇

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/1011002.png" width=50%></div>

&emsp;&emsp;**在启动点定义的可运行功能会根据收到的输入决定是否进行检索以及如何响应。**比如在执行过程中，如果需要检索信息，则可以利用搜索工具来实现，比如`Web Search`（网络搜索）、`Query Database`（查询数据库）、`RAG`等获取必要的信息（图中的 "Action" 圆圈）。接下来，再使用一个大语言模型（LLM）处理工具提供的信息，结合用户最初传入的初始查询，生成最终的响应（图中的 "LLMs" 圆圈）。最终，这个响应被传递至终点节点（图中的 "End" 圆圈）。

&emsp;&emsp;上图所示的流程就是在`LangGraph`概念中一个非常简单的代理构成形式。关键且必须清楚的概念是：在这里，**每个圆圈代表一个“节点”（Nodes），每个箭头表示一条“边”（Edges）。因此，在 `LangGraph` 中，无论代理的构建是简单还是复杂，它最终都是由节点和边通过特定的组合形成的图。这样的构建形式形成的工作流原理就是：当每个节点完成工作后，通过边告诉下一步该做什么，所以也就得出了：`LangGraph`的底层图算法就是在使用消息传递来定义通用程序。当节点完成其操作时，它会沿着一条或多条边向其他节点发送消息。然后，这些接收节点执行其功能，将结果消息传递给下一组节点，然后该过程继续。如此循环往复。**

&emsp;&emsp;**这就是`LangGraph`底层架构设计中图算法的根本思想。**

&emsp;&emsp;接下来，我们再看一个更现实的复杂例子。

&emsp;&emsp;在这个示例中，我们将`AI Agent`定义为应用程序的起点。**构建`AI Agent`代理通常涉及配置一个或多个工具**，否则构建它就没有太大的意义，因为如果仅仅是针对用户的问题直接做响应，即使问题很复杂，我们也可以直接通过提示词来引导大模型进行推理（参考`OpenAI`的 `o1`推理模型）。那么当`AI Agent`包含一些工具时，它是通过函数调用功能使用这些工具，而不是直接执行这些工具。所以当用户输入的原始问题经过`AI Agent`处理的时候，一般会出现以下两种情况：
1. 如果不需要调用任何工具，`AI Agent` 会直接提供一个针对用户问题的自然语言响应。例如：
   - 用户：你好，请你介绍一下你自己。
   - AI Agent：你好，我是一个人工智能助手，可以帮助你解决问题。
2. 如果需要调用工具，则输出将是一个特定格式的 JSON 输出，指示进行特定的函数调用。例如：
   - 输出示例：function': {'arguments': '{"query":"什么是快乐星球？"}','name': 'web_search'},'type': 'function'}

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/101103.png" width=60%></div>

&emsp;&emsp;经过第一个节点后（Agent），如果`AI Agent`认为需要调用某个函数，它会确定使用哪个工具以及传递哪些参数。假设有多个工具可选的情况下，`Action` 节点将呈现多条可能的路径供选择。如何选择呢？这时候，`LangGraph` 引入了一个**称为“条件边”的组件。条件边根据是否满足特定条件来决定走哪条路径，例如，代理可能需要决定是使用搜索工具还是直接生成最终答案。**为了管理这些决策，则使用了一个类似于 `if-else` 语句的结构，称为`Router`。基于`Router`的决策，代理可能会导向“搜索节点”以执行搜索操作并返回原始文本，或者直接前往“最终答案节点”以获取格式化后的自然语言响应。**如果选择了搜索路径，获取的答案文本还需通过另一个大语言模型进行处理，以生成用户可以理解的响应；若选择了直接回答，则可以使用一个专门的工具来格式化输出。**

&emsp;&emsp;在 `LangGraph` 框架中，`Router` 使用 `if..else` 的形式来决定路径，主要通过以下三种方式实现：
- 提示工程：指示大模型以特定格式做出回应。
- 输出解析器：使用后处理从大模型响应中提取结构化数据。
- 工具调用：利用大模型的内置工具调用功能来生成结构化输出。

&emsp;&emsp;更进一步地，我们现在知道了`LangGraph`通过组合`Nodes`和`Edges`去创建复杂的循环工作流程，通过消息传递的方式串联所有的节点形成一个通路。**那么维持消息能够及时的更新并向该去的地方传递，则依赖`langGraph`构建的`State`概念。** 在`LangGraph`构建的流程中，每次执行都会启动一个状态，图中的节点在处理时会传递和修改该状态。这个状态不仅仅是一组静态数据，而是由每个节点的输出动态更新，然后影响循环内的后续操作。如下所示：👇

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/101104.png" width=80%></div>

&emsp;&emsp;**此谓共享状态。**共享状态是指在执行期间在图内的节点之间传递的数据或信息**。 `LangGraph`允许节点在图上执行时时通过共享和更新此公共状态来进行交互。**这种共享状态使节点能够根据它们共同维护的数据进行通信、交换信息并影响彼此的行为。通过利用共享状态， `LangGraph`才能够促进节点间操作的协调和同步，允许动态交互和创建复杂的工作流程，其中节点可以协作并根据可用的共享信息做出决策。

&emsp;&emsp;从`LangGraph`官方的定义看，该框架是一个**用于使用大模型构建有状态、多参与者应用程序的库，可以创建代理和多代理工作流程**。而其官方自己总结的`LangGraph`的优势则是：

- **循环和分支**：在应用程序中实现循环和条件。
- **持久性**：在图中的每个步骤之后自动保存状态。随时暂停和恢复图形执行，以支持错误恢复、人机交互工作流程、时间旅行等。
- **人机交互**：中断图形执行以批准或编辑代理计划的下一个操作。
- **流支持**：流输出由每个节点生成（包括令牌流）。
- **与 LangChain 集成**：LangGraph 与LangChain和LangSmith无缝集成（但不需要它们）。

> LangGraph Github：https://github.com/langchain-ai/langgraph
>
> LangGraph Docs：https://langchain-ai.github.io/langgraph/

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241011112830097.png" width=80%></div>

&emsp;&emsp;至此，当我们了解了上述的原理后，再来看`LangGraph`官方的介绍，就能够比较清楚的理解其独特优势究竟体现在何处。
