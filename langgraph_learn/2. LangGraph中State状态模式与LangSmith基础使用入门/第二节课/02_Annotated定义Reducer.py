"""
02_Annotated定义Reducer
使用Annotated和operator.add定义Reducer，实现列表追加操作
"""
import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import START, StateGraph, END
from IPython.display import Image, display

# 使用Annotated定义状态，指定operator.add作为Reducer
class State(TypedDict):
    messages: Annotated[List[str], operator.add]

# 定义节点函数
def addition(state):
    """处理消息：提取最后一条消息并返回响应"""
    print(state)
    msg = state['messages'][-1]
    response = {"x": msg["x"] + 1}
    return {"messages": [response]}

def subtraction(state):
    """处理消息：提取最后一条消息并返回响应"""
    print(state)
    msg = state['messages'][-1]
    response = {"x": msg["x"] - 2}
    return {"messages": [response]}

# 构建图
builder = StateGraph(State)
builder.add_node("node1", addition)
builder.add_node("node2", subtraction)
builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", END)
graph = builder.compile()

# 可视化图
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 使用不同输入执行图
print("=== 第一次执行 ===")
input_state = {'messages': [{"x": 10}]}
result = graph.invoke(input_state)
print("结果:", result)

print("\n=== 第二次执行 ===")
result = graph.invoke({'messages': [{"x": 32}]})
print("结果:", result)

print("\n=== 第三次执行 ===")
result = graph.invoke({'messages': [{"x": 44}]})
print("结果:", result)

"""
关键点：
1. Annotated[List[str], operator.add] 告诉LangGraph使用添加操作更新messages
2. 每次状态更新时，新消息会被追加到现有列表，而不是覆盖
3. 这样可以保留完整的历史记录
"""