"""
流模式基础
==========

本文件演示 LangGraph 流模式 (Stream Mode) 的基本使用方法。
"""

# =============================================================================
# 1. 同步流模式 (stream)
# =============================================================================
"""
使用 stream 方法进行同步流式调用：

def stream(
    self,
    input: Union[dict[str, Any], Any],  # 图的输入，从状态中取值
    config: Optional[RunnableConfig] = None,
    stream_mode: StreamMode = "values",  # 流模式
    **kwargs: Any
) -> Iterator[Output]
"""

# =============================================================================
# 2. 异步流模式 (astream)
# =============================================================================
"""
使用 astream 方法进行异步流式调用：

async def astream(
    self,
    input: Union[dict[str, Any], Any],
    config: Optional[RunnableConfig] = None,
    stream_mode: StreamMode = "values",
    **kwargs: Any
) -> AsyncIterator[Output]
"""

# =============================================================================
# 3. 流模式类型
# =============================================================================
"""
LangGraph 支持多种流模式：

1. values 模式：
   - 返回图中每次迭代后的完整状态值
   - 适合需要查看完整中间状态的场景

2. updates 模式：
   - 返回每次迭代后的更新部分
   - 格式为 {node_name: values}
   - 适合只需要关注特定节点更新的场景

3. debug 模式：
   - 返回图中执行过程的详细信息
   - 包含更多调试信息
   - 适合调试和性能分析

4. messages 模式：
   - 以消息流的形式返回输出
   - 专为聊天模型设计
   - 可以实时获取 token
"""


# =============================================================================
# 4. 完整示例
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
    # 示例 1: values 模式
    # -----------------
    print("=" * 60)
    print("Stream Mode: values")
    print("=" * 60)

    def print_stream_values(stream):
        """打印 values 模式的流输出"""
        for sub_stream in stream:
            message = sub_stream["messages"][-1]
            print(f"Current node: {sub_stream.get('__node__', 'unknown')}")
            message.pretty_print()

    # input_message = {"messages": ["你好，帮我查一下南京的天气"]}
    # print_stream_values(graph.stream(input_message, stream_mode="values"))

    # -----------------
    # 示例 2: updates 模式
    # -----------------
    print("\n" + "=" * 60)
    print("Stream Mode: updates")
    print("=" * 60)

    def print_stream_updates(stream):
        """打印 updates 模式的流输出"""
        for sub_stream in stream:
            print(sub_stream)

    # input_message = {"messages": ["你好，帮我查一下上海的天气"]}
    # print_stream_updates(graph.stream(input_message, stream_mode="updates"))

    # -----------------
    # 示例 3: 异步 astream
    # -----------------
    print("\n" + "=" * 60)
    print("Async Stream: astream with values")
    print("=" * 60)

    async def async_stream_example():
        """异步流示例"""
        async for chunk in graph.astream(
            input={"messages": ["你好，请详细介绍一下你自己"]},
            stream_mode="values"
        ):
            message = chunk["messages"][-1]
            message.pretty_print()

    # 取消注释运行异步示例
    # import asyncio
    # asyncio.run(async_stream_example())

    print("\n流模式基础示例完成!")