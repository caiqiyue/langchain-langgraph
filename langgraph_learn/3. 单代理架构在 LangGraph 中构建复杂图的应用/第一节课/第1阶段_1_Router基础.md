## <center>第1阶段、Router Agent与条件路由</center>

### 1. LangGraph中的Router使用场景

&nbsp;&nbsp;&nbsp;&nbsp;在`LangGraph`中，我们可以利用"条件边"这一概念来指导或约束大模型在处理特定任务时的逻辑流程。这种机制允许大模型在达到某一环节并满足预设条件时，根据不同的条件输出或数据，选择性地执行不同的逻辑路径。

&nbsp;&nbsp;&nbsp;&nbsp;为了管理这样复杂的图结构，`LangGraph`使用的是一个类似于 `if-else`语句的结构组件，称为`Router`（路由）。这个组件允许大模型从一组预设的选项中选择合适的步骤来进行执行。

&nbsp;&nbsp;&nbsp;&nbsp;对于简单的直接从节点`A`到节点`B`，我们一直使用的是`add_edge`方法。如果想选择性地路由到 1 个或多个边，则需要使用`add_conditional_edges`方法。

&nbsp;&nbsp;&nbsp;&nbsp;`add_conditional_edges`的关键参数是`path`参数，它指的是一个函数调用对象。这个对象接受图的当前`state`并返回一个值，根据返回值的不同，来决定路由到哪个节点。

### 2. 拓展思考

&nbsp;&nbsp;&nbsp;&nbsp;Router Agent的优势是可以精准的控制程序链路中的每一个细节，但同时也表现出来了这是一种相对有限的控制级别的代理架构。当我们需要更复杂的自主决策时，需要引入下一节介绍的 Tool Calling Agent。

![Router Agent 架构图](./assets/router_agent_chart.html)

**图解说明**：Router Agent 条件路由流程图