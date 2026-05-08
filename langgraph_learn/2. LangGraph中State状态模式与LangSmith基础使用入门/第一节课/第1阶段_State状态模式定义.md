## <center>第1阶段、State状态模式定义</center>

### 1. State状态模式概述

&emsp;&emsp;在LangGraph框架中，不论构建的代理简单或复杂，其本质都是通过节点（Node）和边（Edge）的有机组合来形成一个完整的图（Graph）。这种构建方式所形成的工作流逻辑十分清晰：每个节点在完成其任务后，都会通过边来指示下一个工作步骤，从而赋予整个应用系统更高的灵活性和可扩展性。

&emsp;&emsp;LangGraph的底层图算法采用消息传递机制来定义和执行这些图中的交互流程，其中状态（State）组件扮演着关键的载体角色，负责在图的各个节点之间传递信息。State实际上是一个共享的数据结构，表现为一个简单的字典，通过对这个字典进行读写操作，可以实现自左而右的数据流动，从而构建一个可运行的图结构。

### 2. State的定义模式

#### 2.1 使用字典类型定义状态

&emsp;&emsp;对于State的定义，最简单的方式是使用Python的字典类型（dict）。LangGraph的StateGraph类接受dict作为状态模式参数，节点函数可以读取和更新字典中的键值。

&emsp;&emsp;**示例代码**：
```python
from langgraph.graph import StateGraph

# 构建图 - 使用dict作为状态类型
builder = StateGraph(dict)

# 定义节点函数
def addition(state):
    return {"x": state["x"] + 1}

def subtraction(state):
    return {"y": state["x"] - 2}

# 向图中添加两个节点
builder.add_node("addition", addition)
builder.add_node("subtraction", subtraction)

# 构建节点之间的边
builder.add_edge(START, "addition")
builder.add_edge("addition", "subtraction")
builder.add_edge("subtraction", END)

# 编译图
graph = builder.compile()

# 执行图
result = graph.invoke({"x": 10})
```

#### 2.2 使用TypedDict定义状态

&emsp;&emsp;使用TypedDict来定义State的模式，可以精确控制图结构中状态信息的格式和类型。与传统字典类型相比，TypedDict允许明确指定每个键的类型，有助于防止在状态管理过程中出现类型错误。

&emsp;&emsp;**示例代码**：
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class State(TypedDict):
    x: int
    y: int

builder = StateGraph(State)
```

### 3. 节点与状态交互

&emsp;&emsp;图中的每个节点都具备访问、读取和写入状态的权限。当某一个节点去修改状态时，它会将此信息广播到图中的所有其他节点。这种广播机制允许其他节点响应状态的变化并相应地调整其行为。

&emsp;&emsp;**关键特性**：
- 节点函数不需要返回整个状态，而是仅返回它们更新的部分
- LangGraph的内部机制自动处理状态的合并和维护
- 状态在任何给定时间只包含来自一个节点的更新信息

### 4. 图的可视化

&emsp;&emsp;LangGraph提供了三种图形可视化方法：

&emsp;&emsp;**Mermaid.Ink**：一个开源服务，可以根据Mermaid代码生成图表的URL，支持多种输出格式。

&emsp;&emsp;**Mermaid + Pyppeteer**：通过浏览器自动截图功能捕获Mermaid图表，生成图像文件。Windows系统建议使用此方法。

&emsp;&emsp;**Graphviz**：非常适合于复杂图形的生成，支持多种格式的图像输出。

&emsp;&emsp;**代码示例**：
```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

### 5. 拓展思考

#### 5.1 深度概念

&emsp;&emsp;**为什么仅通过返回需要更新的键值，就能实现状态的全局共享？**

&emsp;&emsp;这是因为LangGraph内部为每个State中的每个key都关联了Reducer函数。默认情况下，如果没有显式指定Reducer，则对该键的所有更新执行的是覆盖操作。当节点函数返回更新时，LangGraph会根据Reducer函数的规则将更新合并到全局状态中。

#### 5.2 实践建议

&emsp;&emsp;在实际开发中，强烈建议使用TypedDict来定义和管理状态，特别是在涉及复杂状态逻辑和多个状态依赖的应用中。这种方式可以获得更好的类型检查和代码提示，减少运行时错误。