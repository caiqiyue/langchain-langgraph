"""
02_集成LangSmith监控
演示如何将LangSmith集成到LangGraph应用中，实现实时监控
"""
import getpass
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key-here"  # 替换为你的API密钥

# 设置OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 创建图
graph_builder = StateGraph(State)

# 初始化大模型
llm = ChatOpenAI(model="gpt-4o")

# 定义chatbot节点
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 添加节点和边
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 编译图
graph = graph_builder.compile()

# 交互式聊天函数
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("模型回复:", value["messages"][-1].content)

# 运行示例
print("=== LangSmith集成示例 ===")
user_input = "What do you know about LangGraph?"
print("User:", user_input)
stream_graph_updates(user_input)

"""
LangSmith监控功能：
1. 实时可视化应用程序执行过程中各个状态的输入和输出
2. 跟踪是请求通过图逻辑的步骤的详细记录
3. 每次用户与程序进行交互时，图的每个步骤都会记录为跟踪的一部分

LangSmith核心概念：
- Project (项目)：蓝色方块代表整个项目
- Traces (轨迹)：绿色方块代表项目的执行路径
- Runs (运行)：黄色方块表示特定轨迹的单次执行
- Feedback, Tags, Metadata：反馈、标签、元数据用于增强轨迹管理
"""