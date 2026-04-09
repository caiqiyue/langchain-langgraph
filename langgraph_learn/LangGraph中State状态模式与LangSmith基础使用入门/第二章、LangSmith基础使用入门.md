&emsp;&emsp;大模型具有不确定性，尤其是构建复杂`AI Agent`应用程序中，中间会涉及非常多的子步骤，如果想要了解每一步的运行状态和结果，一方面可以通过`Debug`来进行实时控制，而另一方面可以借助一些工具来观察和调试中间的交互流程。`Langsmith`就是这样一个工具平台， 由​​ `LangChain` 和 `LangGraph` 背后的团队创建，**主要作用是：为基于大语言模型构建的应用程序提供全面的监控、调试和可观察性。提供强大的跟踪、日志记录和实时分析功能。**


> LangSmith：https://smith.langchain.com/

&emsp;&emsp;通常，对于一个项目而言，可以是单个应用程序或服务。该项目将包含多个跟踪，每个跟踪都是运行的集合 - 一个运行代表应用程序中的一个基本操作，例如对 OpenAI 的 API 调用，或检索操作。如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022164041124.png" width=100%></div>

- **Project (项目)：**蓝色方块代表整个项目，可能是一个单独的应用程序或服务。
- **Traces (轨迹)：**绿色方块代表项目在不同条件或配置下的执行路径。每个轨迹可以是一个特定的用户会话、一个功能的执行，或者应用在特定输入下的行为。
- **Runs (运行)：**每个轨迹下的黄色方块表示特定轨迹的单次执行。这些是执行的实例，每个实例都是轨迹在特定条件下的实际运行。
- **Feedback, Tags, Metadata (反馈、标签、元数据)：**这部分显示了系统如何利用用户或自动化工具生成的反馈、标签和元数据来增强轨迹的管理和过滤。反馈可以用于改进未来的运行，标签和元数据可用于分类和筛选特定的轨迹或运行，以便在LangSmith的用户界面中更容易地管理和审查

&emsp;&emsp;我们使用当前的简单 `LangGraph` 作为示例：

```python
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;跟踪是请求通过图逻辑的步骤的详细记录。将其视为显示从开始到结束的确切顺序的路线图，在当前的设置中，`LangGraph` 很简单：
- 它以__start__节点开始
- 穿过 AI 生成回复的response节点
- 结束于__end__节点。

&emsp;&emsp;每次用户与程序进行交互时，该图都会展开，并且此过程中的每个步骤都会记录为跟踪的一部分。借助 `Langsmith`，我们可以实时可视化和分析这些痕迹。设置 `Langsmith`并不复杂，我们需要依次执行如下操作步骤。

- **Step 1. 创建一个 LangSmith 帐户**

&emsp;&emsp;要开始使用 `LangSmith`，我们需要创建一个帐户。可以在这里注册一个免费帐户进入`LangSmith`登录页面： https://smith.langchain.com/， 支持使用 Google、GitHub、Discord 和电子邮件登录。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165215709.png" width=100%></div>

&emsp;&emsp;注册并等登录后，可以直接查看到仪表板：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165247933.png" width=100%></div>

&emsp;&emsp;在构建程序跟踪前，首先需要创建一个 `API` 密钥，该密钥将允许我们的项目开始向 `Langsmith` 发送跟踪数据。

- **Step 2. 创建 API 密钥**

&emsp;&emsp;单击 `Langsmith` 仪表板左侧菜单中的“设置”图标。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165343038.png" width=100%></div>

&emsp;&emsp;导航至“API 密钥”部分，然后单击“创建 API 密钥” 。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165421182.png" width=100%></div>

&emsp;&emsp;`LangSmith` 支持两种类型的 API 密钥：服务密钥和个人访问令牌。两种类型的令牌都可用于验证对 `LangSmith API` 的请求，但它们有不同的用例。这里选择“密钥类型令牌的个人访问” ，因为我们将使用此密钥作为用户进行个人访问。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165455845.png" width=100%></div>

&emsp;&emsp;单击“创建 API 密钥” ，复制并确认已保存。这和`OpenAI`的`API`密钥一样，一旦创建完成，则不允许再次复制。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165542782.png" width=100%></div>

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165638427.png" width=100%></div>

&emsp;&emsp;现在，就可以将其集成到我们的项目中了。

- **Step 3. 创建环境变量**

&emsp;&emsp;将`LANGCHAIN_API_KEY`替换为我们刚刚创建的 `API` 密钥。

```python
import os

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "REDACTED_TOKEN"

# 验证环境变量是否设置成功
print(os.getenv("LANGCHAIN_TRACING_V2"))
print(os.getenv("LANGCHAIN_API_KEY"))```

&emsp;&emsp;在环境变量中设置以后，我们的代码不需要做任何的改变，即可构建`LangSmith`的消息跟踪。

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


llm = ChatOpenAI(model="gpt-4o")

def chatbot(state: State):
    # print(state)
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()```

```python
def stream_graph_updates(user_input: str):  
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("模型回复:", value["messages"][-1].content)


while True:
    try:
        user_input = input("用户提问: ")
        if user_input.lower() in ["退出"]:
            print("下次再见！")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available  
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break```

&emsp;&emsp;然后即可在控制面板上实时查看到该应用程序执行过程中各个状态的输入和输出情况。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241023151932199.png" width=100%></div>

&emsp;&emsp;至此，大家已经可以运行起`LangSmith`应用工具。在初次构建AI应用程序时，建议从最简单的工作流实现开始，结合 `LangSmith` 这样的评估工具是能够极大程度上帮助大家理解其中间过程。而随着构建应用程序的越来越复杂，其中间状态也会变得越来越多。在接下来的课程中，我们会随着新功能点的讲解，再展开对`LangSmith`使用方法和各项指标的具体说明。
