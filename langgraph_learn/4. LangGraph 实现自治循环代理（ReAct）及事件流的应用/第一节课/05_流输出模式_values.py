# -*- coding: utf-8 -*-
"""
【案例5】Stream模式之values
============================================

本案例展示LangGraph流输出模式之values

要点：
1. stream_mode="values"的使用
2. 在每个步骤之后流式传输状态的完整值
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

# ============================================================
# 2. 设置API密钥并创建代理
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    if location.lower() in ["beijing", "北京"]:
        return "北京的温度是16度，天气晴朗。"
    else:
        return f"未找到{location}的天气信息。"

tools = [get_weather]
graph = create_react_agent(llm, tools=tools)

# ============================================================
# 3. 定义打印函数
# ============================================================
def print_stream(stream):
    """打印流式输出"""
    for sub_stream in stream:
        print(f"\n=== Step ===")
        message = sub_stream["messages"][-1]
        message.pretty_print()

# ============================================================
# 4. 使用values模式
# ============================================================
print("=" * 50)
print("Stream模式: values")
print("=" * 50)
print("""
values模式说明：
- 在图中的每个步骤之后流式传输状态的完整值
- 会显示完整的messages列表
""")

input_message = {"messages": ["你好，南京现在的天气怎么样？"]}
print("\n--- 执行 ---")
print_stream(graph.stream(input_message, stream_mode="values"))