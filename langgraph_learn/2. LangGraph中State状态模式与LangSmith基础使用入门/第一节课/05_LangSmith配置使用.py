# -*- coding: utf-8 -*-
"""
【案例 5】LangSmith 基础配置与使用
============================================

本案例展示如何配置和使用 LangSmith 进行 LangGraph 应用的追踪

要点：
1. LangSmith 环境配置
2. 在 compile 时集成 LangSmith
3. 查看追踪结果
"""

# ============================================================
# 1. LangSmith 环境配置
# ============================================================
import os
import getpass

# 设置 LangSmith API Key
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
os.environ["LANGSMITH_PROJECT"] = "langgraph-course"  # 项目名称

# ============================================================
# 2. LangGraph with LangSmith
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(InputState, OutputState):
    pass

def llm_node(state: InputState):
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    messages = [("human", state["question"])]
    response = llm.invoke(messages)
    return {"answer": response.content}

builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("llm", llm_node)
builder.add_edge(START, "llm")
builder.add_edge("llm", END)

# ============================================================
# 3. 编译图（LangSmith 自动集成）
# ============================================================
graph = builder.compile()

# ============================================================
# 4. 测试（会自动发送到 LangSmith）
# ============================================================
print("=" * 50)
print("案例 5: LangSmith 追踪")
print("=" * 50)
print("LangSmith 已配置完成")
print("访问 https://smith.langchain.com 查看追踪结果")
print("\n执行测试调用...")

result = graph.invoke({"question": "LangSmith是什么？"})
print(f"\n执行完成，查看 LangSmith 控制台获取详细信息")