# 2. LangGraph底层源码解析

&emsp;&emsp;在上一小节的原理介绍部分，我们在图中提到了节点、边、状态和路由四个概念，那在`LangGraph`框架中，各个组件是怎么实现，以及如何定义图结构呢？ 我们将在这一小节展开详细的介绍和代码实践。首先我们来看图。

## 2.1 Graph基类

&emsp;&emsp;对于任意一个简单或者复杂的图来说，都是基于`Graph`类来构建和管理图结构的。在`Graph`类中允许添加节点、边，并定义节点间的动态流转逻辑。如下是`Graph`类的主要组成部分和功能：

> Class Graph ：https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.graph.Graph

```python
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Set, Tuple, Union, Awaitable, Hashable

class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Any] = {}  # 一个字典，用于存储图中的所有节点。每个节点可以是一个字符串标识或者是一个可调用对象
        self.edges: Set[Tuple[str, str]] = set()  # 一个集合，用来存储图中所有的边，边由一对节点名称组成，表示从一个节点到另一个节点的直接连接。
        self.branches: defaultdict = defaultdict(dict)  # 一个默认字典，用于存储条件分支，允许从一个节点根据特定条件转移到多个不同的节点。
        self.support_multiple_edges = False  # 一个布尔值，指示图是否支持同一对节点间的多条边。
        self.compiled = False    #  一个布尔值，表示图是否已经被编译。编译是指图的结构已经设置完毕，准备进行执行。

    @property
    def _all_edges(self) -> Set[Tuple[str, str]]:
        """
        添加一个新节点到图中。节点可以有附加的元数据，这些元数据存储在节点的字典中。
        """
        return self.edges

    def add_node(self, node: Union[str, Callable], action: Optional[Callable] = None, *, metadata: Optional[Dict[str, Any]] = None) -> 'Graph':
        """
        添加一个新节点到图中。节点可以有附加的元数据，这些元数据存储在节点的字典中。
        """
        pass

    def add_edge(self, start_key: str, end_key: str) -> 'Graph':
        """
        在图中添加一条边，连接两个指定的节点。
        """
        pass

    def add_conditional_edges(self, source: str, path: Callable, path_map: Optional[Dict[Hashable, str]] = None, then: Optional[str] = None) -> 'Graph':
        """
        添加一个条件边，允许在执行时根据某个条件从一个节点动态地转移到一个或多个节点。
        """
        pass

    def set_entry_point(self, key: str) -> 'Graph':
        """
        设置图的入口点，即定义图执行的起始节点。
        """
        pass

    def set_conditional_entry_point(self, path: Callable, path_map: Optional[Dict[Hashable, str]] = None, then: Optional[str] = None) -> 'Graph':
        """
        设置一个条件入口点，允许根据条件动态决定图的起始执行点。
        """
        pass

    def set_finish_point(self, key: str) -> 'Graph':
        """
        设置结束点，定义图执行到此节点时将停止。
        """
        pass

    def validate(self, interrupt: Optional[Set[str]] = None) -> 'Graph':
        """
        验证图的结构是否正确，确保所有节点和边的定义都符合逻辑和图的规则。
        """
        pass

    def compile(self, checkpointer=None, interrupt_before: Optional[Set[str]] = None, interrupt_after: Optional[Set[str]] = None, debug: bool = False) -> 'Graph':
        """
        编译图，确认图的结构合法且可执行后，准备图以供执行。
        """
        pass
```

&emsp;&emsp;从源码中可以看出，`Graph`该类提供了丰富的方法来控制图的编译和执行，使其适用于需要复杂逻辑和流程控制的应用场景。

## 2.2 GraphState

&emsp;&emsp;**定义图时要做的第一件事是定义图的`State`。**状态表示会随着图计算的进行而维护和更新的上下文或记忆。它用来确保图中的每个步骤都可以访问先前步骤的相关信息，从而可以根据整个过程中积累的数据进行动态决策。这个过程通过状态图`StateGraph`类实现，它继承自 `Graph` 类，这意味着 `StateGraph` 会使用或扩展基类的属性和方法。

> Class StateGraph：https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.StateGraph

```python

from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type, Union

class StateGraph(Graph):

    """StateGraph 是一个管理状态并通过定义的输入和输出架构支持状态转换的图。"""
    def __init__(self, state_schema: Optional[Type[Any]] = None, config_schema: Optional[Type[Any]] = None) -> None:
        super().__init__()
        self.state_schema = state_schema      # 一个可选的类型参数，定义图状态的结构。这是用于定义和验证图中节点处理的状态数据的模式。
        self.config_schema = config_schema    # 一个可选的类型参数，用于定义配置的结构。这可以用于定义和验证图的配置参数。
        self.nodes: Dict[str, Any] = {}       # 一个字典，用于存储图中的节点。每个节点可以关联特定的动作和其他数据。
        self.edges: Set[Tuple[str, str]] = set()   # 一个集合，存储图中所有的边。每条边由一对字符串组成，表示从一个节点到另一个节点的连接。
        self.branches: defaultdict = defaultdict(dict)   # 一个默认字典，用于管理节点间的条件分支。这使得从一个节点基于某些条件跳转到不同的节点成为可能。

    def add_node(self, node: Union[str, Callable], action: Optional[Callable] = None, *, metadata: Optional[Dict[str, Any]] = None) -> 'StateGraph':
        """向图中添加一个新节点。节点可以是一个具名字符串或一个可调用对象（如函数）, 如果node是字符串，则action应为与节点关联的可调用动作。"""
        pass

    def add_edge(self, start_key: str, end_key: str) -> 'StateGraph':
        """在图中添加一条边，连接两个节点。"""
        pass

    def compile(self) -> 'CompiledStateGraph':
        """编译图，将其转换成可运行的形式。包括验证图的完整性、预处理数据等。"""
        pass

```

- **什么是图的模式**

&emsp;&emsp;**默认情况下，`StateGraph`使用单模式运行，这意味着在图中的任意阶段都会读取和写入相同的状态通道，所有节点都使用该状态通道进行通信。**除此之外，在某些情况下如果希望对图的状态有更多的控制，比如：

- 内部节点可以传递图的输入/输出中不需要的信息。
- 对图使用不同的输入/输出模式。例如，输出可能仅包含单个相关输出键。

&emsp;&emsp;`LangGraph`的底层实现上提供了多种不同图模式的支持，这可以通过`state_schema`来进行灵活的指定。不过关于自定义的图模式，因为涉及到更多的基础概念，我们将在课程的后半部分在展开详细的介绍。

&emsp;&emsp;首先来看图的单模式。任何模式都包含输入和输出，输入模式需要确保提供的输入与预期结构匹配，而输出模式根据定义的输出模式过滤内部数据以仅返回相关信息。而这个预期结构的校验，由`TypedDict`工具来限定。

- **TypeDict** 

&emsp;&emsp;`TypedDict` 是 `Python` 类型注解系统中的一个工具，它**允许为字典中的键指定期望的具体类型**。在 `Python` 的 `typing` 模块中定义，通常用于增强代码的可读性和安全性，特别是在字典对象结构固定且明确时。示例代码如下：

```python
from typing import TypedDict

class Contact(TypedDict):
    name: str
    email: str
    phone: str

def send_email(contact: Contact) -> None:
    print(f"Sending email to {contact['name']} at {contact['email']}")

# 使用定义好的 TypedDict 创建字典
contact_info: Contact = {
    'name': 'Alice',
    'email': 'alice@example.com',
    'phone': '123-456-7890'
}

send_email(contact_info)```

&emsp;&emsp;在这个示例中，`Contact` 类型定义了三个必须的字段：`name`，`email`，和 `phone`，每个字段都是字符串（Str）形式。当创建 `contact_info` 字典时，必须提供所有这些字段。函数 `send_email` 则利用这个类型安全的字典进行操作。这样的 `TypedDict` 使用场景非常适合那些需要确保字典中具有特定字段和类型的应用场景，如处理从外部API返回的数据或者在内部各个模块间传递复杂的数据结构，因为在`LangGraph`图中，每个节点传递到下一个节点的数据，将直接影响到下一个节点能否顺利执行。

&emsp;&emsp;接下来我们实践在`LangGraph`中通过`Typedict`定义单输入输出模式。首先，需要安装所需的依赖包，代码如下：

```python
# ! pip install langgraph==0.2.35 ```

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict


# 定义输入的模式
class InputState(TypedDict):
    question: str


# 定义输出的模式
class OutputState(TypedDict):
    answer: str


# 将 InputState 和 OutputState 这两个 TypedDict 类型合并成一个字典类型。
class OverallState(InputState, OutputState):
    pass```

&emsp;&emsp;接下来，创建一个 `StateGraph` 对象，使用 `OverallState` 作为其状态定义，同时指定了输入和输出类型分别为 `InputState` 和 `OutputState`，代码如下：

```python
# 明确指定它的输入和输出数据的结构或模式
builder = StateGraph(OverallState, input=InputState, output=OutputState)```

&emsp;&emsp;创建 `builder` 对象后，相当于构建了一个图结构的框架。接下来的步骤是向这个图中添加节点和边，完善和丰富图的内部执行逻辑。

## 2.3 Nodes

&emsp;&emsp;在 `LangGraph` 中，节点是一个 `python` 函数（sync 或async ），接收当前`State`作为输入，执行自定义的计算，并返回更新的`State`。所以其中第一个位置参数是`state` 。

```python
def agent_node(state:InputState):
    print("我是一个AI Agent。")
    return ```

```python
def action_node(state:InputState):
    print("我现在是一个执行者。")
    return {"answer":"我现在执行成功了"}```

&emsp;&emsp;定义好了节点以后，我们需要使用`add_node`方法将这些节点添加到图中。在将节点添加到图中的时候，可以自定义节点的名称。而如果不指定名称，则会为自动指定一个与函数名称等效的默认名称。代码如下：

```python
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)```

&emsp;&emsp;现在有了图结构，并且图结构中也存在两个孤立的节点`agent_node`和`action_node`，接下来我们要做的事就是需要将图中的节点按照我们所期望的方式进行连接，这需要用到的就是`Edges` - 边。

## 2.4 Edges

&emsp;&emsp;Edges（边）用来定义逻辑如何路由以及图何时开始与停止。这是代理工作以及不同节点如何相互通信的重要组成部分。有几种关键的边类型：
- 普通边：直接从一个节点到下一个节点。
- 条件边：调用函数来确定下一个要转到的节点。
- 入口点：当用户输入到达时首先调用哪个节点。
- 条件入口点：调用函数来确定当用户输入到达时首先调用哪个节点。

&emsp;&emsp;同样，我们先看普通边。如果直接想从节点`A`到节点`B`，可以直接使用`add_edge`方法。注意：`LangGraph`有两个特殊的节点：`START`和`END`。`START`表示将用户输入发送到图的节点。使用该节点的主要目的是确定应该首先调用哪些节点。`END`节点是代表终端节点的特殊节点。当想要指示哪些边完成后没有任何操作时，将使用该节点。因此，一个完整的图就可以使用如下代码进行定义：

```python
from langgraph.graph import START, END

builder.add_edge(START, "agent_node")
builder.add_edge("agent_node", "action_node")
builder.add_edge("action_node", END)```

&emsp;&emsp;最后，通过`compile`编译图。在编译过程中，会对图结构执行一些基本检查（如有没有孤立节点等）。代码如下：

```python
graph = builder.compile()```

&emsp;&emsp;至此，我们已经成功构建了一个完整的图结构，并准备好接收用户的请求。

## 2.5 Graph 的调用方法

&emsp;&emsp;要调用图中的方法，可以使用 `invoke` 方法。示例代码如下：

```python
graph.invoke({"question":"你好"})```

```python
graph.invoke({"question":"今天的天气怎么样？"})```

&emsp;&emsp;在这个过程中，我们将`state: InputState`作为输入模式传递给`agent_node`，在传递到`action_node`，最后由`action_node`传递到`END`节点。节点之间通过边是已经构建了完整的通路，那么如果我们想要传递每个节点的状态信息，则可以稍加修改即可实现。对于图模式，我们的定义方法如下：

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

```python
def agent_node(state: InputState):
    print("我是一个AI Agent。")
    return {"question": state["question"]}```

```python
def action_node(state: InputState):
    print("我现在是一个执行者。")
    step = state["question"]
    return {"answer": f"我接收到的问题是：{step}，读取成功了！"}```

```python
# 明确指定它的输入和输出数据的结构或模式
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)

# 添加便
builder.add_edge(START, "agent_node")
builder.add_edge("agent_node", "action_node")
builder.add_edge("action_node", END)

# 编译图
graph = builder.compile()```

&emsp;&emsp;执行调用：

```python
graph.invoke({"question":"今天的天气怎么样？"})```

```python
graph.invoke({"question":"你好，我用来测试"})```

&emsp;&emsp;不同节点间能够传递信息的原因是因为节点可以写入图状态中的任何状态通道。图状态是初始化时定义的状态通道的并集，而我们定义的状态通道包含了`OverallState`以及过滤器`InputState`和`OutputState` 。
