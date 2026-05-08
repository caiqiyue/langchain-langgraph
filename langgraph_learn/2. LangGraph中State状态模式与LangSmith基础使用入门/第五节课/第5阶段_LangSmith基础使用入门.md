## <center>第5阶段、LangSmith基础使用入门</center>

### 1. LangSmith概述

&emsp;&emsp;大模型具有不确定性，尤其是构建复杂AI Agent应用程序中，中间会涉及非常多的子步骤，如果想要了解每一步的运行状态和结果，一方面可以通过Debug来进行实时控制，而另一方面可以借助一些工具来观察和调试中间的交互流程。

&emsp;&emsp;LangSmith是由LangChain和LangGraph背后的团队创建的工具平台，**主要作用是：为基于大语言模型构建的应用程序提供全面的监控、调试和可观察性。提供强大的跟踪、日志记录和实时分析功能。**

### 2. LangSmith核心概念

&emsp;&emsp;**Project (项目)**：蓝色方块代表整个项目，可能是一个单独的应用程序或服务。

&emsp;&emsp;**Traces (轨迹)**：绿色方块代表项目在不同条件或配置下的执行路径。每个轨迹可以是一个特定的用户会话、一个功能的执行，或者应用在特定输入下的行为。

&emsp;&emsp;**Runs (运行)**：每个轨迹下的黄色方块表示特定轨迹的单次执行。这些是执行的实例，每个实例都是轨迹在特定条件下的实际运行。

&emsp;&emsp;**Feedback, Tags, Metadata (反馈、标签、元数据)**：这部分显示了系统如何利用用户或自动化工具生成的反馈、标签和元数据来增强轨迹的管理和过滤。

### 3. LangSmith配置步骤

#### 3.1 创建LangSmith账户

&emsp;&emsp;要开始使用LangSmith，需要创建一个帐户。可以在这里注册一个免费帐户进入LangSmith登录页面：https://smith.langchain.com/，支持使用Google、GitHub、Discord和电子邮件登录。

#### 3.2 创建API密钥

&emsp;&emsp;注册并登录后，单击LangSmith仪表板左侧菜单中的"设置"图标，导航至"API密钥"部分，然后单击"创建API密钥"。

&emsp;&emsp;LangSmith支持两种类型的API密钥：服务密钥和个人访问令牌。这里选择"密钥类型令牌的个人访问"，因为我们将使用此密钥作为用户进行个人访问。

#### 3.3 创建环境变量

&emsp;&emsp;将LANGCHAIN_API_KEY替换为刚创建的API密钥：
```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key-here"
```

### 4. 集成到LangGraph应用

&emsp;&emsp;在环境变量中设置以后，代码不需要做任何改变，即可构建LangSmith的消息跟踪。

&emsp;&emsp;**代码示例**：
```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
```

### 5. 拓展思考

#### 5.1 深度概念

&emsp;&emsp;**LangSmith的价值**：

&emsp;&emsp;跟踪是请求通过图逻辑的步骤的详细记录。将其视为显示从开始到结束的确切顺序的路线图。在当前的设置中，LangGraph很简单：
- 它以__start__节点开始
- 穿过AI生成回复的response节点
- 结束于__end__节点

&emsp;&emsp;每次用户与程序进行交互时，该图都会展开，并且此过程中的每个步骤都会记录为跟踪的一部分。借助LangSmith，可以实时可视化和分析这些痕迹。

#### 5.2 实践建议

&emsp;&emsp;在初次构建AI应用程序时，建议从最简单的工作流实现开始，结合LangSmith这样的评估工具是能够极大程度上帮助理解其中间过程。而随着构建应用程序的越来越复杂，其中间状态也会变得越来越多。在接下来的课程中，会随着新功能点的讲解，再展开对LangSmith使用方法和各项指标的具体说明。