&emsp;&emsp;继续深入探讨 `Multi-Agent`概念。`LangGraph`利用基于图的结构来定义代理并在它们之间建立连接。在此框架中，每个代理都表示为图中的一个节点，并通过边链接到其它代理。每个代理通过接收来自其他代理的输入并将控制权传递给下一个代理来执行其指定的操作。在`LangGraph` 框架的设计中，主要通过如下几种方法来建立各个子代理之间的通信连接：

- NetWork（网络）：每个代理都可以与其他每个代理通信。任何代理都可以决定接下来要呼叫哪个其他代理。
- Supervisor（主管）：每个代理都与一个 `Supervisor` 代理通信。由 `Supervisor` 代理决定接下来应调用哪个代理。
- Supervisor （tool-calling）： `Supervisor` 架构的一个特例。每个代理都是一个工具。由`Supervisor`代理通过工具调用的方式来决定调用哪些子代理执行任务，以及要传递给这些代理程序的参数
- Hierarchical（分层）：定义具有 `supervisor` 嵌套 `supervisor`多代理系统。这是 `Supervisor` 架构的一种泛化，允许更复杂的控制流。

&emsp;&emsp;各个多代理架构的通信方式如下图所示 👇 ：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411111115580.png" width=100%></div>

&emsp;&emsp;`LangGraph` 非常适合创建多代理工作流，因为它允许将两个或多个代理作为图连接。每个代理都是一个独立的参与者，代理之间的连接由边表示。每个连接边都可以有一个控制条件，用于将信息从一个代理中引导到另一个代理中，并且每个代理都有一个状态，可以在每个流期间使用信息进行更新。

&emsp;&emsp;但是，在具体实践各个不同多代理架构下的具体应用方法之前，我们需要结合`LangGraph`构建图的机制去思考一个问题：**通过`State`可以让一个图中的所有节点共享全局的信息，那么在多代理架构中，当每一个图变成了一个节点，那么不同图之间的状态，应该怎么传递？**

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411131500079.png" width=60%></div>

&emsp;&emsp;在上图所示的架构中，每个子代理（例如Agent 1、Agent 2、Agent 3）由多个内部节点组成，各自通过独立的`State`维护内部节点间的消息传递。举个例子，假设`Agent 1`是一个数据分析师，负责接收并整理关键数据；`Agent 2`则负责进行精细化的计算。在这个过程中，如何有效地在`Agent 1`和`Agent 2`之间传递数据成为了一个关键问题。`Agent 1`需要将数据传递给`Agent 2`进行处理，之后`Agent 2`需要将计算结果返回给`Agent 1`。但是当前的涉及是不支持在代理间传递状态的，即在`Agent 2`的执行过程中无法访问`Agent 1`中的状态。

&emsp;&emsp;因此，如果想让不同`Agent`之间能够做到消息共享，则需要了解 `LangGraph`框架中的`Subgraphs`（子图）相关的概念和使用方法。
