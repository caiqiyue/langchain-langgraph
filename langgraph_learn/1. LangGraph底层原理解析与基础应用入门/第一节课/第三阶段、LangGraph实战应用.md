## <center>第三阶段、LangGraph 实战应用</center>

&emsp;&emsp;当深入理解了 LangGraph 的底层原理及其图结构构建的逻辑后，我们可以明显感受到其相较于 LangChain 中的 `AI Agent` 架构，展现出了更高的灵活性和扩展性。接下来，我们将探索如何将大模型集成至 LangGraph 框架中，从而构建一个更具实际应用价值的用于问答流程的图模式。

### 1. 构建 LLM 问答系统

&emsp;&emsp;`LangGraph`对目前主流的在线或者开源模型均支持接入。下面的示例中，我们选择使用`LangChain`框架，同时使用`OpenAI`的`GPT`模型来进行案例实现。

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from langgraph.graph import START, END
from langchain_openai import ChatOpenAI

# 定义状态
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(InputState, OutputState):
    pass

# 定义 LLM 节点
def llm_node(state: InputState):
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)

    return {"answer": response.content}

# 构建图
builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("llm_node", llm_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)
graph = builder.compile()

# 测试
result = graph.invoke({"question": "你好，我用来测试"})
print(result["answer"])
```

### 2. 构建多节点翻译流程

&emsp;&emsp;如果想在原有的图结构中构建更复杂的功能，只需要新定义一个`Python`函数，并按照自己的预期流程用边来建立连接。

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict, Optional
from langgraph.graph import START, END
from langchain_openai import ChatOpenAI

class InputState(TypedDict):
    question: str
    llm_answer: Optional[str]  # 中间状态

class OutputState(TypedDict):
    answer: str

class OverallState(InputState, OutputState):
    pass

# 第一个节点：回答问题
def llm_node(state: InputState):
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
    ]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)
    return {"llm_answer": response.content}

# 第二个节点：翻译成法语
def translate_node(state: InputState):
    messages = [
        ("system", "无论你接收到什么语言的文本，请翻译成法语"),
        ("human", state["llm_answer"])
    ]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)
    return {"answer": response.content}

# 构建多节点图
builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("llm_node", llm_node)
builder.add_node("translate_node", translate_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "translate_node")
builder.add_edge("translate_node", END)
graph = builder.compile()

# 测试
result = graph.invoke({"question": "你好，请你详细的介绍一下你自己"})
print(result["answer"])
```

### 3. 实战流程图解

![LangGraph实战流程图](../assets/第三课_01_LangGraph实战流程图.html)

**图解说明**：LangGraph 多节点工作流 — START → LLM Node（生成回答）→ Translate Node（翻译）→ END

### 4. LangGraph 与 LangChain 的关系总结

| 对比项 | LangChain | LangGraph |
| ------ | ---------- | --------- |
| **架构** | DAG（有向无环图） | 带循环的图 |
| **状态管理** | 外部管理 | 内置 StateGraph |
| **适用场景** | 简单链式调用 | 复杂 Agent 工作流 |
| **循环支持** | 不支持 | 支持 |
| **灵活性** | 中等 | 高 |

&emsp;&emsp;**核心结论**：虽然`LangGraph`是基于`LangChain`的表达式语言构建的，但它完全可以脱离`LangChain`而独立运行。在 LangGraph 中，我们可以在各个 `Python` 函数中定义节点的核心逻辑，并通过边来确定输入与输出模式。

### 5. 拓展思考

#### 5.1 LangGraph 的设计哲学

&emsp;&emsp;LangGraph 的设计体现了几个核心思想：

1. **一切皆节点**：任何可执行的功能都可以作为对话、代理或程序的启动点
2. **边决定流程**：当每个节点完成工作后，通过边告诉下一步该做什么
3. **状态驱动**：共享状态使节点能够根据它们共同维护的数据进行通信和交互

#### 5.2 为什么选择 LangGraph 而不是 LangChain？

&emsp;&emsp;经过长时间的探索和实践会发现：
- 即使经过多轮的尝试和优化，使用 LangGraph 构建的 `AI Agent` 应用程序的效果也很难超过用 `Assistant API` 几行代码就能实现的效果
- 使用 LangGraph 意味着开发者需要进行较多的自主开发工作
- 但 LangGraph 的高度自主性和开放性让它在功能和灵活性上具有明显优势

&emsp;&emsp;**学习建议**：今天的示例并不复杂，但涉及的知识点和细节颇多。强烈建议大家亲自尝试和体验一下，打好扎实的基础，才能更好的开展接下来复杂循环图的学习。