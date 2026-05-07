# -*- coding: utf-8 -*-
"""
【案例 3】状态传递与节点通信
============================================

本案例展示如何在 LangGraph 中实现状态在节点间的传递

要点：
1. 节点如何读取状态
2. 节点如何更新状态
3. 中间状态的使用
"""

# ============================================================
# 1. 定义状态
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Optional

class InputState(TypedDict):
    """输入状态"""
    question: str

class OutputState(TypedDict):
    """输出状态"""
    answer: str

class OverallState(InputState, OutputState):
    """合并状态"""
    pass

# ============================================================
# 2. 定义节点 - 节点可以读写状态
# ============================================================
def agent_node(state: InputState):
    """
    Agent 节点：读取 question 字段
    """
    question = state["question"]
    print(f"[Agent] 接收到问题: {question}")

    # 返回的字典会更新状态
    return {
        "question": question  # 保持 question 不变
    }

def action_node(state: InputState):
    """
    Action 节点：基于 question 生成 answer
    """
    question = state["question"]
    answer = f"这是一个关于「{question}」的回答"

    return {"answer": answer}

# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("agent", agent_node)
builder.add_node("action", action_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", "action")
builder.add_edge("action", END)

graph = builder.compile()

# ============================================================
# 4. 执行
# ============================================================
print("=" * 50)
print("案例 3: 状态传递与节点通信")
print("=" * 50)

result = graph.invoke({"question": "什么是人工智能？"})
print(f"\n最终结果: {result}")