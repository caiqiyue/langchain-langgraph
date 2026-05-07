# -*- coding: utf-8 -*-
"""
【案例6】Stream模式之updates
============================================

本案例展示LangGraph流输出模式之updates

要点：
1. stream_mode="updates"的使用
2. 在每个步骤之后将更新流式传输到状态
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
# 4. 使用updates模式
# ============================================================
print("=" * 50)
print("Stream模式: updates")
print("=" * 50)
print("""
updates模式说明：
- 在图中的每个步骤之后将更新流式传输到状态
- 如果在同一步骤中进行多个更新，则这些更新将单独流式传输
- 显示的是状态的增量变化，而不是完整状态
""")

input_message = {"messages": ["你好，天津、内蒙现在的天气怎么样？"]}
print("\n--- 执行 ---")
print_stream(graph.stream(input_message, stream_mode="updates"))