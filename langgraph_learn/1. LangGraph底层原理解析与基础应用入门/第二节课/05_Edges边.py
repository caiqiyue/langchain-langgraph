# -*- coding: utf-8 -*-
"""
【案例5】Edges边类型与使用
============================================

本案例展示LangGraph中的边类型。

要点：
1. 普通边：直接从一个节点到下一个节点
2. 条件边：根据条件决定下一个节点
3. 入口点：用户输入首先调用的节点
4. 条件入口点：根据条件决定起始节点
5. START和END是LangGraph的两个特殊节点
"""

# ============================================================
# 1. 定义节点
# ============================================================
from typing import TypedDict
from langgraph.graph import StateGraph

class InputState(TypedDict):
    question: str

def agent_node(state: InputState):
    print("我是一个AI Agent。")
    return

def action_node(state: InputState):
    print("我现在是一个执行者。")
    return {"answer": "我现在执行成功了"}

# ============================================================
# 2. 创建StateGraph并添加节点
# ============================================================
builder = StateGraph(InputState)
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)

# ============================================================
# 3. 添加边
# ============================================================
from langgraph.graph import START, END

# 添加普通边
# START是一个特殊节点，表示用户输入
# END是一个特殊节点，表示终端节点
builder.add_edge(START, "agent_node")           # 入口点 -> agent_node
builder.add_edge("agent_node", "action_node")   # agent_node -> action_node
builder.add_edge("action_node", END)            # action_node -> 结束

print("边类型：")
print("1. 普通边：直接从一个节点到下一个节点")
print("2. 条件边：根据条件决定下一个节点")
print("3. 入口点(START)：用户输入首先调用的节点")
print("4. 条件入口点：根据条件决定起始节点")
print("")
print("已添加的边：")
print("- START -> agent_node")
print("- agent_node -> action_node")
print("- action_node -> END")
