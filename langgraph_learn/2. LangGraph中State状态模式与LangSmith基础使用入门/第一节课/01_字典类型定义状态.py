"""
01_字典类型定义状态
演示使用字典类型(dict)定义LangGraph中的State状态
"""
from langgraph.graph import StateGraph

# 构建图 - 使用dict作为状态类型
builder = StateGraph(dict)

# 查看状态模式
print("状态模式:", builder.schema)

# 定义节点函数
def addition(state):
    """加法逻辑：接收当前状态，将字典中x的值增加1"""
    print(state)
    return {"x": state["x"] + 1}

def subtraction(state):
    """减法逻辑：从字典中的x值减去2，创建并返回一个新的键y"""
    print(state)
    return {"y": state["x"] - 2}

# 向图中添加两个节点
builder.add_node("addition", addition)
builder.add_node("subtraction", subtraction)

# 构建节点之间的边
from langgraph.graph import START, END
builder.add_edge(START, "addition")
builder.add_edge("addition", "subtraction")
builder.add_edge("subtraction", END)

# 查看图的边和节点
print("图的边:", builder.edges)
print("图的节点:", builder.nodes)
print("状态模式:", builder.schema)

# 编译图
graph = builder.compile()

# 定义初始状态并执行
initial_state = {"x": 10}
result = graph.invoke(initial_state)
print("执行结果:", result)