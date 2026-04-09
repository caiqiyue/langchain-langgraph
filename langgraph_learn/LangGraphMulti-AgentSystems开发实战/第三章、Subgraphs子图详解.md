# 3. Subgraphs

&emsp;&emsp;`Subgraphs`（子图）指的是能够用作另一个图中的节点的图。**简单理解就是：把一个已经编译好的图，嵌入到另一个已经编译好的图中，并且两个独立图的中的状态可以信息共享**。一个典型的应用就是构建多代理系统架构。它所做的事情是：当把每个独立的`Agent`图结构定义为一个子图时，只要遵守子图的接口（输入和输出模式）规范，那么子图中定义的共享状态就可以在父图中进行使用。如下图所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131619712.png" width=60%></div>

&emsp;&emsp;添加子图主要解决的问题就是解决各`Single-Agent`之间的通信问题，即它们如何在图执行期间在彼此之间传递状态。这主要有两种情况：
- **父、子图的状态模式中有共同的键（通道）。**
- **父、子图的状态模式中没有共同的键。（通道）**

&emsp;&emsp;如何理解这两种情况？我们就分别用实际的案例来帮助大家理解这个过程。首先来看第一种情况：**如果父、子图节点中定义的状态模式有共同的键，比如下述情况所示**：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131857901.png" width=100%></div>

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

# llm = ChatOpenAI(model="gpt-4o-mini")```

&emsp;&emsp;而如何想要使用本地部署的开源大模型，可以用`LangChain`进行高效的接入。如下代码所示，我们使用`langChain`的`ChatOllama`第三方的集成方法接入本地启动的`Qwen-2.5:72B`模型。

&emsp;&emsp;注意：在执行如下代码之前，需要在本地/云服务器上使用`Ollama`部署并启动对应的模型，如下所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411151319498.png" width=100%></div>

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411151334219.png" width=100%></div>

> 关于如何使用`Ollama`启动大模型的详细教程，请查看《开源大模型模块-【Qwen2.5】Qwen2.5介绍与部署流程》课件

```python
# ! pip install  langchain-ollama```

```python
# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)```

&emsp;&emsp;测试一下 `qwen2.5:72b` 模型的连通性，代码如下：

```python
print(llm.invoke("你好，请你介绍一下你自己。").content)```

- **Step 2. 定义父图的状态模式**

&emsp;&emsp;父图的作用是接收来自用户的输入，这些输入可能是问题、请求或任何形式的查询，使用大模型处理用户输入，生成一个详细的响应。所以涉及两个状态键：用户的输入和大模型针对用户输入的响应。因此定义如下：

```python
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应```

- **Step 3. 定义父图的节点逻辑**

&emsp;&emsp;节点的功能就是使用大模型处理用户输入，并生成响应。

```python
def parent_node(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}```

- **Step 4. 定义子图的状态模式**

&emsp;&emsp;对于子图来说，父图生成的响应会传递到子图，子图的第一个节点负责将这个响应缩减为一个简洁的总结。然后在子图的第二个节点，对完整的响应及其总结进行评分。因此涉及的状态模式就如下图所示：

```python
# 定义子图中的状态
class SubgraphState(TypedDict):
    # 这个 key 是和 父图（ParentState）共享的，
    final_answer: str 
    # 这个key 是 子图 (subgraph) 中独享的
    summary_answer:str```

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
    return {"summary_answer": response}```

```python
def subgraph_node_2(state: SubgraphState):
    # final_answer 仅能在 子图中使用
    messages = f"""
    This is the full content of what you received：{state["final_answer"]} \n
    This information is summarized for the full content:{state["summary_answer"]} 
    Please rate the text and summary information, returning a scale of 1 to 10. Note: Only the score value needs to be returned.
    """
  
    response = llm.invoke([HumanMessage(content=messages)])

    # 发送共享状态密钥（'user_input'）的更新
    return {"final_answer": response.content}```

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
subgraph = subgraph_builder.compile()```

- **Step 7. 定义父图的图结构，并将子图作为节点添加至父图**

```python
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node)

# 将编译后的子图作为一个节点添加到父图中
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()```

- **Step 8. 可视化完整的图结构**

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

```python
async for chunk in graph.astream({"user_input": "我现在想学习大模型，应该关注哪些技术？"}, stream_mode='values'):
    print(chunk)```

&emsp;&emsp;当一个图中添加了子图，按照常规的调用方法可以看到父图的最终输出包括子图调用的结果（即字符串 “final_answer”）。如果想进一步查看子图的输出，可以在流式传输时指定 `subgraphs=True`。如下代码所示：

```python
async for chunk in graph.astream({"user_input": "如何理解RAG？"}, stream_mode='values', subgraphs=True):
    print(chunk)```

&emsp;&emsp;这个案例实现的工作流就让父图和子图借助共享的状态键（通道）进行通信，这是非常常见的一种多代理架构的底层构建模式，这种通信模式要关注的点就是如何设计自己的工作流以通过父图的全局状态键进行各个子图（子代理）的有效交互和信息传递。

&emsp;&emsp;**接下来我们看第二种情况：父、子图节点中定义的状态模式没有共同的键的时候，怎么做**？这种情况如下图所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131909694.png" width=100%></div>

&emsp;&emsp;如果父图与子图是完全不同的架构，则会出现上图中无共同键可用的情况。在这种情况下如果仍然想让父图与子图之间能够以某种方式进行通信，则需要定义一个调用子图的 `node` 函数，其作用是：**在调用子图之前将输入（父）状态转换为子图状态，并在从节点返回状态更新之前将结果转换回父状态。** 我们来看下面这个案例：

```python
# import getpass
# import os
# from langchain_openai import ChatOpenAI

# if not os.environ.get("OPENAI_API_KEY"):
#     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# llm = ChatOpenAI(model="gpt-4o-mini")

# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)```

&emsp;&emsp;父图的状态和节点的逻辑均布发生变化，如下所示：

```python
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应

def parent_node_1(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}```

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
    return {"score": response.content}```

&emsp;&emsp;正常定义子图并编译。

```python
subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()```

&emsp;&emsp;接下来的j这个函数是关键。**`parent_node_2`用来连接父图与子图之间的网络通信，它通过将父节点与子节点的状态做转化来达到此目的**。代码如下：

```python
def parent_node_2(state: ParentState):
    # 将父图中的状态转换为子图状态
    response = subgraph.invoke({"response_answer": state["final_answer"]})
    # 将子图状态再转换回父状态
    return {"final_answer": response["score"]}```

```python
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node_1)

# 注意，我们使用的不是编译后的子图，而是调用子图的‘ node_2 ’函数
builder.add_node("node_2", parent_node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

```python
async for chunk in graph.astream({"user_input": "我现在想学习大模型，应该关注哪些技术？"}, stream_mode='values'):
    print(chunk)```

```python
all_chunk = []

async for chunk in graph.astream({"user_input": "什么是机器学习？"}, stream_mode='values', subgraphs=True):
    all_chunk.append(chunk)```

```python
all_chunk[-1][1]["final_answer"]```

&emsp;&emsp;在上面的案例中，`subgraph state` 完全独立于父 `graph state`，即两者之间没有重叠的键（通道）是最常见的，也是灵活性最高的。其中的关键点在于：**需要在调用子图之前将其输入转换为子图，然后在返回之前转换其输出**，即可正常完成父、子图之间的通信。

&emsp;&emsp;在`LangGraph`中，子图的应用主要用于多代理系统的构建，而如果理解了上面两个案例中通信状态的传递方式，就基本具备了构建多代理系统的必要条件。接下来，我们就针对`LangGraph`框架下的不同多代理架构依次展开详细的探讨和实践。
