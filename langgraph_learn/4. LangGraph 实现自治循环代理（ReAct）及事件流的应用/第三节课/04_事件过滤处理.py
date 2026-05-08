"""
事件过滤与处理
==============

本文件演示如何根据事件类型、名称等条件过滤和处理事件。
"""

# =============================================================================
# 1. 事件过滤基础
# =============================================================================
"""
可以根据以下字段过滤事件：
- event: 事件类型（如 on_chat_model_stream）
- name: 事件名称（如 agent、tools）
- tags: 事件标签
- type: 事件类型字段
"""

# =============================================================================
# 2. 常见过滤场景
# =============================================================================

"""
场景 1: 只获取聊天模型的 token 流
-----------------------------------
"""
# async for event in graph.astream_events({"messages": [query]}, version="v2"):
#     kind = event["event"]
#     if kind == "on_chat_model_stream":
#         print(event["data"]["chunk"].content, end="|", flush=True)


"""
场景 2: 获取特定节点的事件
---------------------------
"""
# async for event in graph.astream_events({"messages": [query]}, version="v2"):
#     if event["name"] == "agent":
#         print(f"Agent event: {event['event']}")


"""
场景 3: 获取工具执行结果
------------------------
"""
# async for event in graph.astream_events({"messages": [query]}, version="v2"):
#     if event["event"] == "on_tool_end":
#         print(f"Tool result: {event['data']}")


# =============================================================================
# 3. 完整示例
# =============================================================================
if __name__ == "__main__":
    import os
    import getpass
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from langchain_core.messages import HumanMessage, AIMessageChunk
    from 04_定义外部工具 import tools

    # 配置 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    # 初始化
    llm = ChatOpenAI(model="gpt-4o")
    graph = create_react_agent(llm, tools=tools)

    # -----------------
    # 示例 1: 只获取 token 流
    # -----------------
    print("=" * 60)
    print("过滤示例: 只获取聊天模型生成的 token")
    print("=" * 60)

    async def stream_tokens_only():
        """只打印聊天模型生成的 token"""
        query = "请用一句话介绍自己"

        async for event in graph.astream_events(
            {"messages": [query]},
            version="v2"
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                # 获取 token 内容
                token = event["data"]["chunk"].content
                print(token, end="|", flush=True)

        print("\n[Token stream complete]")

    # 取消注释运行
    # import asyncio
    # asyncio.run(stream_tokens_only())

    # -----------------
    # 示例 2: 同时获取 token 和工具调用
    # -----------------
    print("\n" + "=" * 60)
    print("过滤示例: 获取 token 和工具调用")
    print("=" * 60)

    async def stream_with_tools():
        """打印 token 流，并检测工具调用"""
        query = "查一下上海的天气"

        first = True
        gathered = None

        async for event in graph.astream_events(
            {"messages": [query]},
            version="v2"
        ):
            kind = event["event"]

            # 处理 token 流
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    print(chunk.content, end="|", flush=True)

                # 收集 chunk 用于获取完整消息
                if isinstance(chunk, AIMessageChunk):
                    if first:
                        gathered = chunk
                        first = False
                    else:
                        gathered = gathered + chunk

                    # 检测工具调用
                    if chunk.tool_call_chunks:
                        print(f"\n[Tool call detected: {gathered.tool_calls}]")

        print("\n[Stream complete]")

    # 取消注释运行
    # import asyncio
    # asyncio.run(stream_with_tools())

    print("\n提示: 取消注释上面的代码来运行实际的事件过滤示例")