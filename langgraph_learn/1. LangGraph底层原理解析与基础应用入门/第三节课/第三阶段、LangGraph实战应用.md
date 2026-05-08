## <center>第三阶段、LangGraph实战应用</center>

### 1. 构建LLM问答流程

&emsp;&emsp;在`LangGraph`框架中，将大模型集成到问答流程是一个常见的应用场景。`LangGraph`对目前主流的在线或者开源模型均支持接入，所以大家可以在该框架下非常便捷的应用到自己偏爱的大模型来进行问答流程的构建。

&emsp;&emsp;首先需要定义图的模式，然后使用`ChatOpenAI`方法定义`Agent`节点，用来接收用户输入的问题，调用大模型来根据用户的问题生成自然语言的回复响应。

#### 1.1 定义状态模式

```python
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(InputState, OutputState):
    pass
```

#### 1.2 定义LLM节点

```python
def llm_node(state: InputState):
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
    ]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)
    return {"answer": response.content}
```

### 2. 构建多节点工作流

&emsp;&emsp;当深入理解了`LangGraph`的底层原理及其图结构构建的逻辑后，我们是可以明显感受到其相较于`LangChain`中的`AI Agent`架构，展现出了更高的灵活性和扩展性。

&emsp;&emsp;在`LangGraph`中，我们可以在各个`Python`函数中定义节点的核心逻辑，并通过边来确定输入与输出模式。此外，节点函数在定义时还可以自主构建中间状态的信息。

### 3. LangGraph的灵活性

&emsp;&emsp;尽管在本示例中我们使用`LangChain`来接入大模型，但通过节点函数的定义逻辑来看，我们当然也可以完全不依赖`LangChain`，而采用原生方法进行接入。

&emsp;&emsp;由此可见，**虽然`LangGraph`是基于`LangChain`的表达式语言构建的，但它完全可以脱离`LangChain`而独立运行**。

&emsp;&emsp;总体来看，今天的示例并不复杂，但涉及的知识点和细节颇多。强烈建议大家亲自尝试和体验一下，打好扎实的基础，才能更好的开展接下来复杂循环图的学习。

### 4. 拓展思考

#### 4.1 与Assistant API的对比

&emsp;&emsp;`LangGraph`是一个适用范围更广的`AI Agent`开发框架。在**大模型的支持方面**，`LangGraph`不仅支持`GPT`系列，还兼容其他多种在线或开源模型，例如 `glm4`、`llama3`和`Qwen`等。在**大模型的接入方式**上，我们既可以通过传统的`openai api`等原生方式将大模型集成到`LangGraph`构建的`AI Agent`流程中，也可以利用`ollma`、`vllm`等大模型推理加速库。

#### 4.2 LangGraph的优势总结

- **高度自主性和开放性**：功能和灵活性上相较于`Assistant API`具有明显的优势
- **支持循环和分支**：在应用程序中实现循环和条件
- **持久性**：在图中的每个步骤之后自动保存状态，支持错误恢复、人机交互工作流程
- **人机交互**：中断图形执行以批准或编辑代理计划的下一个操作
- **流支持**：流输出由每个节点生成（包括令牌流）
- **与 LangChain 集成**：LangGraph 与LangChain和LangSmith无缝集成

> LangChain Docs：https://python.langchain.com/docs/integrations/chat/ 或 https://python.langchain.com/docs/integrations/llms/
