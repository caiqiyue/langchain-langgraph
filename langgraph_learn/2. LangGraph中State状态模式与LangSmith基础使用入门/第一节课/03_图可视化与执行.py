"""
03_图可视化与执行
演示LangGraph的三种可视化方法以及图的执行
"""
# 安装依赖
# ! pip install pyppeteer ipython

from IPython.display import Image, display
from typing_extensions import TypedDict
from langgraph.graph import START, StateGraph, END

# 使用TypedDict定义状态模式
class State(TypedDict):
    x: int
    y: int

# 定义节点函数
def addition(state):
    """加法逻辑"""
    print(state)
    return {"x": state["x"] + 1}

def subtraction(state):
    """减法逻辑"""
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

# 使用Mermaid + Pyppeteer进行可视化
# Windows系统建议使用此方法
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 执行图
initial_state = {"x": 10}
result = graph.invoke(initial_state)
print("执行结果:", result)

"""
LangGraph提供的三种图形可视化方法：
1. Mermaid.Ink - 开源服务，通过API生成PNG、JPEG、SVG和PDF
2. Mermaid + Pyppeteer - 通过浏览器自动截图生成图像
3. Graphviz - 适合复杂图形生成，有更精细的布局控制

Windows系统建议使用Mermaid + Pyppeteer方法
"""