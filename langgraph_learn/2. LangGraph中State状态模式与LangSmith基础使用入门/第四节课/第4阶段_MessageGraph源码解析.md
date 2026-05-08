## <center>第4阶段、MessageGraph源码解析</center>

### 1. MessageGraph概述

&emsp;&emsp;**MessageGraph**是**StateGraph**的一个子类，使用了`Annotated[list[AnyMessage], add_messages]`来初始化其基类StateGraph。

&emsp;&emsp;**源码定义**：
```python
class MessageGraph(StateGraph):
    def __init__(self) -> None:
        super().__init__(Annotated[list[AnyMessage], add_messages]])
```

&emsp;&emsp;这里的`list[AnyMessage]`指明了MessageGraph的状态由消息列表组成，而这个列表类型是一个可以不断添加消息的结构（因为列表是可变的数据类型），MessageGraph中的每个节点都将消息列表作为输入，并返回零个或多个消息作为输出。

### 2. add_messages函数解析

&emsp;&emsp;**add_messages**函数是LangGraph预构建的Reducer函数，用于将每个节点的输出消息合并进图的状态中已存在的消息列表。

&emsp;&emsp;**核心逻辑**：
```python
def add_messages(left: Messages, right: Messages) -> Messages:
    """Merges two lists of messages, updating existing messages by ID.

    By default, this ensures the state is "append-only", unless the
    new message has the same ID as an existing message.
    """
```

&emsp;&emsp;**合并规则**：
- 如果right的消息与left的消息具有相同的ID，则right的消息将替换left的消息
- 否则作为一条新的消息进行追加
- 默认情况下，状态为"仅附加"

### 3. operator.add与add_messages的区别

&emsp;&emsp;使用`operator.add`能做到的功能极限是：发送到图表的手动状态更新将被附加到现有的消息列表中，而不是更新现有的消息。

&emsp;&emsp;为了避免这种情况，我们需要一个可以跟踪消息ID并覆盖现有消息的Reducer函数。`add_messages`函数实现了这个功能：
- 对于全新的消息，它会附加到现有列表
- 但它也会正确处理现有消息的更新（通过ID匹配）

### 4. MessageGraph与StateGraph的区别

&emsp;&emsp;**MessageGraph**：
- 专门用于以消息为中心的工作流程
- 使用单个仅附加消息列表作为其整个状态
- 每个节点处理该列表并可以返回其他消息

&emsp;&emsp;**StateGraph**：
- 更通用，适用于更广泛的应用程序
- 状态可以是任何Python类型（如TypedDict或Pydantic模型）
- 可以通过各种方式更新
- 除消息处理之外还支持更复杂的数据操作和工作流程

### 5. 拓展思考

#### 5.1 深度概念

&emsp;&emsp;**为什么需要add_messages而不是直接覆盖？**

&emsp;&emsp;在复杂的对话系统中，消息可能需要被修改或删除。例如：
- 用户可能需要编辑之前发送的消息
- 系统可能需要删除某些不当内容
- 消息可能在处理过程中被修改

&emsp;&emsp;使用add_messages可以通过ID追踪特定消息，支持更新和删除操作，而operator.add只能追加，无法实现这些功能。

#### 5.2 实践建议

&emsp;&emsp;对于人机交互的程序，在LangGraph的开发流程中，一般会首先创建一个StateGraph，然后定义一个使用add_messages作为Reducer的messages键。这种方式既保留了StateGraph的灵活性，又能够正确处理消息的更新和删除操作。