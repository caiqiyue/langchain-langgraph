"""
第1阶段、LangGraph中的HIL
本文件演示如何在 compile() 方法中设置中断点（breakpoint）
"""

import getpass
import os
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages


# 初始化 LLM
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str


# 定义节点函数
def call_model(state: State):
    """处理用户输入"""
    response = llm.invoke(state["user_input"])
    return {"messages": [response]}


def execute_action(state: State):
    """执行操作（这里模拟需要人工确认的操作）"""
    # 模拟执行某个敏感操作
    if "删除" in state["user_input"]:
        return {"messages": ["[需要人工确认] 是否执行删除操作？"]}
    return {"messages": ["操作已完成"]}


# ============================================================
# 中断点设置示例
# ============================================================
# 在 compile() 方法中，通过 interrupt_before 和 interrupt_after 参数
# 可以在指定节点之前或之后中断图的执行，实现 Human-in-the-loop


def build_graph_with_interrupt_before():
    """
    在节点之前中断示例

    interrupt_before=["节点名称"] 会在执行该节点之前中断
    """
    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_node("execute_action", execute_action)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", "execute_action")
    builder.add_edge("execute_action", END)

    # 创建 MemorySaver 作为 checkpointer（中断点需要 checkpointer）
    memory = MemorySaver()

    # 在 execute_action 节点之前设置中断点
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["execute_action"]
    )

    return graph


def build_graph_with_interrupt_after():
    """
    在节点之后中断示例

    interrupt_after=["节点名称"] 会在执行该节点之后中断
    """
    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_node("execute_action", execute_action)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", "execute_action")
    builder.add_edge("execute_action", END)

    memory = MemorySaver()

    # 在 execute_action 节点之后设置中断点
    graph = builder.compile(
        checkpointer=memory,
        interrupt_after=["execute_action"]
    )

    return graph


def build_graph_with_both():
    """
    同时设置 interrupt_before 和 interrupt_after
    """
    builder = StateGraph(State)
    builder.add_node("call_model", call_model)
    builder.add_node("execute_action", execute_action)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", "execute_action")
    builder.add_edge("execute_action", END)

    memory = MemorySaver()

    # 同时在节点之前和之后设置中断点
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["execute_action"],
        interrupt_after=["call_model"]
    )

    return graph


def test_interrupt_before():
    """测试 interrupt_before 中断点"""
    print("=" * 50)
    print("测试 interrupt_before 中断点")
    print("=" * 50)

    graph = build_graph_with_interrupt_before()
    config = {"configurable": {"thread_id": "test1"}}

    # 运行图，会在 execute_action 节点之前中断
    print("\n执行第一段输入...")
    for chunk in graph.stream(
        {"user_input": "帮我查询天气"},
        config,
        stream_mode="values"
    ):
        print(f"输出: {chunk}")

    # 检查图的状态
    state = graph.get_state(config)
    print(f"\n中断点位置: {state.next}")
    print("图已暂停，等待人工确认...")

    # 可以通过 update_state 更新状态，然后继续执行
    print("\n更新状态后继续执行...")
    for chunk in graph.stream(None, config, stream_mode="values"):
        print(f"输出: {chunk}")


def test_interrupt_after():
    """测试 interrupt_after 中断点"""
    print("\n" + "=" * 50)
    print("测试 interrupt_after 中断点")
    print("=" * 50)

    graph = build_graph_with_interrupt_after()
    config = {"configurable": {"thread_id": "test2"}}

    # 运行图
    for chunk in graph.stream(
        {"user_input": "测试中断"},
        config,
        stream_mode="values"
    ):
        print(f"输出: {chunk}")


if __name__ == "__main__":
    print("=" * 50)
    print("中断点设置示例")
    print("=" * 50)
    print("""
在 compile() 方法中设置中断点：
1. interrupt_before: 在指定节点执行之前中断
2. interrupt_after: 在指定节点执行之后中断

使用中断点的注意事项：
1. 必须提供 checkpointer 参数，因为需要保存图状态
2. 中断后可以通过 get_state() 查看状态
3. 通过 update_state() 更新状态
4. 传入 None 作为输入可以继续执行

下一节我们将学习如何构建完整的 HIL 图。
""")

    # 运行测试
    # test_interrupt_before()
    # test_interrupt_after()