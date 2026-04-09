&emsp;&emsp;在 `LangGraph` 开发框架中有一些预构建的组件。上节课介绍的 `ToolNode` 是其中一个，它用于处理外部函数调用，其内部结合了 `LangGraph` 底层的图结构，能够接收 `JSON Schema` 形式的数据，执行工具函数并返回结果。除此之外，`LangGraph`的预构建组件中还包含了 `ReAct` 代理架构，该架构与我们在《Ch.3 ReAct Agent 基本理论与项目实战》中手动实现的思路和流程基本一致。不同之处在于，**在 `LangGraph` 框架中，`ReAct` 组件被改造成适配图结构的循环代理，其具体过程是：大模型可以在一个 `while` 循环中被重复调用。每一步，代理来自主决定调用哪些工具及其输入，然后执行这些工具，并将输出作为观察结果反馈给大模型。当代理判断不再需要调用更多工具时，`while` 循环便会终止，输出最终的结果。**

&emsp;&emsp;**因此，我们需要理解的关键概念是：`LangGraph`预构建的`ReAct`组件，其实就是通过接入大模型，搭配着`Tool Calling Agent`，再结合`Router Agent` 共同构建起来的图，这个图以自治循环代理的架构形式提供服务。**其图结构如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/20241029002.png" width=80%></div>

&emsp;&emsp;如上图所示的代理架构在 `LangGraph` 中的实现机制类似于 `LangChain` 中的 `ReAct Agent`，毕竟 `LangGraph` 的底层语言是 `LangChain` 的 `LCEL` 表达式语言。因此，该 `ReAct Agent` 架构是从 `LangChain` 已实现的 `ReAct Agent` 迁移而来，不同的是在`LangGraph`框架中适配的是图结构，而非`AgentExecuter`。其本质依然基于一种规划（Planning）的思想：

> LangChain Agents Type： https://python.langchain.com/v0.1/docs/modules/agents/agent_types/
>
> Agent Planning：https://smith.langchain.com/hub/hwchase17/react?organizationId=33612d73-91c5-5140-b8a0-f3155ff5dc45

```json
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer

Final Answer: the final answer to the original input question

Begin!

Question: {input}

Thought:{agent_scratchpad}
```

&emsp;&emsp;这种代理实现的机制表明了，在`LangGraph`中实现的预构建`ReAct`代理结构，它支持：

- **Tool calling ：允许大模型根据需要选择和使用各种工具。**
- **Memory：使代理能够保留和使用先前步骤中的信息。**
- **Planning ：授权大模型制定并遵循多步骤计划以实现目标。**


&emsp;&emsp;而其在图结构中的具体构建的工作流如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241028180303239.png" width=80%></div>

&emsp;&emsp;如图所示，`Agent`节点使用消息列表的形式来调用大语言模型，`Messages Modifier`指的是在传递到大模型之前，修饰用户的原始输入内容，可以是`SystemMessage`（作为背景信息添加的消息列表的开头）、`Runnable`（可运行）等不同状态，如果生成的 `AIMessage` 包含`tool_calls`，则该图将调用 `tools` 。 `tools` 节点执行工具（每个 `tool_call` 1 个工具）并且将响应作为`ToolMessage`对象添加到消息列表。然后`Agent`节点再次调用大语言模型。重复该过程，直到响应中不再存在`tool_calls` ，最终由`Agent`节点将完整的消息列表作为包含键 `messages`的字典返回。

&emsp;&emsp;那么如何实现上述这个非常复杂的过程呢？非常简单，既然我们一直提到的是预构建组件，则说明整个过程已经由`LangGraph`内部封装好了，其提供给开发者使用的接口就是：`create_react_agent`方法。

> LangGraph create_react_agent：[点击查看源码参数介绍](https://langchain-ai.github.io/langgraph/reference/prebuilt/?h=create+react+agent#langgraph.prebuilt.chat_agent_executor.create_react_agent)
