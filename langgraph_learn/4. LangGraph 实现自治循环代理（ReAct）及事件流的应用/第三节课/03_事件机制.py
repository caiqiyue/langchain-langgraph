"""
LangGraph 事件机制
==================

本文件演示如何使用 astream_events 方法获取 Agent 执行过程中的详细事件信息。

重要：astream_events 只支持异步调用，需要使用 astream_events 方法。
"""

# =============================================================================
# 1. 事件机制概述
# =============================================================================
"""
LangGraph 的 astream_events 方法可以追踪 Agent 执行过程中的所有事件：

事件类型：
- on_chain_start: 链开始执行
- on_chain_end: 链结束执行
- on_chat_model_start: 聊天模型开始
- on_chat_model_stream: 聊天模型生成中（实时 token）
- on_chat_model_end: 聊天模型结束
- on_tool_start: 工具开始执行
- on_tool_end: 工具结束执行
- on_tool_stream: 工具执行中
"""

# =============================================================================
# 2. 事件结构
# =============================================================================
"""
每个事件包含以下字段：
- event: 事件类型名称
- name: 事件名称（如节点名称）
- data: 事件数据
- metadata: 元数据（包括 tags、thread_id 等）
"""

# =============================================================================
# 3. 完整示例
# =============================================================================
if __name__ == "__main__":
    import os
    import getpass
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from 04_定义外部工具 import tools

    # 配置 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    # 初始化
    llm = ChatOpenAI(model="gpt-4o")
    graph = create_react_agent(llm, tools=tools)

    # -----------------
    # 示例 1: 基本事件追踪
    # -----------------
    print("=" * 60)
    print("事件追踪示例")
    print("=" * 60)

    async def track_events():
        """追踪 Agent 执行过程中的所有事件"""
        query = "你好，请帮我查一下北京的天气"

        events = []
        async for event in graph.astream_events(
            {"messages": [query]},
            version="v2"  # 使用 v2 版本 API
        ):
            events.append(event)
            kind = event["event"]
            name = event["name"]
            print(f"{kind}: {name}")

        return events

    # 取消注释运行
    # import asyncio
    # events = asyncio.run(track_events())

    # -----------------
    # 示例 2: 查看事件详情
    # -----------------
    print("\n" + "=" * 60)
    print("事件详情示例")
    print("=" * 60)

    async def event_details():
        """查看具体事件的详细信息"""
        query = "你好，请介绍一下你自己"

        events = []
        async for event in graph.astream_events(
            {"messages": [query]},
            version="v2"
        ):
            events.append(event)

        # 查看第一个事件
        print("第一个事件 (events[0]):")
        print(f"  Event type: {events[0]['event']}")
        print(f"  Event name: {events[0]['name']}")
        print(f"  Data keys: {list(events[0]['data'].keys()) if events[0].get('data') else 'N/A'}")

        # 查看聊天模型流事件
        print("\n聊天模型流事件 (events[10]):")
        if len(events) > 10:
            print(f"  Event type: {events[10]['event']}")
            print(f"  Data chunk: {events[10]['data'].get('chunk')}")

    # 取消注释运行
    # import asyncio
    # asyncio.run(event_details())

    print("\n事件机制示例完成!")
    print("提示: 取消注释上面的代码来运行实际的事件追踪")