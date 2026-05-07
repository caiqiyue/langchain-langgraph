# -*- coding: utf-8 -*-
"""
【案例 6】多节点状态传递
============================================

本案例展示如何在 LangGraph 中实现复杂的多节点状态传递

要点：
1. 中间状态的使用
2. 多个节点间的状态流转
3. Optional 类型的状态字段
"""

# ============================================================
# 1. 定义带中间状态的结构
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
import os
import getpass

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

class InputState(TypedDict):
    """输入状态"""
    question: str
    llm_answer: Optional[str]  # 中间状态：LLM 原始回答

class OutputState(TypedDict):
    """输出状态"""
    answer: str

class OverallState(InputState, OutputState):
    """合并状态"""
    pass

# ============================================================
# 2. 定义多个节点
# ============================================================
def llm_node(state: InputState):
    """
    第一个 LLM 节点 - 回答问题
    """
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)

    return {"llm_answer": response.content}

def translate_node(state: InputState):
    """
    第二个节点 - 翻译回答
    """
    messages = [
        ("system", "无论你接收到什么语言的文本，请翻译成法语"),
        ("human", state["llm_answer"])
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(messages)

    return {"answer": response.content}

# ============================================================
# 3. 构建多节点图
# ============================================================
builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("llm_node", llm_node)
builder.add_node("translate_node", translate_node)

# 连接边
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "translate_node")
builder.add_edge("translate_node", END)

graph = builder.compile()

# ============================================================
# 4. 测试状态传递
# ============================================================
print("=" * 50)
print("案例 6: 多节点状态传递")
print("=" * 50)

result = graph.invoke({"question": "你好，请你详细的介绍一下你自己"})
print(f"问题: 你好，请你详细的介绍一下你自己")
print(f"最终回答（法语）: {result['answer'][:100]}...")

print("\n状态传递说明:")
print("1. question -> llm_node -> llm_answer (中间状态)")
print("2. llm_answer -> translate_node -> answer (输出状态)")