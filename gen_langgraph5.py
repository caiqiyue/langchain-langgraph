# -*- coding: utf-8 -*-
"""
Script to generate course 5 files
"""

import os

base5 = "E:/langchain_learning/langgraph_learn/5. LangGrah 长短期记忆实现机制及检查点的使用/第一节课"
os.makedirs(base5, exist_ok=True)
os.makedirs(base5 + "/assets", exist_ok=True)

# ===== Course 5 Python File 1: Checkpointer =====
py1 = '''# -*- coding: utf-8 -*-
"""
【案例 1】LangGraph 短期记忆与 Checkpointer
============================================

本案例展示 LangGraph 短期记忆的实现机制，包括：
- State 状态模式在单次运行与跨次运行中的行为差异
- MemorySaver 内存检查点的使用
- SqliteSaver 本地持久化检查点
- ReAct 代理与 checkpointer 的集成

要点：
1. State 状态模式仅在单次运行内有效，跨次运行会重置
2. checkpointer 通过 thread_id 管理不同会话的状态持久化
3. MemorySaver 适合实验，SqliteSaver 适合轻量级生产
4. ExitStack 管理 SqliteSaver 跨 notebook cell 的生命周期
"""

# ============================================================
# 1. 问题引入：State 状态不跨次运行
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": response}

builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)
simple_graph = builder.compile()

# 测试：多轮问答发现图不具备上下文记忆能力
async for chunk in simple_graph.astream(
    input={"messages": ["你好，我叫木羽"]},
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

async for chunk in simple_graph.astream(
    input={"messages": ["你知道我叫什么吗？"]},
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

# 结论：每次调用都是"新图"，State 仅在单次运行内有效


# ============================================================
# 2. 图执行流程的 Debug 分析
# ============================================================
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

builder = StateGraph(State)
builder.add_node("call_model", call_model)

# 添加翻译节点：call_model -> translate_message -> END
def translate_message(state: State):
    from langchain_core.messages import SystemMessage
    system_prompt = "Please translate the received text into English."
    messages = state["messages"][-1]
    response = llm.invoke([SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)])
    return {"messages": response}

builder.add_node("translate_message", translate_message)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "translate_message")
builder.add_edge("translate_message", END)
simple_short_graph = builder.compile()

# Debug 模式观察 task id 和 message id
async for chunk in simple_short_graph.astream(
    {"messages": ["你好，我叫木羽"]},
    stream_mode="debug"
):
    print(f"Task id: {chunk[\'payload\'][\'id\']}")
    if chunk["type"] == "task":
        for message in chunk["payload"]["input"]["messages"]:
            print(f"Message id: {message.id}, Content: {message.content}")
    if chunk["type"] == "task_result":
        print(f"Result id: {chunk[\'payload\'][\'result\'][0][1].id}, Content: {chunk[\'payload\'][\'result\'][0][1].content}")
    print("-" * 40)


# ============================================================
# 3. Checkpointer 的核心概念
# ============================================================
"""
checkpointer 通过以下方式实现记忆：
1. 在每个 super-step 后保存 State 状态的 checkpoint
2. 通过 thread_id 标识不同会话线程
3. 新一轮执行时自动加载该 thread_id 的历史状态

四种 checkpointer 实现：
- MemorySaver：实验性质，内存存储
- SqliteSaver / AsyncSqliteSaver：SQLite 数据库，轻量级
- PostgresSaver / AsyncPostgresSaver：Postgres 数据库，生产级
- 支持自定义检查点
"""


# ============================================================
# 4. MemorySaver 实战
# ============================================================
from langgraph.checkpoint.memory import MemorySaver

llm = ChatOpenAI(model="gpt-4o")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": response}

builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

memory = MemorySaver()
graph_with_memory = builder.compile(checkpointer=memory)

# 可视化
display(Image(graph_with_memory.get_graph().draw_mermaid_png()))

# ！！！关键：使用 thread_id 调用图
config = {"configurable": {"thread_id": "1"}}

# 第一轮问答
for chunk in graph_with_memory.stream(
    {"messages": ["你好，我叫木羽"]},
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

# 第二轮问答（使用相同 thread_id，自动携带历史上下文）
for chunk in graph_with_memory.stream(
    {"messages": ["请问我叫什么？"]},
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


# ============================================================
# 5. Debug 模式观察检查点的创建与加载
# ============================================================
config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream(
    {"messages": ["你好，我叫木羽"]},
    config,
    stream_mode="debug"
):
    if chunk["type"] == "checkpoint":
        print(f"Thread id: {chunk[\'payload\'][\'config\'][\'configurable\'][\'thread_id\']}")
        print(f"CheckPoint id: {chunk[\'payload\'][\'config\'][\'configurable\'][\'checkpoint_id\']}")
        for message in chunk["payload"]["values"]["messages"]:
            print(f"Message id: {message.id}，Content: {message.content}")
    print("-" * 40)


# ============================================================
# 6. 新线程（thread_id）不携带历史信息
# ============================================================
config_new = {"configurable": {"thread_id": "3"}}

for chunk in graph_with_memory.stream(
    {"messages": ["请问我叫什么？"]},
    config_new,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

# 恢复旧线程
config_old = {"configurable": {"thread_id": "2"}}
for chunk in graph_with_memory.stream(
    {"messages": ["你还知道我叫什么吗？"]},
    config_old,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


# ============================================================
# 7. SqliteSaver 内存模式
# ============================================================
# pip install langgraph-checkpoint-sqlite

from langgraph.checkpoint.sqlite import SqliteSaver

# 内存模式（重启后数据丢失）
with SqliteSaver.from_conn_string(":memory:") as memory:
    saved_config = memory.put(
        config={"configurable": {"thread_id": "test123", "thread_ts": "2024-10-30T07:23:38", "checkpoint_ns": ""}},
        checkpoint={"id": "checkpoint-001"},
        metadata={"timestamp": "2024-10-30T07:23:38"},
        new_versions={"writes": {"key": "value"}}
    )
    print("Saved config:", saved_config)

    # 检索所有检查点
    checkpoints = list(memory.list({"configurable": {"thread_id": "test123"}}))
    for cp in checkpoints:
        print(cp)


# ============================================================
# 8. SqliteSaver 持久化模式
# ============================================================
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

with SqliteSaver.from_conn_string("checkpoints.sqlite") as memory:
    saved_config = memory.put(
        config={"configurable": {"thread_id": "muyu123", "thread_ts": "2024-10-30T07:23:38", "checkpoint_ns": ""}},
        checkpoint={"id": "1ef968fe-1eb4-6049-bfff"},
        metadata={"timestamp": "2024-10-30T07:23:38"}
    )
    checkpoints = list(memory.list({"configurable": {"thread_id": "muyu123"}}))
    for cp in checkpoints:
        print(cp)

# 直接查询 SQLite 数据库
conn = sqlite3.connect("checkpoints.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

cursor.execute("SELECT * FROM checkpoints;")
for row in cursor.fetchall():
    print("Row:", row)
conn.close()


# ============================================================
# 9. ReAct 代理 + checkpointer（跨 cell 传播）
# ============================================================
from contextlib import ExitStack
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent

stack = ExitStack()
checkpointer = stack.enter_context(SqliteSaver.from_conn_string(":memory:"))

llm = ChatOpenAI(model="gpt-4o")
tools = [get_weather]  # 需提前定义 get_weather 工具

graph = create_react_agent(llm, tools=tools, checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

for chunk in graph.stream({"messages": ["你好，我叫木羽"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

for chunk in graph.stream({"messages": ["请问我叫什么？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

for chunk in graph.stream({"messages": ["帮我查一下北京的天气"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

for chunk in graph.stream({"messages": ["请问我刚才问了什么问题？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

stack.close()
'''

with open(base5 + "/01_Checkpointer短期记忆机制.py", "w", encoding="utf-8") as f:
    f.write(py1)
print("Written: 01_Checkpointer短期记忆机制.py")


# ===== Course 5 Python File 2: Store (Long-term Memory) =====
py2 = '''# -*- coding: utf-8 -*-
"""
【案例 2】LangGraph 长期记忆与 Store
============================================

本案例展示 LangGraph 的长期记忆实现机制：
- InMemoryStore 跨线程共享记忆
- Store 与 Checkpointer 协同工作
- 自定义 namespace 管理不同用户/场景的记忆

要点：
1. checkpointer 通过 thread_id 管理会话内记忆（短期记忆）
2. Store 通过自定义 namespace 跨线程共享信息（长期记忆）
3. InMemoryStore + MemorySaver 组合使用
4. 节点函数通过 store 关键字参数访问 Store
"""

# ============================================================
# 1. 为什么需要 Store
# ============================================================
"""
仅使用 checkpointer，我们无法跨线程共享信息。
Store 使用自定义 namespace 来组织数据，不依赖 thread_id。
常见用例：存储用户配置文件、构建知识库、管理全局首选项。
"""

# ============================================================
# 2. InMemoryStore 基础使用
# ============================================================
from langgraph.store.memory import InMemoryStore
import uuid

in_memory_store = InMemoryStore()

# namespace：tuple 类型，类似文件夹路径
user_id = "1"
namespace_for_memory = (user_id, "memories")

# 存储记忆
memory_id = str(uuid.uuid4())
memory = {"user": "你好，我叫木羽"}
in_memory_store.put(namespace_for_memory, memory_id, memory)

# 检索记忆
memories = in_memory_store.search(namespace_for_memory)
print("记忆内容:", memories[-1].dict())


# ============================================================
# 3. 完整示例：ReAct 代理 + Checkpointer + Store
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
import uuid

# 初始化 store 和 checkpointer
in_memory_store = InMemoryStore()
memory = MemorySaver()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")


class State(TypedDict):
    messages: Annotated[list, add_messages]


# 定义对话节点：访问记忆并在模型调用中使用它们
def call_model(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    # 获取用户 id
    user_id = config["configurable"]["user_id"]

    # 定义命名空间
    namespace = ("memories", user_id)

    # 根据用户 id 检索记忆
    memories = store.search(namespace)
    info = "\\n".join([d.value["data"] for d in memories])

    # 获取最新消息
    last_message = state["messages"][-1]
    store.put(namespace, str(uuid.uuid4()), {"data": last_message.content})

    system_msg = f"Answer the user\\'s question in context: {info}"

    response = llm.invoke(
        [{"type": "system", "content": system_msg}] + state["messages"]
    )

    # 存储响应到记忆
    store.put(namespace, str(uuid.uuid4()), {"data": response.content})
    return {"messages": response}


# 构建状态图
builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

# 编译图：同时传入 checkpointer 和 store
graph = builder.compile(checkpointer=memory, store=in_memory_store)

# 可视化
display(Image(graph.get_graph().draw_mermaid_png()))


# ============================================================
# 4. 测试：同用户 + 同线程（延续对话）
# ============================================================
config1 = {"configurable": {"thread_id": "10", "user_id": "6"}}

async for chunk in graph.astream(
    {"messages": ["你好，我是木羽"]},
    config1,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()

async for chunk in graph.astream(
    {"messages": ["你知道我叫什么吗？"]},
    config1,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


# ============================================================
# 5. 测试：同用户 + 新线程（跨线程共享记忆）
# ============================================================
# user_id 相同（6），但 thread_id 不同（11）
config2 = {"configurable": {"thread_id": "11", "user_id": "6"}}

async for chunk in graph.astream(
    {"messages": ["你知道我叫什么吗？"]},
    config2,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


# ============================================================
# 6. 测试：新用户（无历史记忆）
# ============================================================
config3 = {"configurable": {"thread_id": "18", "user_id": "8"}}

async for chunk in graph.astream(
    {"messages": ["你知道我叫什么吗？"]},
    config3,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()


# ============================================================
# 7. 直接访问 Store 查看存储的记忆
# ============================================================
# 查看 user_id=6 的所有记忆
for mem in in_memory_store.search(("memories", "6")):
    print("user 6 记忆:", mem.value)

# 查看 user_id=8 的所有记忆
for mem in in_memory_store.search(("memories", "8")):
    print("user 8 记忆:", mem.value)


# ============================================================
# 8. 异步版本的 Store（AsyncSqliteSaver + astream_events）
# ============================================================
import asyncio
from contextlib import AsyncExitStack
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async def run_async_example():
    stack = AsyncExitStack()
    checkpointer = await stack.enter_async_context(
        AsyncSqliteSaver.from_conn_string(":memory:")
    )

    graph = create_react_agent(llm, tools=[get_weather], checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "24"}}

    async for chunk in graph.astream(
        {"messages": ["帮我查一下北京的天气"]},
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

    async for chunk in graph.astream(
        {"messages": ["我刚才问了你什么问题"]},
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

    await stack.aclose()

# asyncio.run(run_async_example())
'''

with open(base5 + "/02_Store长期记忆机制.py", "w", encoding="utf-8") as f:
    f.write(py2)
print("Written: 02_Store长期记忆机制.py")

print("Course 5 Python files done")
