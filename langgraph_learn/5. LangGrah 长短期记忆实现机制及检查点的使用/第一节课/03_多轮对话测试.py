"""
第1阶段、AI Agent的记忆机制认知
本文件演示多轮对话测试（配合 Checkpointer 使用）
"""

import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


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


def translate_message(state: State):
    """将上一步的回复翻译成英文"""
    system_prompt = """
    Please translate the received text in any language into English as output
    """
    translated = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": translated}


# 构建带 Checkpointer 的图
def build_graph_with_checkpointer():
    """构建带记忆功能的图"""
    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_node("translate_message", translate_message)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", "translate_message")
    builder.add_edge("translate_message", END)

    # 创建 MemorySaver 作为 checkpointer
    memory = MemorySaver()

    # 编译图时传入 checkpointer
    graph = builder.compile(checkpointer=memory)

    return graph


# 多轮对话测试函数
def test_multi_round_conversation():
    """测试多轮对话功能"""

    # 构建带记忆的图
    graph = build_graph_with_checkpointer()

    # 创建配置，指定 thread_id
    config = {"configurable": {"thread_id": "1"}}

    print("=" * 50)
    print("多轮对话测试 - 带 Checkpointer")
    print("=" * 50)

    # 第一轮对话
    print("\n--- 第一轮对话 ---")
    print("用户: 你好，请介绍你自己")
    for chunk in graph.stream(
        {"messages": ["你好，请介绍你自己"]},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")

    # 第二轮对话（同一 thread_id，可以访问之前的对话历史）
    print("\n--- 第二轮对话 ---")
    print("用户: 我刚才问了你什么？")
    for chunk in graph.stream(
        {"messages": ["我刚才问了你什么？"]},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")

    # 第三轮对话
    print("\n--- 第三轮对话 ---")
    print("用户: 请用英文介绍你自己")
    for chunk in graph.stream(
        {"messages": ["请用英文介绍你自己"]},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")


# 测试不同 thread_id（新的会话）
def test_different_threads():
    """测试不同的线程（新的会话）"""
    graph = build_graph_with_checkpointer()

    print("\n" + "=" * 50)
    print("不同线程测试 - 新的会话")
    print("=" * 50)

    # 使用不同的 thread_id（新的会话）
    config = {"configurable": {"thread_id": "2"}}

    print("\n--- 新会话 ---")
    print("用户: 你好，你认识我吗？")
    for chunk in graph.stream(
        {"messages": ["你好，你认识我吗？"]},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")


# 使用 MemorySaver 查看检查点信息
def test_checkpoint_info():
    """测试查看检查点信息"""

    graph = build_graph_with_checkpointer()
    config = {"configurable": {"thread_id": "test_thread"}}

    # 执行一次对话
    for chunk in graph.stream(
        {"messages": ["你好"]},
        config,
        stream_mode="values"
    ):
        pass

    # 获取当前状态
    state = graph.get_state(config)
    print("\n" + "=" * 50)
    print("检查点状态信息")
    print("=" * 50)
    print(f"Thread ID: {config['configurable']['thread_id']}")
    print(f"Checkpoint ID: {state.config['configurable']['checkpoint_id']}")
    print(f"当前节点: {state.next}")
    print(f"消息数量: {len(state.values.get('messages', []))}")


if __name__ == "__main__":
    # 运行多轮对话测试
    test_multi_round_conversation()

    # 运行不同线程测试
    test_different_threads()

    # 运行检查点信息测试
    test_checkpoint_info()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    print("""
本节代码演示了：
1. 如何使用 MemorySaver 作为 checkpointer
2. 如何通过 thread_id 管理不同的会话
3. 如何查看图的检查点状态

通过 checkpointer，LangGraph 能够在多轮对话中记住之前的上下文，
实现真正的 agent 记忆功能。
""")