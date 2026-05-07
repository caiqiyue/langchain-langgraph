# -*- coding: utf-8 -*-
"""
【案例9】使用astream_events获取事件流
============================================

本案例展示如何使用astream_events获取完整事件流

要点：
1. astream_events方法的使用
2. 事件类型说明
3. 事件数据结构
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
# 3. 事件流说明
# ============================================================
print("=" * 50)
print("事件流 astream_events")
print("=" * 50)
print("""
事件流说明：
- astream_events方法仅支持异步
- 用于访问自定义事件和中间输出
- version="v2"参数指定使用测试版API

常见事件类型：
- on_chain_start: LangGraph - 开始
- on_chain_end: LangGraph - 结束
- on_chat_model_start: ChatOpenAI - 开始聊天模型调用
- on_chat_model_stream: ChatOpenAI - 流式输出
- on_chat_model_end: ChatOpenAI - 聊天模型结束
- ChannelWrite<call_model,messages> - 写入通道
""")

# ============================================================
# 4. 执行事件流
# ============================================================
import asyncio

async def run_events():
    """执行事件流"""
    print("\n--- 打印所有事件 ---")

    async for event in graph.astream_events(
        {"messages": ["你好，请你介绍一下你自己"]},
        version="v2"
    ):
        kind = event["event"]
        print(f"{kind}: {event['name']}")

asyncio.run(run_events())

# ============================================================
# 5. 打印特定事件
# ============================================================
async def print_events_detail():
    """打印事件详情"""
    print("\n--- 打印事件详情 ---")

    events = []
    async for event in graph.astream_events(
        {"messages": ["你好，北京的天气怎么样？"]},
        version="v2"
    ):
        events.append(event)

    print(f"\n总事件数: {len(events)}")
    print(f"\n第一个事件:")
    print(events[0])
    print(f"\n第十个事件:")
    print(events[10])

asyncio.run(print_events_detail())