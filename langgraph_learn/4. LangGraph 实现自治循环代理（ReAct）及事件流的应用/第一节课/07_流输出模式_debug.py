# -*- coding: utf-8 -*-
"""
【案例7】Stream模式之debug
============================================

本案例展示LangGraph流输出模式之debug

要点：
1. stream_mode="debug"的使用
2. 在整个图的执行过程中流式传输尽可能多的信息
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
        print(sub_stream)

# ============================================================
# 4. 使用debug模式
# ============================================================
print("=" * 50)
print("Stream模式: debug")
print("=" * 50)
print("""
debug模式说明：
- 在整个图的执行过程中流式传输尽可能多的信息
- 主要用于调试程序
- 会显示详细的技术信息
""")

input_message = {"messages": ["你好，天津现在的天气怎么样？"]}
print("\n--- 执行 ---")
print_stream(graph.stream(input_message, stream_mode="debug"))