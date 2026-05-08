# -*- coding: utf-8 -*-
"""
【案例4】Nodes节点定义与添加
============================================

本案例展示如何在LangGraph中定义和添加节点。

要点：
1. 节点是一个Python函数（sync或async）
2. 接收当前State作为输入
3. 执行自定义计算并返回更新的State
4. 使用add_node方法添加节点到图中
"""

# ============================================================
# 1. 安装依赖
# ============================================================
# ! pip install langgraph==0.2.35

# ============================================================
# 2. 定义节点函数
# ============================================================
from typing import TypedDict

class InputState(TypedDict):
    question: str

def agent_node(state: InputState):
    """Agent节点：打印消息并返回"""
    print("我是一个AI Agent。")
    return

def action_node(state: InputState):
    """Action节点：打印消息并返回答案"""
    print("我现在是一个执行者。")
    return {"answer": "我现在执行成功了"}

# ============================================================
# 3. 创建StateGraph并添加节点
# ============================================================
from langgraph.graph import StateGraph

# 创建StateGraph
builder = StateGraph(InputState)

# 添加节点
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)

print("节点已添加到图中：")
print("- agent_node: AI代理节点")
print("- action_node: 执行者节点")
