# 3. 使用LangGraph构建大模型的问答流程

&emsp;&emsp;在上面的示例中，我们通过使用打印函数来初步了解`LangGraph`构建图的基本方法和机制。接下来，我们将探索如何将大模型集成至`LangGraph`框架中，从而构建一个更具实际应用价值的用于问答流程的图模式。

&emsp;&emsp;首先，`LangGraph`对目前主流的在线或者开源模型均支持接入，所以大家可以在该框架下非常便捷的应用到自己偏爱的大模型来进行问答流程的构建。这下面的示例中，我们选择比较方便且高效的`LangChain`框架，同时使用`OpenAI`的`GPT`模型来进行案例实现。而关于`LangChain`支持接入的模型列表及方式，大家可以在`LangChain Docs`中查阅：https://python.langchain.com/docs/integrations/chat/ 或者 https://python.langchain.com/docs/integrations/llms/ 。

&emsp;&emsp;这里仍然需要首先定义图模式，代码如下：

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from langgraph.graph import START, END

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 这两个 TypedDict 类型合并成一个更全面的字典类型。
class OverallState(InputState, OutputState):
    pass```

&emsp;&emsp;使用`OpenAI`的`GPT`模型需要使用到`ChatOpenAI`方法，我们需要将其定义到`Agent`节点中，用来接收用户输入的问题，调用`GPT`模型来根据用户的问题生成自然语言的回复响应。代码如下：

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")```

```python
def llm_node(state: InputState):
    messages = [
        ("system","你是一位乐于助人的智能小助理",),
        ("human", state["question"])
    ]
    
    llm = ChatOpenAI(model="gpt-4o",temperature=0,)

    response = llm.invoke(messages) 

    return {"answer": response.content}```

&emsp;&emsp;构建图，添加节点和边，并进行图结构的编译。完整代码如下所示：

```python
# 明确指定它的输入和输出数据的结构或模式
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("llm_node", llm_node)

# 添加便
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)

# 编译图
graph = builder.compile()```

&emsp;&emsp;进行测试：

```python
graph.invoke({"question":"你好，我用来测试"})```

```python
final_answer = graph.invoke({"question":"你好，我用来测试"})

print(final_answer["answer"])```

```python
final_answer = graph.invoke({"question":"你好，请你详细的介绍一下你自己"})

print(final_answer["answer"])```

&emsp;&emsp;更进一步地，如果想在原有的图结构中构建更复杂的功能，则只需要新定义一个`Python`函数，并按照自己的预期流程用边来建立连接，如下代码所示：

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict, Optional
from langgraph.graph import START, END

# 定义输入的模式
class InputState(TypedDict):
    question: str
    llm_answer: Optional[str]  # 表示 answer 可以是 str 类型，也可以是 None


# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 这两个 TypedDict 类型合并成一个更全面的字典类型。
class OverallState(InputState, OutputState):
    pass```

&emsp;&emsp;我们定义了一个`action_node`节点，用来接收`llm_node`的输出，将其翻译成中文，如下代码所示：

```python
def llm_node(state: InputState):
    messages = [
        ("system","你是一位乐于助人的智能小助理",),
        ("human", state["question"])
    ]
    
    llm = ChatOpenAI(model="gpt-4o",temperature=0,)

    response = llm.invoke(messages) 

    return {"llm_answer": response.content}

def action_node(state: InputState):
    messages = [
        ("system","无论你接收到什么语言的文本，请翻译成法语",),
        ("human", state["llm_answer"])
    ]
    
    llm = ChatOpenAI(model="gpt-4o",temperature=0,)

    response = llm.invoke(messages) 

    return {"answer": response.content}```

&emsp;&emsp;构建图，添加节点和边，并进行图结构的编译。

```python
# 明确指定它的输入和输出数据的结构或模式
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("llm_node", llm_node)
builder.add_node("action_node", action_node)

# 添加便
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "action_node")
builder.add_edge("action_node", END)

# 编译图
graph = builder.compile()```

```python
final_answer = graph.invoke({"question":"你好，请你详细的介绍一下你自己"})

print(final_answer["answer"])```

```python
final_answer = graph.invoke({"question":"请问什么是人工智能？"})

print(final_answer["answer"])```

&emsp;&emsp;当深入理解了`LangGraph`的底层原理及其图结构构建的逻辑后，我们是可以明显感受到其相较于`LangChain`中的`AI Agent`架构，展现出了更高的灵活性和扩展性。在`LangGraph`中，我们可以在各个`Python`函数中定义节点的核心逻辑，并通过边来确定输入与输出模式。此外，节点函数在定义时还可以自主构建中间状态的信息。尽管在本示例中我们使用`LangChain`来接入大模型，但通过节点函数的定义逻辑来看，我们当然也可以完全不依赖`LangChain`，而采用原生方法进行接入。

&emsp;&emsp;由此可见，正如课程开始阶段所提到的，**虽然`LangGraph`是基于`LangChain`的表达式语言构建的，但它完全可以脱离`LangChain`而独立运行**。总体来看，今天的示例并不复杂，但涉及的知识点和细节颇多。强烈建议大家亲自尝试和体验一下，打好扎实的基础，才能更好的开展接下来复杂循环图的学习。
