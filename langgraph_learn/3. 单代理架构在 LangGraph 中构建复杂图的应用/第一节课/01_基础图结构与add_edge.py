# -*- coding: utf-8 -*-
"""
【案例1】基础图结构与add_edge方法
============================================

本案例展示LangGraph中最基本的图结构构建方式

要点：
1. 使用StateGraph创建图
2. 使用add_edge构建节点之间的边
3. 使用START和END特殊节点
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph

# ============================================================
# 2. 定义节点函数
# ============================================================
def node_a(state):
    """节点A：状态中的x值加1"""
    return {"x": state["x"] + 1}

def node_b(state):
    """节点B：状态中的x值减2"""
    return {"x": state["x"] - 2}

# ============================================================
# 3. 构建图结构
# ============================================================
builder = StateGraph(dict)

# 添加节点
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

# 构建节点之间的边
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 编译图
graph = builder.compile()

# ============================================================
# 4. 可视化图结构
# ============================================================
from IPython.display import Image, display

print("图结构可视化：")
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ============================================================
# 5. 测试图执行
# ============================================================
result = graph.invoke({"x": 10})
print(f"\n执行结果：输入x=10，输出x={result['x']}")