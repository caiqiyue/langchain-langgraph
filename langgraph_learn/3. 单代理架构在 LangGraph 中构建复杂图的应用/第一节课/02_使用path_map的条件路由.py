"""
02_使用path_map的条件路由
演示如何使用 path_map 参数通过布尔值映射到目标节点
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

# 条件路由函数 - 返回布尔值
def routing_function(state):
    if state["x"] == 10:
        return True
    else:
        return False

# 构建图
builder = StateGraph(dict)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

# 设置入口点
builder.set_entry_point("node_a")

# 添加条件边 - 使用 path_map 映射布尔值到节点名称
builder.add_conditional_edges("node_a", routing_function, {True: "node_b", False: "node_c"})

# 设置结束点
builder.add_edge("node_b", END)
builder.add_edge("node_c", END)

graph = builder.compile()

# 可视化
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))