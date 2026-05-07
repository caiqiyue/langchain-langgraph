# -*- coding: utf-8 -*-
"""
【案例 4】Nodes 节点与 Edges 边
============================================

本案例展示如何在 LangGraph 中定义和使用节点与边

要点：
1. 节点是接收 State 并返回更新的 State 的 Python 函数
2. 边的类型：普通边、条件边、入口点、结束点
3. START 和 END 特殊节点
"""

# ============================================================
# 1. 节点定义
# ============================================================
from typing_extensions import TypedDict

class InputState(TypedDict):
    """输入状态定义"""
    question: str

class OutputState(TypedDict):
    """输出状态定义"""
    answer: str

class OverallState(InputState, OutputState):
    """合并输入输出状态"""
    pass

def agent_node(state: InputState):
    """
    Agent 节点 - 接收输入，决定操作
    """
    print("我是一个AI Agent。")
    return {"question": state["question"]}

def action_node(state: InputState):
    """
    Action 节点 - 执行具体操作
    """
    print("我现在是一个执行者。")
    step = state["question"]
    return {"answer": f"我接收到的问题是：{step}，读取成功了！"}

# ============================================================
# 2. 构建 StateGraph
# ============================================================
from langgraph.graph import StateGraph, START, END

# 创建状态图
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)

# ============================================================
# 3. 添加边
# ============================================================
# 普通边：直接从一个节点到下一个节点
builder.add_edge(START, "agent_node")      # 设置入口点
builder.add_edge("agent_node", "action_node")  # agent -> action
builder.add_edge("action_node", END)       # 设置结束点

# 编译图
graph = builder.compile()

# ============================================================
# 4. 调用图
# ============================================================
print("=" * 50)
print("案例 4: Nodes 节点与 Edges 边")
print("=" * 50)

result = graph.invoke({"question": "今天的天气怎么样？"})
print(f"结果: {result}")

print("\n边类型说明:")
print("- 普通边: add_edge() 直接连接节点")
print("- 条件边: add_conditional_edges() 根据条件决定路径")
print("- START: 用户输入入口")
print("- END: 终止节点")