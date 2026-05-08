## <center>第2阶段、Reducer函数机制</center>

### 1. Reducer函数概述

&emsp;&emsp;LangGraph内部原理是：State中的每个key都有自己独立的Reducer函数，通过指定的reducer函数应用状态值的更新。

&emsp;&emsp;**Reducer函数**用来根据当前的状态（state）和一个操作（action）来计算并返回新的状态。它是一种设计模式，用于将业务逻辑与状态变更解耦，使得状态的变更预测性更强并且容易追踪。这样的函数通常接收两个参数：当前的状态（state）和一个描述应用了什么操作的对象（action），根据action类型来决定如何修改状态。

### 2. Reducer机制原理

&emsp;&emsp;默认情况下，如果没有显式指定Reducer，则对该键的所有更新执行的是**覆盖操作**。也就是说，当节点函数返回更新时，该键的旧值会被新值完全替代。

&emsp;&emsp;**示例**：
```python
class State(TypedDict):
    x: int
    y: int

# 节点函数
def addition(state):
    return {"x": state["x"] + 1}

def subtraction(state):
    return {"y": state["x"] - 2}
```

&emsp;&emsp;在这个例子中，由于没有指定Reducer，每次更新都是覆盖操作。addition返回的{"x": 11}会覆盖原来的{"x": 10}。

### 3. Annotated与operator.add

&emsp;&emsp;**Annotated**是Python的一个类型提示工具，属于typing模块。它被用来添加额外的信息或元数据到类型提示上。这些信息可以是关于如何使用该类型的指示，或者提供给静态类型检查器、框架和库的其他元数据。

&emsp;&emsp;通过使用Annotated，我们可以指定一个Reducer函数来控制状态如何更新：

```python
import operator
from typing import Annotated, List

class State(TypedDict):
    messages: Annotated[List[str], operator.add]
```

&emsp;&emsp;这里的operator.add表示可以通过使用添加操作将新消息与现有消息组合来更新列表。

### 4. Reducer的执行效果

&emsp;&emsp;当定义状态模式的结构发生变化后，在节点函数中的读取和存储逻辑也要发生相应的变化。

&emsp;&emsp;**工作流程**：
1. 初始状态包含一条消息 {"x": 10}
2. Node 1 (addition) 处理后返回 {"messages": [{"x": 11}]}
3. 由于使用operator.add，新消息被追加到现有列表
4. Node 2 (subtraction) 处理后返回 {"messages": [{"x": 9}]}
5. 最终状态包含两条消息的列表

### 5. 拓展思考

#### 5.1 深度概念

&emsp;&emsp;**为什么需要Reducer机制？**

&emsp;&emsp;Reducer机制的核心目的是允许更灵活地定义状态如何根据各种操作更新。通过指定不同的reducer函数，我们可以控制状态的每个部分应如何响应特定的更新。这对于构建复杂的工作流特别重要，例如：

&emsp;&emsp;- 消息处理场景：需要保留对话历史（追加操作）
&emsp;&emsp;- 计数器场景：需要累加计数（加法操作）
&emsp;&emsp;- 覆盖场景：直接用新值替代旧值（默认行为）

#### 5.2 实践建议

&emsp;&emsp;在实际开发中，选择合适的Reducer取决于业务需求：

&emsp;&emsp;- 如果需要保留历史记录，使用operator.add或自定义的追加Reducer
&emsp;&emsp;- 如果每次都是最新值覆盖，使用默认的覆盖Reducer
&emsp;&emsp;- 如果需要更复杂的合并逻辑，可以自定义Reducer函数