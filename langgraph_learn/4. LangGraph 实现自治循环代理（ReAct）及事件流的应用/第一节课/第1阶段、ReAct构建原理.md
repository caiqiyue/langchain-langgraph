## <center>第1阶段、ReAct构建原理</center>

### 1. LangGraph 与 ReAct 的关系

&emsp;&emsp;LangGraph 是 LangChain 生态中的图结构扩展，它在底层图结构上封装了预置的 ReAct Agent 结构，提供 `create_react_agent` 方法，可以快速创建基于 ReAct 循环的 Agent。

&emsp;&emsp;ReAct（Reasoning + Acting）是一种结合推理和行动的 Agent 模式，核心思想是让 Agent 在执行任务时进行多轮推理和行动，直到完成任务。

### 2. ReAct Agent 的底层实现

&emsp;&emsp;从底层原理看，LangGraph 预置的 ReAct Agent 结构包含以下核心组件：

- **StateGraph**: 图的状态管理，通过 `messages` 列表记录对话历史
- **Agent Node**: 模型调用节点，负责调用 LLM 生成响应
- **Tools Node**: 工具执行节点，执行 Agent 调用的外部工具
- **Router Function**: 路由函数，根据节点执行结果决定下一步路径

### 3. Tool Calling 模式与 ReAct 模式的区别

&emsp;&emsp;LangGraph 支持两种预置 Agent 结构：

&emsp;&emsp;**Tool Calling 模式**：模型直接决定调用哪个工具，工具选择是确定性的，适用于工具数量较少、场景明确的场景。

&emsp;&emsp;**ReAct 模式**：模型先推理再决定行动，支持更复杂的决策流程，适用于需要多步推理的复杂场景。

### 4. 拓展思考

&emsp;&emsp;思考：ReAct 模式的「推理-行动」循环与传统的「规划-执行」模式有何区别？在什么场景下应该选择 ReAct 模式而非简单的 Tool Calling 模式？

&emsp;&emsp;提示：考虑任务复杂度、工具数量、决策确定性等因素。

![ReAct 构建原理图](./assets/第四课_01_ReAct构建原理图.html)

**图解说明**：ReAct Agent 推理-行动循环原理图