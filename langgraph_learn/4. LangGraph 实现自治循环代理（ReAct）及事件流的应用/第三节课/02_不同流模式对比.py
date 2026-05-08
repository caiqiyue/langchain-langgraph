"""
不同流模式对比
==============

本文件对比 LangGraph 的各种流模式，帮助理解何时使用哪种模式。
"""

# =============================================================================
# 流模式详解
# =============================================================================

"""
LangGraph 提供 4 种主要的流模式：

┌─────────────┬────────────────────────────────────────────────────────────┐
│  模式       │  说明                                                       │
├─────────────┼────────────────────────────────────────────────────────────┤
│  values     │  返回每次迭代后的完整状态值 (State)                          │
│             │  格式: {"messages": [...], "state_key": value, ...}        │
├─────────────┼────────────────────────────────────────────────────────────┤
│  updates    │  返回每次迭代后的状态更新部分                                │
│             │  格式: {node_name: {"messages": [...]}}                   │
├─────────────┼────────────────────────────────────────────────────────────┤
│  debug      │  返回详细的调试信息，包括执行时间、节点名称等                │
├─────────────┼────────────────────────────────────────────────────────────┤
│  messages   │  以消息流形式返回，专为聊天模型设计                          │
│             │  可以实时获取生成的 token                                   │
└─────────────┴────────────────────────────────────────────────────────────┘
"""


# =============================================================================
# 完整对比示例
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

    query = "你好，请帮我查一下杭州的天气"

    # -----------------
    # 1. values 模式
    # -----------------
    print("=" * 60)
    print("values 模式 - 返回完整状态")
    print("=" * 60)
    print("每次迭代返回完整的状态字典\n")

    for i, chunk in enumerate(graph.stream({"messages": [query]}, stream_mode="values")):
        print(f"Iteration {i}:")
        print(f"  Keys in state: {list(chunk.keys())}")
        print(f"  Last message type: {type(chunk['messages'][-1]).__name__}")
        print()

    # -----------------
    # 2. updates 模式
    # -----------------
    print("\n" + "=" * 60)
    print("updates 模式 - 返回状态更新")
    print("=" * 60)
    print("每次迭代返回更新状态的节点名称和值\n")

    for i, chunk in enumerate(graph.stream({"messages": [query]}, stream_mode="updates")):
        print(f"Iteration {i}:")
        print(f"  Updated nodes: {list(chunk.keys())}")
        print()

    # -----------------
    # 3. debug 模式
    # -----------------
    print("\n" + "=" * 60)
    print("debug 模式 - 返回调试信息")
    print("=" * 60)
    print("每次迭代返回详细的执行信息\n")

    for i, chunk in enumerate(graph.stream({"messages": [query]}, stream_mode="debug")):
        print(f"Iteration {i}:")
        print(f"  Data type: {type(chunk)}")
        if isinstance(chunk, dict):
            print(f"  Keys: {list(chunk.keys())}")
        print()

    # -----------------
    # 4. messages 模式
    # -----------------
    print("\n" + "=" * 60)
    print("messages 模式 - 消息流")
    print("=" * 60)
    print("实时返回生成的 token\n")

    from langchain_core.messages import HumanMessage, AIMessageChunk

    first = True
    for msg, metadata in graph.stream({"messages": [query]}, stream_mode="messages"):
        # 过滤掉 HumanMessage，只显示 AI 消息
        if msg.content and not isinstance(msg, HumanMessage):
            print(msg.content, end="|", flush=True)

        # 收集并合并 AIMessageChunk
        if isinstance(msg, AIMessageChunk):
            if first:
                gathered = msg
                first = False
            else:
                gathered = gathered + msg

            # 如果有工具调用，显示工具调用信息
            if msg.tool_call_chunks:
                print(f"\n[Tool calls detected: {gathered.tool_calls}]")

    print("\n\n流模式对比完成!")