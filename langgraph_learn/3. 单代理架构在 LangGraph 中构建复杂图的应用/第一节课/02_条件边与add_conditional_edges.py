# -*- coding: utf-8 -*-
"""
【案例2】条件边与add_conditional_edges方法
============================================

本案例展示如何使用条件边实现动态路由

要点：
1. add_conditional_edges的使用方法
2. 路由函数(routing_function)的定义
3. path_map参数的使用
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph
from IPython.display import Image, display

# ============================================================
# 2. 定义节点函数
# ============================================================
def node_a(state):
    """节点A：状态中的x值加1"""
    return {"x": state["x"] + 1}

def node_b(state):
    """节点B：状态中的x值减2"""
    return {"x": state["x"] - 2}

def node_c(state):
    """节点C：状态中的x值加1"""
    return {"x": state["x"] + 1}

# ============================================================
# 3. 定义路由函数
# ============================================================
def routing_function(state):
    """
    路由函数：根据x的值决定下一个节点
    如果x等于10，路由到node_b，否则路由到node_c
    """
    if state["x"] == 10:
        return "node_b"
    else:
        return "node_c"

# ============================================================
# 4. 构建带条件边的图结构
# ============================================================
builder = StateGraph(dict)

# 添加节点
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

builder.set_entry_point("node_a")

# 构建条件边
builder.add_conditional_edges("node_a", routing_function)

# 设置终止节点
builder.add_edge("node_b", END)
builder.add_edge("node_c", END)

# 编译图
graph = builder.compile()

# ============================================================
# 5. 可视化图结构
# ============================================================
print("带条件边的图结构：")
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ============================================================
# 6. 测试不同输入的路由结果
# ============================================================
# 测试x=10的情况
result1 = graph.invoke({"x": 10})
print(f"\n输入x=10时，执行node_a后x=11，路由到node_b，x-2={result1['x']}")

# 测试x!=10的情况
result2 = graph.invoke({"x": 5})
print(f"输入x=5时，执行node_a后x=6，路由到node_c，x+1={result2['x']}")