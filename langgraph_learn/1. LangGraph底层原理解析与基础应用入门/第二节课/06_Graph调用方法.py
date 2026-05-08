# -*- coding: utf-8 -*-
"""
【案例6】Graph的编译与调用
============================================

本案例展示如何编译和调用LangGraph。

要点：
1. 使用compile()方法编译图
2. 使用invoke()方法调用图
3. 节点间通过State传递信息
4. 可以写入图状态中的任何状态通道
"""

# ============================================================
# 1. 定义状态和节点
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 合并成更全面的字典类型
class OverallState(InputState, OutputState):
    pass

def agent_node(state: InputState):
    """Agent节点：打印并传递状态"""
    print("我是一个AI Agent。")
    return {"question": state["question"]}

def action_node(state: InputState):
    """Action节点：处理并返回答案"""
    print("我现在是一个执行者。")
    step = state["question"]
    return {"answer": f"我接收到的问题是：{step}，读取成功了！"}

# ============================================================
# 2. 构建图
# ============================================================
# 明确指定输入和输出数据的结构或模式
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("agent_node", agent_node)
builder.add_node("action_node", action_node)

# 添加边
builder.add_edge(START, "agent_node")
builder.add_edge("agent_node", "action_node")
builder.add_edge("action_node", END)

# 编译图
graph = builder.compile()

# ============================================================
# 3. 调用图
# ============================================================
print("调用图测试：")
result = graph.invoke({"question": "今天的天气怎么样？"})
print(f"结果: {result}")
