## <center>第3阶段、基于记忆Store知识库</center>

# 3.长期记忆和Store（仓库）

&emsp;&emsp;仅使用`checkpointer`，我们无法做到跨线程共享信息。这激发了对`Store`的需求。`LangGraph`通过`BaseStore`接口提供内置文档存储。与通过线程 ID 保存状态的`checkpointer`不同，存储使用自定义命名空间来组织数据。常见用例包括存储用户配置文件、构建知识库以及管理所有线程的全局首选项。具体的**实现形式是：`LangGraph` 将长期记忆作为 `JSON` 文档存储在`Store`中，每个`memory`都组织在自定义`namespace`（类似于文件夹）和不同的`key` （例如文件名）下。命名空间通常包含用户或组织 ID 或其他标签，以便更轻松地组织信息。这种结构可以实现存储器的分层组织。然后通过内容过滤器支持跨命名空间搜索。** &emsp;&emsp;**整体而言，`LangGraph` 中的长期记忆允许系统保留不同对话或会话中的信息。与线程范围的短期内存不同，长期内存保存在自定义“命名空间”中。**

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241101144509032.png" width=100%></div>

> `Store`的实现源码：https://langchain-ai.github.io/langgraph/reference/store/

&emsp;&emsp;具体的实现方法，是我们可以定义一个`InMemoryStore`来跨线程存储有关用户的信息。`InMemoryStore`会与`checkpointer`协同工作：由`checkpointer`将状态保存到线程，而`InMemoryStore`允许我们存储任意信息以供跨线程访问。我们看一下其实现细节：

```python
# 文件: 24_3_基于记忆Store知_py
from langgraph.store.memory import InMemoryStore
in_memory_store = InMemoryStore()
```

&emsp;&emsp;`namespase`的类型是`tuple`，需要一个键值对。可以理解为：我们以 `user_id=1`这个人的电脑创建了一个`memories`文件夹，所有这个人的数据，都存存放在这个文件夹中。

```python
# 文件: 25_3_基于记忆Store知_py
user_id = "1"
namespace_for_memory = (user_id, "memories")
```

&emsp;&emsp;接下来使用`.put`方法将`memory`保存到存储中的命名空间中。每个`memory`都有唯一的一个对应的`id`.

```python
# 文件: 26_3_基于记忆Store知_py
import uuid

memory_id = str(uuid.uuid4())
memory = {"user" : "你好，我叫木羽"}
in_memory_store.put(namespace_for_memory, memory_id,  memory)
```

&emsp;&emsp;当创建完成后，可以使用`store.search`读取命名空间中的记忆，这将以列表的形式返回给定用户的所有记忆。最近的记忆是列表中的最后一个。

```python
# 文件: 27_3_基于记忆Store知_py
memories = in_memory_store.search(namespace_for_memory)
memories[-1].dict()
```

&emsp;&emsp;理解了上述过程后，就可以使用 `LangGraph` 中的`in_memory_store`方法了，当我们在编译图表时传递 `store` 对象，就会允许图中的每个节点访问 `store`，定义节点函数时的时候，就可以定义`store`关键字参数，`LangGraph` 会自动传递编译图时使用的 `store` 对象，代码如下所示：

```python
# 文件: 28_3_基于记忆Store知_py
import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore


in_memory_store = InMemoryStore()
memory = MemorySaver()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# 定义大模型实例
llm = ChatOpenAI(model="gpt-4o")


# 定义状态模式
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 定义对话节点， 访问记忆并在模型调用中使用它们。
def call_model(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    # 获取用户id
    user_id = config["configurable"]["user_id"]

    # 定义命名空间
    namespace = ("memories", user_id)

    # 根据用户id检索记忆
    memories = store.search(namespace)
    info = "\n".join([d.value["data"] for d in memories])

    # # 存储记忆
    last_message = state["messages"][-1]
    store.put(namespace, str(uuid.uuid4()), {"data": last_message.content})

    system_msg = f"Answer the user's question in context: {info}"

    response = llm.invoke(
        [{"type": "system", "content": system_msg}] + state["messages"]
    )

    # 存储记忆
    store.put(namespace, str(uuid.uuid4()), {"data": response.content})
    return {"messages": response}

# 构建状态图
builder = StateGraph(State)

# 向图中添加节点
builder.add_node("call_model", call_model)

# 构建边
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

# 编译图
graph = builder.compile(checkpointer=memory, store=in_memory_store)

# 可视化
display(Image(graph.get_graph().draw_mermaid_png()))
```

&emsp;&emsp;接下来我们进行测试：

```python
# 文件: 29_3_基于记忆Store知_py
config = {"configurable": {"thread_id": "10"}, "user_id": "6"}

async for chunk in graph.astream({"messages": ["你好，我是木羽"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

```python
# 文件: 30_3_基于记忆Store知_py
config = {"configurable": {"thread_id": "10"}, "user_id": "6"}

async for chunk in graph.astream({"messages": ["你知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;这一次我们传入相同的`user_id`，但开启一个新的线程：

```python
# 文件: 31_3_基于记忆Store知_py
config = {"configurable": {"thread_id": "11"}, "user_id": "6"}

async for chunk in graph.astream({"messages": ["你知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;能够发现，我们已经正确的实现了跨线程的记忆能力。而如果使用新的`user_id`，将会开启全新的交互。

```python
# 文件: 32_3_基于记忆Store知_py
config = {"configurable": {"thread_id": "18"}, "user_id": "8"}

async for chunk in graph.astream({"messages": ["你知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;我们可以直接去访问`store`查看存储的`memory`信息。

```python
# 文件: 33_3_基于记忆Store知_py
for memory in in_memory_store.search(("memories", "6")):
    print(memory.value)
```

```python
# 文件: 34_3_基于记忆Store知_py
for memory in in_memory_store.search(("memories", "8")):
    print(memory.value)
```

&emsp;&emsp;有效的记忆管理可以增强代理维护上下文、从过去的经验中学习以及随着时间的推移做出更明智决策的能力。大多数`AI Agent`构建的应用程序都需要记忆来在多个交互中共享上下文。在 `LangGraph` 中，这种记忆就是通过`checkpointer` 和 `store` 来做持久性，从而添加到任何`StateGraph`中。最常见的用例之一是用它来跟踪对话历史记录，但是也有很大的优化空间，因为随着对话变得越来越长，历史记录会累积并占用越来越多的上下文窗口，导致对大模型的调用更加昂贵和耗时，并且可能会出错。为了防止这种情况发生，我们一般是需要借助一些优化手段去管理对话历史记录，同时更加适配生产环境的` PostgresSaver / AsyncPostgresSaver ）`高级检查点，我们也将随着知识点的进一步补充后，再结合实际的案例进行详细的讲解。

### 2. 拓展思考

#### 2.1 深度概念

&emsp;&emsp;本节内容涵盖了LangGraph中记忆机制的核心概念，包括短期记忆（通过checkpointer实现）和长期记忆（通过Store实现）。

