## <center>第2阶段、基于记忆和Checkpointer实现状态持久化</center>

# 2. 短期记忆及Checkpointer（检查点）

&emsp;&emsp;在介绍`LangGraph`中的`Checkpointer`功能之前，我们先利用已学的知识分析一下图在运行时处理中间过程信息的方式。这里我们构建一个简单的图，包括两个节点：`call_model`节点用于加载一个大模型并回答用户输入的问题，而`translate_message`节点则将`call_model`生成的回答翻译成英文。以下是完整的代码实现：

```python
# 文件: 01_2_基于记忆和Check_py
import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages


if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# 定义大模型实例
llm = ChatOpenAI(model="gpt-4o")

# 定义状态模式
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 定义大模型交互节点
def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": response}

# 定义翻译节点
def translate_message(state: State):
    system_prompt = """
    Please translate the received text in any language into English as output
    """
    messages = state['messages'][-1]
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"messages": response}

# 构建状态图
builder = StateGraph(State)

# 向图中添加节点
builder.add_node("call_model", call_model)
builder.add_node("translate_message", translate_message)

# 构建边
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "translate_message")
builder.add_edge("translate_message", END)

# 编译图
simple_short_graph = builder.compile()

# 生成可视化图像结构
display(Image(simple_short_graph.get_graph().draw_mermaid_png()))
```

&emsp;&emsp;首先我们测试图的运行流程，这里使用异步的流式输出形式，并指定它的输出模式为`values`。代码如下

```python
# 文件: 02_2_基于记忆和Check_py
async for chunk in simple_short_graph.astream(input={"messages": ["你好，我叫木羽"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()
```

```python
# 文件: 03_2_基于记忆和Check_py
async for chunk in simple_short_graph.astream(input={"messages": ["请问，我叫什么？"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;这里确定当前的`graph`实例不具备任何的上下文记忆能力。然后我们进入`Debug`模式去分析其中间过程。代码如下：

```python
# 文件: 04_2_基于记忆和Check_py
async for chunk in simple_short_graph.astream({"messages": ["你好，我叫木羽"]}, stream_mode="debug"):
    # print(chunk)
    print(f"Task id : {chunk['payload']['id']}")
    if chunk["type"] == "task":
        for message in chunk["payload"]["input"]["messages"]:
            print(f"Message id:{message.id}, Message content:{message.content}")

    if chunk["type"] == "task_result":
         print(f"Message id:{chunk['payload']['result'][0][1].id}, Message content:{chunk['payload']['result'][0][1].content}")  # tuple 类型

    print("------------------------------------------------")
    print("------------------------------------------------")
```

&emsp;&emsp;再进行一轮问答：

```python
# 文件: 05_2_基于记忆和Check_py
async for chunk in simple_short_graph.astream({"messages": ["你知道我叫什么吗?"]}, stream_mode="debug"):
    # print(chunk)
    print(f"Task id : {chunk['payload']['id']}")
    if chunk["type"] == "task":
        for message in chunk["payload"]["input"]["messages"]:
            print(f"Message id:{message.id}, Message content:{message.content}")

    if chunk["type"] == "task_result":
         print(f"Message id:{chunk['payload']['result'][0][1].id}, Message content:{chunk['payload']['result'][0][1].content}")  # tuple 类型

    print("------------------------------------------------")
    print("------------------------------------------------")
```

&emsp;&emsp;观察上面两轮对话中我们打印的关键信息。在`State`状态管理的事件流中，每个阶段都会生成一个`task`，并且每个`task`被分为两个阶段：生成（当前事件）和执行结果（`task_result`）。这两个阶段都有一个唯一的且共同的`task id`。此外，每条消息，无论是用户输入的还是大模型生成的回复，都有一个唯一的ID。

&emsp;&emsp;那么，既然每个消息都有不同的`ID`, 如果想让后面的交互过程知道前面都产生了哪些消息，**如果有一种机制可以把消息维护起来（比如使用字典来存储会话，其中每个会话ID映射到一个消息列表），当新一轮的输入进来，我们把指定的消息列表作为初始状态追加到`State`状态中（默认新一轮`State`状态会重新初始化），借助`State`状态可以全局共享的机制，是不是就能实现上下文记忆了呢？** ```json sessions = { "会话1": [ { "id": "message_1", "content": "你好！", "timestamp": "2024-10-30T09:00:00" }, { "id": "message_2", "content": "请问有什么可以帮助您的？", "timestamp": "2024-10-30T09:05:00" }, { "id": "message_3", "content": "感谢，再见！", "timestamp": "2024-10-30T09:10:00" } ], "会话2": [ { "id": "message_5", "content": "怎么了解更多产品信息？", "timestamp": "2024-10-30T10:00:00" }, { "id": "message_7", "content": "请查看我们的产品目录。", "timestamp": "2024-10-30T10:05:00" }, { "id": "message_3", "content": "感谢，再见！", "timestamp": "2024-10-30T09:10:00" } ] } ```

&emsp;&emsp;理解到这里，现在我们就可以说：`LangGraph`框架中的`checkpointer`做的就是这样的事。具体来说，**它就是通过一些数据结构来存储`State`状态中产生的信息，并且在每个`task`开始时去读取全局的状态。**主要通过以下四种方式来实现： - **MemorySaver：**用于实验性质的记忆检查点。 - **SqliteSaver / AsyncSqliteSaver：**使用 `SQLite` 数据库 实现的记忆检查点，适合实验性质和本地工作流程。 - **PostgresSaver / AsyncPostgresSaver：**使用 `Postgres` 数据库实现的高级检查点，适合在生产系统中使用。 - **支持自定义检查点**。

&emsp;&emsp;不同类型的`checkpointer`以不同的形式去管理`State`状态中记录的中间状态信息。但这还不够。为了将一系列产生的消息归属到正确的类别中，就像上面的`会话1`包含一系列的问答，而`会话2`包含另一批系列的回答**，`LangGraph`框架引入`Thread`（线程）概念来充当`会话`的角色。每个线程代表一个独特的交互或对话流。而`thread_id`是与特定执行线程关联的唯一标识符。**各个概念之间的关联如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/20241031001.png" width=100%></div>

&emsp;&emsp;`checkpointer`是`memory`的一种特定实现，它在执行期间保存图在各个点的状态，使系统能够在中断时从该点恢复。这**与 `LangGraph` 中状态的一般概念不同，后者表示应用程序在任何给定时刻的当前快照。虽然状态是动态的并且随着图形的执行而变化，但`checkpointer`提供了一种存储和检索历史状态的方法**，从而促进更复杂的工作流程和人机交互。

&emsp;&emsp;接下来，我们以 `MemorySaver` 这个实现`checkpointer`的方法为例，帮助大家理解这个过程。

## 2.1 检查点的特定实现类型-MemorySaver

&emsp;&emsp;`LangGraph` 框架有一个内置的持久层，通过`checkpointer`实现。**当使用`checkpointer`编译图时，检查点会在每个超级步骤中保存图状态的`checkpoint`。这些`checkpoint`被保存到一个`thread`中，可以在图执行后访问**。如下图所示：

> 超级步骤可以被认为是图节点上的单次迭代。并行运行的节点是同一超级步骤的一部分，而顺序运行的节点则属于单独的超级步骤。在图执行开始时，所有节点都开始处于inactive状态。当节点在其任何传入边缘（或“通道”）上接收到新消息（状态）时，该节点将变为active 。然后，活动节点运行其功能并以更新进行响应。在每个超级步骤结束时，没有传入消息的节点通过将自己标记为inactive 。当所有节点inactive并且没有消息在传输时，图执行终止。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241028150907387.png" width=100%></div>

&emsp;&emsp;`MemorySaver`是实现上述流程的一种形式，它通过使用 `defaultdict` 将`checkpointer`存储在`memory`中。如下源码所示：

```python class MemorySaver( BaseCheckpointSaver[str], AbstractContextManager, AbstractAsyncContextManager ): # thread ID -> checkpoint NS -> checkpoint ID -> checkpoint mapping storage: defaultdict[ str, dict[ str, dict[str, tuple[tuple[str, bytes], tuple[str, bytes], Optional[str]]] ], ] writes: defaultdict[ tuple[str, str, str], dict[tuple[str, int], tuple[str, str, tuple[str, bytes]]] ] ```

> https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.memory.MemorySaver 

&emsp;&emsp;使用的方法非常简单，就是在创建任何 `LangGraph` 图时，通过在编译图时添加`MemorySaver`来将其设置为保留其`State`状态中的数据，即： ```python from langgraph.checkpoint.memory import MemorySaver checkpointer = MemorySaver() graph.compile(checkpointer=checkpointer) ```

&emsp;&emsp;我们通过一个图来理解这个中间过程，构建如下图结构。注意：**在编译图的时候，添加`MemorySaver`作为`checkpointer`提供`Memory`功能。**

```python
# 文件: 06_2_基于记忆和Check_py
# 导入检查点
from langgraph.checkpoint.memory import MemorySaver

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")


class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": response}

def translate_message(state: State):
    system_prompt = """
    Please translate the received text in any language into English as output
    """
    messages = state['messages'][-1]
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"messages": response}

builder = StateGraph(State)

builder.add_node("call_model", call_model)
builder.add_node("translate_message", translate_message)

builder.add_edge(START, "call_model")
builder.add_edge("call_model", "translate_message")
builder.add_edge("translate_message", END)


memory = MemorySaver()
graph_with_memory = builder.compile(checkpointer=memory)   # 在编译图的时候添加检查点

display(Image(graph_with_memory.get_graph().draw_mermaid_png()))
```

&emsp;&emsp;当添加了`checkpointer`后，在该图执行的每个超级步骤中会自动创建检查点。即每个节点处理其输入并更新状态后，会当前状态将保存为检查点。但如果像普通图一样，仅传入输入的问题是会报错的，如下所示：

```python
# 文件: 07_2_基于记忆和Check_py
async for chunk in graph_with_memory.astream(input={"messages": ["你好，我叫木羽"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;这是因为**当增加了`checkpointer`后，需要`Thread`来作为`checkpointer`保存图中每个检查点的唯一标识，而`Thread`（线程）又是通过`thread_id`来标识某个特定执行线程，所以在使用`checkpointer`调用图时，必须指定`thread_id`，指定的方式是作为配置`configurable`的一部分进行声明。** 正确调用的代码就如下所示：

```python
# 文件: 08_2_基于记忆和Check_py
# 这个 thread_id 可以取任意数值
config = {"configurable": {"thread_id": "1"}}

for chunk in graph_with_memory.stream({"messages": ["你好，我叫木羽"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()


for chunk in graph_with_memory.stream({"messages": ["请问我叫什么？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

```python
# 文件: 09_2_基于记忆和Check_py
for chunk in graph_with_memory.stream({"messages": ["我刚才都问了你什么问题？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;现在可以发现与`Agent`的交互中每次它都能记住之前的消息。然后我们再深入细节了解一下，当添加了检查点后，其中间状态的信息会有什么变化。如下代码所示：

```python
# 文件: 10_2_基于记忆和Check_py
config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream({"messages": ["你好,我叫木羽"]}, config, stream_mode="debug"):
    # print(chunk)
    if chunk["type"] == "checkpoint":

        print(f"Thread id:{chunk['payload']['config']['configurable']['thread_id']}")
        print(f"CheckPoint id :{chunk['payload']['config']['configurable']['checkpoint_id']}")

        for message in chunk['payload']['values']['messages']:
            print(f"Message id:{message.id}，Message content:{message.content}")
      
    # print(f"Task id : {chunk['payload']['id']}")
    # if chunk["type"] == "task":
    #     for message in chunk["payload"]["input"]["messages"]:
    #         print(f"Message id:{message.id}, Message content:{message.content}")

    # if chunk["type"] == "task_result":
    #      print(f"Message id:{chunk['payload']['result'][0][1].id}, Message content:{chunk['payload']['result'][0][1].content}")  # tuple 类型

    print("------------------------------------------------")
    print("------------------------------------------------")
```

&emsp;&emsp;每个`super-step`后，都会生成一个`checkpointer`存储中间信息，而一次交互中，只会存在一个`thread_id`，也就是我们在`config = {"configurable": {"thread_id": "2"}}`中自定义的线程ID，当我们再次使用相同的`thread_id`进行问答时，图在执行前后自动加载该`thread_id`之前存储的所有的信息，添加到新一轮问答的初始状态中，比如下面的代码，我们仍然使用`{"thread_id": "2"}`再次进行交互；

```python
# 文件: 11_2_基于记忆和Check_py
config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream({"messages": ["请问我刚才都问了你什么问题？"]}, config, stream_mode="debug"):
    if chunk["type"] == "checkpoint":
        # print(chunk)
        print(f"Thread id:{chunk['payload']['config']['configurable']['thread_id']}")
        print(f"CheckPoint id :{chunk['payload']['config']['configurable']['checkpoint_id']}")

        for message in chunk['payload']['values']['messages']:
            print(f"Message id:{message.id}，Message content:{message.content}")
      
    # print(f"Task id : {chunk['payload']['id']}")
    # if chunk["type"] == "task":
    #     for message in chunk["payload"]["input"]["messages"]:
    #         print(f"Message id:{message.id}, Message content:{message.content}")

    # if chunk["type"] == "task_result":
    #      print(f"Message id:{chunk['payload']['result'][0][1].id}, Message content:{chunk['payload']['result'][0][1].content}")  # tuple 类型

    print("------------------------------------------------")
    print("------------------------------------------------")
```

&emsp;&emsp;**由此可以印证检查点的机制是：当调用图或完成一个步骤时，其记忆会更新，而如果线程相同，则会在每个步骤开始时读取全部的状态。**如果我们把`thread_id`换成其他的，则会开启全新的一个线程进行对话，比如：

```python
# 文件: 12_2_基于记忆和Check_py
config = {"configurable": {"thread_id": "3"}}

for chunk in graph_with_memory.stream({"messages": ["请问我叫什么？"]}, config, stream_mode="debug"):
    if chunk["type"] == "checkpoint":
        # print(chunk)
        print(f"Thread id:{chunk['payload']['config']['configurable']['thread_id']}")
        print(f"CheckPoint id :{chunk['payload']['config']['configurable']['checkpoint_id']}")

        for message in chunk['payload']['values']['messages']:
            print(f"Message id:{message.id}，Message content:{message.content}")
```

&emsp;&emsp;因为`thread_id`变成了3，所以它是完全不具备`thread_id == 2`这个线程中的任何信息的，但我们可以恢复以前的线程并继续进行对话，即：

```python
# 文件: 13_2_基于记忆和Check_py
config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream({"messages": ["你还知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;**短期记忆可让应用程序记住单个线程或对话中先前的交互，并且可以随时找到某个对话线程中继续之前的问答。**这种情况其实就是我们在使用`Web`端应用程序的时候，可以切回到历史的聊天框继续问答的场景。`LangGraph` 将短期记忆作为代理状态的一部分进行管理，并通过线程范围的检查点进行持久化。此状态通常可以包括对话历史记录以及其他状态数据，例如上传的文件、检索的文档或生成的工件。通过将这些存储在图的状态中，程序可以访问给定对话的完整上下文，同时保持不同线程之间的分离。这就是其现实应用价值的体现。 &emsp;&emsp;那么接下来要考虑的是： 既然所实际进行存储的是 `Checkpointer`， 那么`Checkpointer`如何去做持久化的存储呢？正如我们上面使用的 `MemorySaver`， 虽然在当前的代码运行环境下可以去指定线程ID，获取到具体的历史信息，但是，一旦我们重启代码环境，则所有的数据都将被抹除。那么一种持久化的方法就是把每个`checkpointer`存储到本地的数据库中。

## 2.2 检查点的特定实现类型-SqliteSaver

&emsp;&emsp;`SqliteSaver`是`checkponiter`的第二种实现形式，不同于`MemorySaver`仅通过字典的形式将状态信息存储在当前的运行环境下，`SqliteSaver`做的是持久化存储，这个方法会把`checkponiter`实际的存储在本地的`SQLite` 数据库中，同时提供了异步环境下的实现`AsyncSqliteSaver`，适用于轻量级的应用落地场景。

> https://langchain-ai.github.io/langgraph/reference/checkpoints/?h=memory+saver#langgraph.checkpoint.sqlite.SqliteSaver

&emsp;&emsp;`SqliteSaver`源码定义如下： ```python class SqliteSaver(BaseCheckpointSaver[str]): """A checkpoint saver that stores checkpoints in a SQLite database. Note: This class is meant for lightweight, synchronous use cases (demos and small projects) and does not scale to multiple threads. For a similar sqlite saver with `async` support, consider using [AsyncSqliteSaver][langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver]. Args: conn (sqlite3.Connection): The SQLite database connection. serde (Optional[SerializerProtocol]): The serializer to use for serializing and deserializing checkpoints. Defaults to JsonPlusSerializerCompat. ```

&emsp;&emsp;`SqliteSaver`有两种存储形式，一种是类似于`MemorySaver`将`checkpointer`存储在内存中，另外一种是存储在`sqlite`数据库中。首先来看第一种：

&emsp;&emsp;内存存储（in-Memory Storage）是指存储在计算机主存储器 (RAM) 中的数据，这种类型的存储允许非常快速地访问和检索数据，因为它不涉及磁盘 I/O 操作。这个过程是将`checkpointer`最初保存到内存中，在需要时从内存中进行检索。内部完整的实现思路如下：

- **Step 1. 安装依赖库**

&emsp;&emsp;需要单独安装`langgraph-checkpoint-sqlite`库。

```python
# 文件: 14_2_基于记忆和Check_py
# pip install langgraph-checkpoint-sqlite
```

- **Step 2. 定义内存的存储形式**

&emsp;&emsp;通过`:memory:`方法指定在内存中存储`checkpointer`。代码如下：

```python
# 文件: 15_2_基于记忆和Check_py
from langgraph.checkpoint.sqlite import SqliteSaver

# 创建一个内存中的检查点
memory = SqliteSaver.from_conn_string(":memory:")
```

- **Step 3. 构建checkpointer**

&emsp;&emsp;这里为了演示`SqliteSaver`的执行原理，我们手动构建一个测试的`checkpointer`，其默认实现的是从`State`中进行提取。

```python
# 文件: 16_2_基于记忆和Check_py
checkpoint_data = {
    "thread_id": "muyu123",  
    "thread_ts": "2024-10-30T07:23:38.656547+00:00", 
    "checkpoint": {
        "id": "1ef968fe-1eb4-6049-bfff", 
    },
    "metadata": {"timestamp": "2024-10-30T07:23:38.656547+00:00"}
}
```

- **Step 3. 存储checkpointer**

&emsp;&emsp;在源码中，`from_conn_string`方法使用了`Python`的`contextmanager`装饰器，所以它是一个生成器函数。这个方法创建的实例必须在`with`语句中使用。即我们需要修改其构建的方式，并通过`put`方法进行`checkpointer`配置的写入，代码如下：

```python
# 文件: 17_2_基于记忆和Check_py
with SqliteSaver.from_conn_string(":memory:") as memory:
    # 保存检查点，包括时间戳
    saved_config = memory.put(
        config={"configurable": {"thread_id": checkpoint_data["thread_id"], "thread_ts": checkpoint_data["thread_ts"], "checkpoint_ns": ""}},
        checkpoint=checkpoint_data["checkpoint"],
        metadata=checkpoint_data["metadata"],
        new_versions= {"writes": {"key": "value"}}
    )
```

```python
# 文件: 18_2_基于记忆和Check_py
print(saved_config)
```

&emsp;&emsp;除此之外，还可以通过`list`方法查看到`thread_id`下所有的检查点信息，代码如下：

```python
# 文件: 19_2_基于记忆和Check_py
with SqliteSaver.from_conn_string(":memory:") as memory:
    # 保存检查点，包括时间戳
    saved_config = memory.put(
        config={"configurable": {"thread_id": checkpoint_data["thread_id"], "thread_ts": checkpoint_data["thread_ts"], "checkpoint_ns": ""}},
        checkpoint=checkpoint_data["checkpoint"],
        metadata=checkpoint_data["metadata"],
        new_versions= {"writes": {"key": "value"}}
    )

    # 检索检查点的数据
    config = {"configurable": {"thread_id": checkpoint_data["thread_id"]}}
    
    # 获取给定 thread_id 的所有检查点
    checkpoints = list(memory.list(config))  
    for checkpoint in checkpoints:
        print(checkpoint)
```

&emsp;&emsp;内部原理如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/20241031002.png" width=100%></div>

&emsp;&emsp;除此之外，`SQLiteSaver`还支持持久化存储。这种方式是指存储在非易失性介质上的数据，例如硬盘驱动器、SSD 或云存储，即使应用程序停止或系统断电，这种类型的存储也会保留数据。使用的方式也非常简单，只需要把`from_conn_string`中的`:memory:`更换为指向为本地的`sqlite.db`的文件即可，这允许数据持久保存，便于长期存取。代码如下：

```python
# 文件: 20_2_基于记忆和Check_py
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver 

with SqliteSaver.from_conn_string("checkpoints20241101.sqlite") as memory:
    # 保存检查点，包括时间戳
    saved_config = memory.put(
        config={"configurable": {"thread_id": checkpoint_data["thread_id"], "thread_ts": checkpoint_data["thread_ts"], "checkpoint_ns": ""}},
        checkpoint=checkpoint_data["checkpoint"],
        metadata=checkpoint_data["metadata"],
        new_versions= {"writes": {"key": "value"}}
    )

    # 检索检查点的数据
    config = {"configurable": {"thread_id": checkpoint_data["thread_id"]}}
    
    # 获取给定 thread_id 的所有检查点
    checkpoints = list(memory.list(config))  
    for checkpoint in checkpoints:
        print(checkpoint)
```

&emsp;&emsp;可以使用标准的 `SQL` 语法直接与数据库进行交互。

```python
# 文件: 21_2_基于记忆和Check_py
# 建立数据库连接
conn = sqlite3.connect("checkpoints20241101.sqlite")

# 创建一个游标对象来执行你的SQL查询
cursor = conn.cursor()

# 查询数据库中所有表的名称
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# 获取查询结果
tables = cursor.fetchall()
```

```python
# 文件: 22_2_基于记忆和Check_py
# 打印所有表名
for table in tables:
    print(table)
```

```python
# 文件: 23_2_基于记忆和Check_py
# 从检查点表中检索所有数据
cursor.execute(f"SELECT * FROM checkpoints;")
all_data = cursor.fetchall()

# 打印检查点表中的所有数据
print("Data in the 'checkpoints' table:")
for row in all_data:
    print(row)
```

### 2. 拓展思考

#### 2.1 深度概念

&emsp;&emsp;本节内容涵盖了LangGraph中记忆机制的核心概念，包括短期记忆（通过checkpointer实现）和长期记忆（通过Store实现）。

