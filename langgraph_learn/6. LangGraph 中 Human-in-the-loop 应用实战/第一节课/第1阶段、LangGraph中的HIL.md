## <center>第1阶段、LangGraph中的HIL</center>

# 1. LangGraph中的HIL

&emsp;&emsp;`LangGraph`底层是通过图结构来进行构建，并由状态做消息的传递，那么对于这样的结构来说，如果我们想在这样的架构中加入人工的介入流程，能操作的大致思路应该是：通过`Router Agent`去做判断，如果生成的响应触发了某种条件，就在原本要正常进入的节点之前先停止，等待人工的确认，再决定要不要执行，或者执行什么逻辑。在这个过程中，有几种常见的用户交互模式，分别是： - **批准（Approval）**：在代理的执行过程中，人工暂停代理的自主工作流，向用户展示当前的状态，并批准或者不批准执行该操作。 - **编辑（Editing）**：在需要的时候，人工可以暂停代理，向用户展示当前的状态，并允许用户对代理的状态进行编辑。 - **输入（Input）**：专门设计一个图节点来收集用户的输入，并将这些输入直接用于更新代理的状态。 &emsp;&emsp;在`LangGraph`的设计思路下**，`HIL`通过战略性地放置断点（`breakpoint`）来实现的。这些断点会在关键点停止图的执行。在暂停期间，`Agent`将等待用户输入，利用这段时间收集响应，将它们集成到图状态中，并顺利继续进行，从而实现用户和代理之间的协作和交互式体验**。这个交互过程在`LangGraph`框架下的具体实现思路如下图所示：

> 图片来源：https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/breakpoints/

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411051145371.png" width=100%></div>

&emsp;&emsp;`LangGraph`能够**在中断后继续运行的核心在于我们之前介绍的`checkpointer`组件**。这个组件能够在一个独立的线程中保存图中每个节点的状态。由于这些信息被持久化保存（包括将内存用作持久存储），我们就可以随时提取并修改图产生的数据。更改完成后，再将这些数据重新传回到图中以继续运行流程。这一机制是`LangGraph`已成功实现的功能。**由此可见 `Human-in-the-loop (HIL)` 并不是一个全新的组件，而是基于`LangGraph`底层的构建组件延展出来的一种实现方法。那这里我们就需要清楚两个概念，其一是用于中断两个本应顺序执行节点的操作，在`LangGraph`中称其为`breakpoint`（断点），其二是`breakpoint`是构建在`checkpointer`之上的。**

&emsp;&emsp;因此，当我们需要在定义的图结构中加入人机交互，这个图必须具备的两个核心参数正如`compile()`方法中的源码所示：

> LangGraph Graph Compile ：https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.StateGraph.compile

```python def compile( self, checkpointer: Checkpointer = None, *, store: Optional[BaseStore] = None, interrupt_before: Optional[Union[All, list[str]]] = None, interrupt_after: Optional[Union[All, list[str]]] = None, debug: bool = False, ) -> "CompiledStateGraph": ```

&emsp;&emsp;**其中，`checkpointer`参数可以接收任意类型的`checkpointer`，用来保存图的状态。而`interrupt_before`和`interrupt_after`参数，接收图中某个节点的名称，将其作为`breakpoint`，起到的作用是在该节点之前/之后中断图的继续运行**。我们来看一个具体的应用案例。

### 2. 拓展思考

#### 2.1 深度概念

&emsp;&emsp;Human-in-the-loop (HIL) 是一种让人类能够干预AI Agent决策过程的技术。通过在图中设置断点（breakpoint），可以在关键节点暂停执行，等待人工确认后再继续。

