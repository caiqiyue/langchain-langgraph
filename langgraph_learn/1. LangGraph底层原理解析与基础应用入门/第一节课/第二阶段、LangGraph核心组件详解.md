## <center>第二阶段、LangGraph 核心组件详解</center>

&emsp;&emsp;在了解了 LangGraph 的底层原理后，本阶段我们将深入探讨 LangGraph 框架中各个核心组件的实现细节，包括 Graph 基类、StateGraph、节点、边等。

### 1. Graph 基类

&emsp;&emsp;对于任意一个简单或者复杂的图来说，都是基于`Graph`类来构建和管理图结构的。在`Graph`类中允许添加节点、边，并定义节点间的动态流转逻辑。

```python
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Set, Tuple, Union, Awaitable, Hashable

class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Any] = {}           # 存储图中所有节点
        self.edges: Set[Tuple[str, str]] = set()   # 存储图中所有边
        self.branches: defaultdict = defaultdict(dict)  # 条件分支
        self.support_multiple_edges = False         # 是否支持多重边
        self.compiled = False                      # 图是否已编译
```

| Graph 类方法 | 说明 |
| ------------ | ---- |
| `add_node()` | 添加新节点到图中 |
| `add_edge()` | 添加边连接两个节点 |
| `add_conditional_edges()` | 添加条件边 |
| `set_entry_point()` | 设置图的入口点 |
| `set_finish_point()` | 设置图的结束点 |
| `compile()` | 编译图，准备执行 |

### 2. StateGraph 状态图

&emsp;&emsp;**定义图时要做的第一件事是定义图的`State`。** 状态表示会随着图计算的进行而维护和更新的上下文或记忆。这个过程通过状态图`StateGraph`类实现，它继承自 `Graph` 类。

```python
class StateGraph(Graph):
    """StateGraph 是一个管理状态并通过定义的输入和输出架构支持状态转换的图"""
    def __init__(self, state_schema: Optional[Type[Any]] = None, config_schema: Optional[Type[Any]] = None) -> None:
        super().__init__()
        self.state_schema = state_schema      # 图状态的结构
        self.config_schema = config_schema    # 配置的结构
        self.nodes: Dict[str, Any] = {}       # 节点存储
        self.edges: Set[Tuple[str, str]] = set()   # 边存储
```

### 3. TypedDict 状态定义

&emsp;&emsp;`TypedDict` 是 `Python` 类型注解系统中的一个工具，它**允许为字典中的键指定期望的具体类型**。

```python
from typing import TypedDict

class Contact(TypedDict):
    name: str
    email: str
    phone: str

def send_email(contact: Contact) -> None:
    print(f"Sending email to {contact['name']}")

contact_info: Contact = {
    'name': 'Alice',
    'email': 'alice@example.com',
    'phone': '123-456-7890'
}
```

&emsp;&emsp;在 `LangGraph` 中，我们使用 `TypedDict` 来定义状态模式：

```python
from typing_extensions import TypedDict

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 合并
class OverallState(InputState, OutputState):
    pass
```

### 4. 节点（Nodes）详解

&emsp;&emsp;在 `LangGraph` 中，节点是一个 `Python` 函数（sync 或 async），接收当前`State`作为输入，执行自定义的计算，并返回更新的`State`。

```python
# 定义 Agent 节点
def agent_node(state: InputState):
    print("我是一个AI Agent。")
    return {"question": state["question"]}

# 定义 Action 节点
def action_node(state: InputState):
    print("我现在是一个执行者。")
    return {"answer": "我现在执行成功了"}

# 添加节点到图中
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)
```

| 节点特性 | 说明 |
| -------- | ---- |
| 输入 | 接收当前 State 作为第一个位置参数 |
| 输出 | 返回更新的 State 字典 |
| 名称 | 可以自定义，默认使用函数名 |
| 类型 | 支持 sync 和 async 两种 |

### 5. 边（Edges）详解

&emsp;&emsp;**边用来定义逻辑如何路由以及图何时开始与停止。**

```python
from langgraph.graph import START, END

# 普通边：直接连接
builder.add_edge(START, "agent_node")
builder.add_edge("agent_node", "action_node")
builder.add_edge("action_node", END)

# 条件边
builder.add_conditional_edges(
    source="agent_node",
    path=my_router_function,
    path_map={"search": "search_node", "answer": "answer_node"}
)
```

| 边类型 | 方法 | 说明 |
| ------ | ---- | ---- |
| 普通边 | `add_edge()` | 直接从一个节点到下一个节点 |
| 条件边 | `add_conditional_edges()` | 根据条件决定下一个节点 |
| 入口点 | `set_entry_point()` | 设置起始节点 |
| 结束点 | `set_finish_point()` | 设置终止节点 |
| 条件入口 | `set_conditional_entry_point()` | 根据条件决定起始节点 |

### 6. 图的编译与调用

&emsp;&emsp;最后，通过`compile`编译图。在编译过程中，会对图结构执行一些基本检查。

```python
# 编译图
graph = builder.compile()

# 调用图
result = graph.invoke({"question": "今天的天气怎么样？"})
print(result)  # {'answer': '我接收到的问题是：今天的天气怎么样？，读取成功了！'}
```

### 7. 拓展思考

#### 7.1 为什么需要 StateGraph？

&emsp;&emsp;**默认情况下，`StateGraph`使用单模式运行，这意味着在图中的任意阶段都会读取和写入相同的状态通道，所有节点都使用该状态通道进行通信。**

&emsp;&emsp;在某些情况下如果希望对图的状态有更多的控制：
- 内部节点可以传递图的输入/输出中不需要的信息
- 对图使用不同的输入/输出模式

#### 7.2 状态通道的工作原理

&emsp;&emsp;不同节点间能够传递信息的原因是因为**节点可以写入图状态中的任何状态通道**。图状态是初始化时定义的状态通道的并集。

&emsp;&emsp;当我们定义 `OverallState(InputState, OutputState)` 时，实际上是合并了输入状态和输出状态的所有字段，使得节点可以在执行过程中读写这些状态通道。**这正是 LangGraph 实现节点间数据传递的核心机制。**