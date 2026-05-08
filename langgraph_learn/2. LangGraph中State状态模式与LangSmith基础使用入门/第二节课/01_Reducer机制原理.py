"""
01_Reducer机制原理
演示LangGraph中Reducer函数的基本原理
默认情况下，如果没有显式指定Reducer，对键的所有更新执行的是覆盖操作
"""
from typing_extensions import TypedDict
from langgraph.graph import START, StateGraph, END

# 使用TypedDict定义状态模式
class State(TypedDict):
    x: int
    y: int

# 定义节点函数 - 每次更新只返回x或y
def addition(state):
    """加法逻辑：只更新x"""
    print(state)
    return {"x": state["x"] + 1}

def subtraction(state):
    """减法逻辑：只更新y"""
    print(state)
    return {"y": state["x"] - 2}

# 构建图
builder = StateGraph(State)
builder.add_node("addition", addition)
builder.add_node("subtraction", subtraction)
builder.add_edge(START, "addition")
builder.add_edge("addition", "subtraction")
builder.add_edge("subtraction", END)
graph = builder.compile()

# 定义初始状态并执行
initial_state = {"x": 10}
result = graph.invoke(initial_state)
print("执行结果:", result)

"""
运行结果分析：
1. 初始状态: {"x": 10}
2. addition节点执行: 返回 {"x": 11}，状态更新为 {"x": 11}
3. subtraction节点执行: 返回 {"y": 9}，状态更新为 {"x": 11, "y": 9}

注意：由于没有指定Reducer，默认使用覆盖操作
每个节点返回的更新会覆盖之前的状态
"""