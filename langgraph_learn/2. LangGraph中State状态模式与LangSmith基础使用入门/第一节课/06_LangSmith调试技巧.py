# -*- coding: utf-8 -*-
"""
【案例 6】LangSmith 调试技巧
============================================

本案例展示如何利用 LangSmith 调试 LangGraph 应用

要点：
1. 使用 verbose 查看本地日志
2. LangSmith 云端追踪
3. 检查点（Checkpoints）功能
"""

# ============================================================
# 1. 基础配置
# ============================================================
import os
import getpass

# LangSmith 配置
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
os.environ["LANGSMITH_PROJECT"] = "langgraph-debug"

# ============================================================
# 2. 构建可调试的图
# ============================================================
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class OverallState(MessagesState):
    """带消息的历史状态"""
    pass

def chat_node(state: OverallState):
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(OverallState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

# ============================================================
# 3. 使用 MemorySaver 实现检查点
# ============================================================
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# ============================================================
# 4. 测试检查点功能
# ============================================================
print("=" * 50)
print("案例 6: LangSmith 调试与检查点")
print("=" * 50)

from langchain_core.messages import HumanMessage

# 第一次对话
config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke(
    {"messages": [HumanMessage(content="我叫张三")]},
    config=config
)
print(f"第一次调用完成")

# 第二次对话（可以访问之前的状态）
result2 = graph.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config=config
)
print(f"第二次调用完成")
print(f"回答: {result2['messages'][-1].content}")