"""
第1阶段、AI Agent的记忆机制认知
本文件演示异步流式输出的测试方法
"""

import asyncio
import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


# 初始化 LLM
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: State):
    """处理用户输入，调用大模型生成回复"""
    response = llm.invoke(state["messages"])
    return {"messages": response}


async def test_async_stream():
    """测试异步流式输出"""
    # 构建简单图
    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)

    simple_graph = builder.compile()

    print("=" * 50)
    print("异步流式输出测试")
    print("=" * 50)

    # 使用异步流式输出
    print("\n开始异步流式输出测试...")
    async for chunk in simple_graph.astream(
        input={"messages": ["你好，请介绍你自己"]},
        stream_mode="values"
    ):
        print(f"收到片段: {chunk}")


# 下面的函数用于流式输出测试
async def test_stream_mode():
    """测试不同流模式下的输出"""

    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)

    graph = builder.compile()

    print("\n" + "=" * 50)
    print("测试 values 流模式")
    print("=" * 50)

    async for chunk in graph.astream(
        input={"messages": ["你好"]},
        stream_mode="values"
    ):
        print(f"values chunk: {chunk}")

    print("\n" + "=" * 50)
    print("测试 debug 流模式")
    print("=" * 50)

    # debug 模式可以看到更多内部信息
    async for chunk in graph.astream(
        input={"messages": ["你好"]},
        stream_mode="debug"
    ):
        print(f"debug chunk type: {chunk.get('type', 'unknown')}")
        if chunk.get('type') == 'checkpoint':
            print(f"  Thread id: {chunk['payload']['config']['configurable']['thread_id']}")


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(test_async_stream())
    asyncio.run(test_stream_mode())