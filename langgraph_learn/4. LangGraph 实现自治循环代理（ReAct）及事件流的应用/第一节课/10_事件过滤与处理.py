# -*- coding: utf-8 -*-
"""
【案例10】事件过滤与自定义处理
============================================

本案例展示如何过滤事件并自定义处理

要点：
1. 按事件类型过滤
2. 按事件名称过滤
3. 自定义数据处理
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import AIMessageChunk, HumanMessage

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
# 3. 事件过滤示例
# ============================================================
import asyncio

async def filter_events():
    """过滤特定事件"""
    print("=" * 50)
    print("事件过滤")
    print("=" * 50)

    print("\n--- 只打印聊天模型流 ---")

    async for event in graph.astream_events(
        {"messages": ["你好，北京的天气怎么样？"]},
        version="v2"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            print(f"事件: {kind}")
            print(f"数据: {event['data']}")

asyncio.run(filter_events())

# ============================================================
# 4. 自定义数据处理
# ============================================================
async def custom_processing():
    """自定义数据处理"""
    print("\n" + "=" * 50)
    print("自定义数据处理")
    print("=" * 50)

    print("\n--- 提取聊天模型输出的内容 ---")

    async for event in graph.astream_events(
        {"messages": ["你好，请你介绍一下你自己"]},
        version="v2"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            # 提取content
            content = event["data"]["chunk"].content
            if content:
                print(content, end="|", flush=True)

    print("\n")

asyncio.run(custom_processing())

# ============================================================
# 5. 完整的Token处理示例
# ============================================================
async def token_processing():
    """完整的Token处理"""
    print("\n" + "=" * 50)
    print("完整Token处理")
    print("=" * 50)

    first = True
    gathered = None

    async for msg, metadata in graph.astream(
        {"messages": ["你好，北京天气怎么样？"]},
        stream_mode="messages"
    ):
        if msg.content and not isinstance(msg, HumanMessage):
            print(msg.content, end="|", flush=True)

        if isinstance(msg, AIMessageChunk):
            if first:
                gathered = msg
                first = False
            else:
                gathered = gathered + msg

            if msg.tool_call_chunks:
                print(f"\n工具调用: {gathered.tool_calls}")

    print("\n")

asyncio.run(token_processing())