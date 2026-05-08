"""
02_State定义模式
使用TypedDict定义State状态，获得更好的类型约束和代码提示
"""
from typing_extensions import TypedDict
from langgraph.graph import START, StateGraph, END

# 使用TypedDict定义状态模式，精确控制状态信息的格式和类型
class State(TypedDict):
    x: int
    y: int

# 定义节点函数
def addition(state):
    """加法逻辑：接收当前状态，将字典中x的值增加1"""
    print(state)
    return {"x": state["x"] + 1}

def subtraction(state):
    """减法逻辑：从字典中的x值减去2，创建并返回一个新的键y"""
    print(state)
    return {"y": state["x"] - 2}

# 构建图
builder = StateGraph(State)

# 向图中添加两个节点
builder.add_node("addition", addition)
builder.add_node("subtraction", subtraction)

# 构建节点之间的边
builder.add_edge(START, "addition")
builder.add_edge("addition", "subtraction")
builder.add_edge("subtraction", END)

# 编译图
graph = builder.compile()

# 定义初始状态并执行
initial_state = {"x": 10}
result = graph.invoke(initial_state)
print("执行结果:", result)