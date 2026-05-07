## <center>第一阶段、LangGraph中ReAct的构建原理</center>

### 1. 从Router Agent到Full Autonmonous Agent

&emsp;&emsp;上节课介绍的 `Router Agent` 和 `Tool Calling Agent`，我们通过两个实际的案例证明了**随着任务需求的复杂性增加，代理架构中对中间流程的控制自由度也必须相应提高。**

&emsp;&emsp;`Tool Calling Agent` 的局限性在于：虽然它可以自主选择工具，但在其架构中，每次仅能执行一次函数调用。因此，当任务需要依次执行 A 工具、B 工具和 C 工具时，它无法支持这种自主控制的过程。

&emsp;&emsp;`Full Autonmonous`（自治循环代理）以两种主要的方式去扩展了`Agent`对工作流的控制：
- **多步骤决策**：Agent可以控制一系列决策，而不仅仅是一个决策。
- **工具访问**：Agent可以选择并使用多种工具来完成任务。

### 2. ReAct思想与自治循环代理

&emsp;&emsp;满足上述两个条件，典型且通用的代理架构，就是基于`ReAct`思想而形成的代理模式。

&emsp;&emsp;**ReAct的核心在于：为大模型配备足够丰富的外部工具，使用合适的提示词，引导大模型在接收到用户输入后，进入自主思考和循环执行的状态，以实现最终目标。**

### 3. LangGraph中ReAct的构建原理

&emsp;&emsp;在 `LangGraph` 开发框架中，预构建的`ReAct`组件，其实就是通过接入大模型，搭配着`Tool Calling Agent`，再结合`Router Agent` 共同构建起来的图。

&emsp;&emsp;**其核心过程是：大模型可以在一个 `while` 循环中被重复调用。每一步，代理来自主决定调用哪些工具及其输入，然后执行这些工具，并将输出作为观察结果反馈给大模型。当代理判断不再需要调用更多工具时，`while` 循环便会终止，输出最终的结果。**

#### 3.1 ReAct Agent的内部机制

&emsp;&emsp;ReAct Agent架构支持：
- **Tool calling**：允许大模型根据需要选择和使用各种工具。
- **Memory**：使代理能够保留和使用先前步骤中的信息。
- **Planning**：授权大模型制定并遵循多步骤计划以实现目标。

#### 3.2 图结构中的工作流

&emsp;&emsp;在图结构中，`Agent`节点使用消息列表的形式来调用大语言模型，`Messages Modifier`指的是在传递到大模型之前，修饰用户的原始输入内容。

&emsp;&emsp;如果生成的 `AIMessage` 包含`tool_calls`，则该图将调用 `tools`。`tools` 节点执行工具（每个 `tool_call` 1 个工具）并且将响应作为`ToolMessage`对象添加到消息列表。然后`Agent`节点再次调用大语言模型。

&emsp;&emsp;重复该过程，直到响应中不再存在`tool_calls` ，最终由`Agent`节点将完整的消息列表作为包含键 `messages`的字典返回。

### 4. create_react_agent接口

&emsp;&emsp;整个过程已经由`LangGraph`内部封装好了，其提供给开发者使用的接口就是：`create_react_agent`方法。

```python
from langgraph.prebuilt import create_react_agent

# 创建ReAct代理
graph = create_react_agent(llm, tools=tools)
```

&emsp;&emsp;必要的参数：
- **model**：支持工具调用的LangChain聊天模型
- **tools**：工具列表、ToolExecutor 或 ToolNode 实例
- **state_schema**：图的状态模式（可选）

### 5. 拓展思考

#### 5.1 ReAct与Tool Calling Agent的本质区别

&emsp;&emsp;ReAct Agent与Tool Calling Agent的核心区别在于循环机制。Tool Calling Agent在一次工具调用后即结束，而ReAct Agent会持续循环，直到大模型判断不再需要调用工具为止。

&emsp;&emsp;这种设计使得ReAct能够处理复杂的多步骤任务，例如：
1. 先搜索相关信息
2. 基于搜索结果查询数据库
3. 综合所有信息生成最终答案

#### 5.2 预构建组件的优势

&emsp;&emsp;使用`create_react_agent`预构建方法的优势：
1. **开发效率高**：一行代码即可创建完整的自治代理
2. **可维护性好**：底层逻辑由LangGraph维护
3. **扩展性强**：只需添加新工具即可扩展功能
4. **可追踪性强**：与LangSmith集成，支持完整的执行追踪