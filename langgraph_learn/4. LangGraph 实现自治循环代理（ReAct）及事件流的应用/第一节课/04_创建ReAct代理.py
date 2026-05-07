# -*- coding: utf-8 -*-
"""
【案例4】使用create_react_agent创建ReAct代理
============================================

本案例展示如何创建完整的ReAct代理

要点：
1. create_react_agent的使用方法
2. 工具列表的准备
3. 代理的测试
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
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    if location.lower() in ["beijing", "北京"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai", "上海"]:
        return "上海的温度是20度，部分多云。"
    else:
        return f"未找到{location}的天气信息。"

@tool
def search_online(query: str) -> str:
    """Search online for information."""
    return f"搜索结果：关于{query}的信息如下..."

tools = [get_weather, search_online]

# ============================================================
# 4. 创建ReAct代理
# ============================================================
graph = create_react_agent(llm, tools=tools)

print("=" * 50)
print("ReAct代理创建成功")
print("=" * 50)
print(f"\n工具数量: {len(tools)}")
print(f"代理类型: {type(graph).__name__}")

# ============================================================
# 5. 可视化图结构
# ============================================================
from IPython.display import Image, display

print("\n--- 图结构 ---")
display(Image(graph.get_graph().draw_mermaid_png()))

# ============================================================
# 6. 测试代理
# ============================================================
print("\n--- 测试1: 普通对话 ---")
result = graph.invoke({"messages": ["你好，请你介绍一下你自己"]})
print(f"用户: 你好，请你介绍一下你自己")
print(f"AI: {result['messages'][-1].content}")

print("\n--- 测试2: 工具调用 ---")
result = graph.invoke({"messages": ["北京现在的天气怎么样？"]})
print(f"用户: 北京现在的天气怎么样？")
print(f"AI: {result['messages'][-1].content}")