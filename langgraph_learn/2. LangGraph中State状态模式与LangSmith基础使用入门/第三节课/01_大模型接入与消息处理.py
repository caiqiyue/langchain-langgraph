"""
01_大模型接入与消息处理
演示如何将大模型接入LangGraph工作流程，实现动态消息处理
"""
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from IPython.display import Image, display
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 设置OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model='gpt-4o')

# 定义图的状态模式
class State(TypedDict):
    messages: Annotated[List[str], operator.add]

# 创建图的实例
builder = StateGraph(State)

def chat_with_model(state):
    """与大模型对话的节点"""
    print(state)
    print("-----------------")
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

def convert_messages(state):
    """将消息转换为JSON格式的节点"""
    EXTRACTION_PROMPT = """
    You are a data extraction specialist tasked with retrieving key information from a text.
    Extract such information for the provided text and output it in JSON format.
    """
    print(state)
    print("-----------------")
    messages = state['messages']
    messages = messages[-1]

    messages = [
        SystemMessage(content=EXTRACTION_PROMPT),
        HumanMessage(content=state['messages'][-1].content)
    ]

    response = llm.invoke(messages)
    return {"messages": [response]}

# 添加节点
builder.add_node("chat_with_model", chat_with_model)
builder.add_node("convert_messages", convert_messages)

# 设置启动点
builder.set_entry_point("chat_with_model")

# 添加边
builder.add_edge("chat_with_model", "convert_messages")
builder.add_edge("convert_messages", END)

# 编译图
graph = builder.compile()

# 可视化图
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 执行图
query = "你好，请你介绍一下你自己"
input_message = {"messages": [HumanMessage(content=query)]}

result = graph.invoke(input_message)
print("\n=== 最终结果 ===")
print(result["messages"][-1].content)

"""
关键点：
1. 使用Annotated[List[str], operator.add]定义messages键
2. 每次状态更新时，新消息会被追加到现有列表
3. 节点函数返回的是包含AIMessage的字典
4. LangGraph自动处理消息的合并和维护
"""