# -*- coding: utf-8 -*-
"""
【案例1】LangGraph中ReAct的构建原理
============================================

本案例展示LangGraph中ReAct Agent的构建原理

要点：
1. ReAct Agent的核心思想
2. create_react_agent的使用方法
3. 自治循环机制的解释
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

print("=" * 50)
print("LangGraph中ReAct的构建原理")
print("=" * 50)

# ============================================================
# 3. ReAct Agent的核心思想
# ============================================================
print("""
ReAct Agent的核心思想：
1. 大模型在一个while循环中被重复调用
2. 每一步，代理自主决定调用哪些工具及其输入
3. 执行工具后，将输出作为观察结果反馈给大模型
4. 当代理判断不再需要调用更多工具时，循环终止
5. 输出最终结果

create_react_agent接口：
- model: 支持工具调用的LangChain聊天模型
- tools: 工具列表、ToolExecutor 或 ToolNode 实例
- state_schema: 图的状态模式（可选，有默认值）
""")

# ============================================================
# 4. 简单示例
# ============================================================
# 定义一个简单的工具
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    if location.lower() in ["beijing", "北京"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai", "上海"]:
        return "上海的温度是20度，部分多云。"
    else:
        return f"未找到{location}的天气信息。"

tools = [get_weather]

# 创建ReAct代理
graph = create_react_agent(llm, tools=tools)

print(f"\nReAct代理创建成功: {graph}")

# 可视化图结构
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))