"""
01_MessageGraph基础
演示MessageGraph的基本用法
MessageGraph是StateGraph的子类，专门用于以消息为中心的工作流程
"""
import getpass
import os
from langchain_openai import ChatOpenAI

# 设置OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# 使用State类型提示
from langgraph.graph.message import MessageGraph

# 创建MessageGraph
builder = MessageGraph()

# 添加节点
builder.add_node("chatbot", lambda state: [("assistant", "你好，最帅气的人！")])

# 设置入口点和结束点
builder.set_entry_point("chatbot")
builder.set_finish_point("chatbot")

# 编译图
graph = builder.compile()

# 执行图
print("=== 第一次执行 ===")
result = graph.invoke([("user", "你好，请你介绍一下你自己.")])
print("结果:", result)

print("\n=== 第二次执行 ===")
result = graph.invoke([("user", "Hi 3213.")])
print("结果:", result)

"""
MessageGraph特点：
1. 使用单个仅附加消息列表作为其整个状态
2. 每个节点处理该列表并可以返回其他消息
3. 适合对话式应用程序，可以轻松跟踪对话历史和交互
"""