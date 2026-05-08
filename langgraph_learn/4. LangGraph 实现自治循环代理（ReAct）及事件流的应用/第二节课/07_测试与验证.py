"""
测试与验证 ReAct Agent
=======================

本文件演示如何测试 ReAct Agent 的各种功能。
"""

# =============================================================================
# 1. 基础调用
# =============================================================================
# response = graph.invoke({"messages": ["你好，请介绍一下你自己"]})
# print(response["messages"][-1].content)

# =============================================================================
# 2. 工具调用示例
# =============================================================================
# 调用天气查询工具
# response = graph.invoke({"messages": ["查询北京的天气"]})
# print(response["messages"][-1].content)

# =============================================================================
# 3. 复杂多工具调用
# =============================================================================
# 同时查询天气并存储到数据库
# response = graph.invoke({
#     "messages": ["查询上海和北京的天气，然后告诉我哪个城市更暖和，并把结果存储到数据库"]
# })
# print(response["messages"][-1].content)

# =============================================================================
# 4. 从数据库查询数据
# =============================================================================
# response = graph.invoke({
#     "messages": ["查询数据库中有哪些城市的天气记录，列出详细信息并做一个详细的对比"]
# })
# print(response["messages"][-1].content)


# =============================================================================
# 完整测试代码
# =============================================================================
if __name__ == "__main__":
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
    from 04_定义外部工具 import tools
    import os
    import getpass

    # 配置 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    # 初始化模型和 Agent
    llm = ChatOpenAI(model="gpt-4o")
    graph = create_react_agent(llm, tools=tools)

    # 测试用例
    test_queries = [
        "你好，请介绍一下你自己",
        "查询北京的天气",
        "查询上海和北京的天气，告诉我哪个城市更暖和",
    ]

    print("=" * 60)
    print("ReAct Agent Testing")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        try:
            response = graph.invoke({"messages": [query]})
            print(f"Response: {response['messages'][-1].content[:200]}...")
        except Exception as e:
            print(f"Error: {e}")