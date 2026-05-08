"""
01_基础条件路由实现
演示如何使用 add_conditional_edges 实现基础的条件路由
"""
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph
from IPython.display import Image, display

# 定义三个节点函数
def node_a(state):
    return {"x": state["x"] + 1}

def node_b(state):
    return {"x": state["x"] - 2}

def node_c(state):
    return {"x": state["x"] + 1}

# 基础条件路由函数 - 直接返回节点名称
def routing_function(state):
    if state["x"] == 10:
        return "node_b"
    else:
        return "node_c"

# 构建图
builder = StateGraph(dict)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

# 设置入口点
builder.set_entry_point("node_a")

# 添加条件边 - 路由函数返回节点名称
builder.add_conditional_edges("node_a", routing_function)

# 设置结束点
builder.add_edge("node_b", END)
builder.add_edge("node_c", END)

graph = builder.compile()

# 可视化
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))