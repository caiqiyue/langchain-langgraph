## <center>第一阶段、State 状态模式详解</center>

&emsp;&emsp;在上一课程中，我们已经了解了 LangGraph 的基本概念和核心组件。本课程我们将深入探讨 LangGraph 中 State 状态模式的定义和使用，以及 Reducer 函数的工作原理。

### 1. 使用字典类型定义状态

&emsp;&emsp;**定义图时要做的第一件事是定义图的`State`。** 状态表示会随着图计算的进行而维护和更新的上下文或记忆。在 LangGraph 中，我们使用 `TypedDict` 来定义状态模式。

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

| 状态类型 | 说明 |
| -------- | ---- |
| `InputState` | 定义图的输入结构 |
| `OutputState` | 定义图的输出结构 |
| `OverallState` | 合并后的完整状态 |

&emsp;&emsp;**为什么使用 TypedDict？** `TypedDict` 允许为字典中的键指定期望的具体类型，增强代码的可读性和安全性。在 LangGraph 图中，每个节点传递到下一个节点的数据，将直接影响到下一个节点能否顺利执行。

### 2. Reducer 函数基础

&emsp;&emsp;**Reducer 函数定义了如何合并多个状态更新。** 当同一个状态通道被多个节点更新时，Reducer 决定如何合并这些更新。

```python
from operator import add

# 定义带列表的状态
class ChatState(TypedDict):
    messages: list

# 自定义 Reducer：追加新消息
def message_adder(existing: list, new: list) -> list:
    return existing + new
```

| Reducer 类型 | 说明 |
| ------------ | ---- |
| 默认（覆盖） | 新值直接覆盖旧值 |
| 追加 | 使用 + 或 extend 追加 |
| 累加 | 使用 add 或 + 累加数值 |
| 自定义 | 根据业务逻辑自定义合并规则 |

&emsp;&emsp;**什么时候需要自定义 Reducer？** 当你需要：
- 追加消息到消息历史
- 累加计数器的值
- 合并列表而不是覆盖
- 实现复杂的合并逻辑

### 3. 在图状态中传递信息的思路

&emsp;&emsp;**节点可以写入图状态中的任何状态通道。** 图状态是初始化时定义的状态通道的并集。

```python
def agent_node(state: InputState):
    # 读取状态
    question = state["question"]
    print(f"[Agent] 接收到问题: {question}")

    # 返回的字典会更新状态
    return {"question": question}

def action_node(state: InputState):
    # 基于状态生成回答
    question = state["question"]
    answer = f"这是一个关于「{question}」的回答"

    return {"answer": answer}
```

![State状态传递图](../assets/第二课_01_State状态传递图.html)

**图解说明**：LangGraph 状态传递 — 输入状态经过节点处理后更新，传递给下一个节点

| 节点操作 | 说明 |
| -------- | ---- |
| 读取 state | 通过 `state["key"]` 读取 |
| 写入 state | 通过 `return {"key": value}` 写入 |
| 中间状态 | 可定义 Optional 字段暂存中间结果 |

### 4. MessageGraph 消息管理

&emsp;&emsp;`LangGraph` 提供了一种特殊的状态类型 `MessagesState`，专门用于管理消息历史。

```python
from langgraph.graph import MessagesState

def chat_node(state: MessagesState):
    # state["messages"] 是消息列表
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

| Message 类型 | 说明 |
| ------------ | ---- |
| `HumanMessage` | 用户消息 |
| `AIMessage` | AI 回复 |
| `SystemMessage` | 系统提示 |
| `ToolMessage` | 工具调用结果 |

### 5. 拓展思考

#### 5.1 为什么需要状态模式？

&emsp;&emsp;**默认情况下，`StateGraph`使用单模式运行，这意味着在图中的任意阶段都会读取和写入相同的状态通道，所有节点都使用该状态通道进行通信。**

&emsp;&emsp;这种设计使得：
- 节点可以访问先前步骤的信息
- 根据整个过程中积累的数据进行动态决策
- 实现复杂的多轮对话和工作流

#### 5.2 状态模式的高级用法

&emsp;&emsp;在某些情况下如果希望对图的状态有更多的控制：
- 内部节点可以传递图的输入/输出中不需要的信息
- 对图使用不同的输入/输出模式
- 使用自定义 Reducer 实现复杂的合并逻辑

&emsp;&emsp;**关键理解**：状态模式的设计哲学是让开发者能够灵活地控制数据在图中的流动方式，从而构建出符合业务需求的工作流程。