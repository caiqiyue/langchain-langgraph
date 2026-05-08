"""
第1阶段、LangGraph中的HIL
本文件演示如何构建基础的 HIL（Human-in-the-loop）图结构
"""

import getpass
import os
from typing import TypedDict
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage


# 初始化 LLM
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")


# ============================================================
# 定义状态和节点
# ============================================================

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str
    need_approval: bool
    approval_result: str


def call_model(state: State):
    """
    处理用户输入，判断是否需要人工审批

    如果用户输入包含"删除"等敏感词，则触发人工审批流程
    """
    user_input = state["user_input"]

    if "删除" in user_input:
        # 需要人工审批
        return {
            "need_approval": True,
            "messages": [AIMessage(content=f"您的请求「{user_input}」需要人工审批确认。")]
        }
    else:
        # 直接执行
        response = llm.invoke(user_input)
        return {
            "need_approval": False,
            "messages": [response]
        }


def execute_with_approval(state: State):
    """
    根据人工审批结果执行操作

    这是中断点后的节点，需要根据审批结果决定如何执行
    """
    approval = state.get("approval_result", "")

    if approval == "是":
        return {
            "messages": [AIMessage(content="已获得批准，操作已执行。")]
        }
    elif approval == "否":
        return {
            "messages": [AIMessage(content="操作已被拒绝。")]
        }
    else:
        return {
            "messages": [AIMessage(content="等待审批中...")]
        }


def normal_execution(state: State):
    """
    正常执行（不需要审批）
    """
    user_input = state["user_input"]
    response = llm.invoke(user_input)
    return {"messages": [response]}


# ============================================================
# 构建 HIL 图
# ============================================================

def build_hil_graph():
    """
    构建 Human-in-the-loop 图

    核心要点：
    1. 使用 checkpointer 保存状态
    2. 使用 interrupt_before 在需要审批的节点前中断
    3. 通过 update_state 更新审批结果
    """

    # 定义状态图
    builder = StateGraph(State)

    # 添加节点
    builder.add_node("call_model", call_model)
    builder.add_node("execute_with_approval", execute_with_approval)
    builder.add_node("normal_execution", normal_execution)

    # 添加边
    builder.add_edge(START, "call_model")

    # 注意：这里需要通过条件边来决定下一步是审批流程还是直接执行
    # 简化起见，我们使用以下逻辑：
    # - 如果 need_approval 为 True，走 execute_with_approval
    # - 否则走 normal_execution

    # 构建条件边（这里简化了，实际应用中可能更复杂）
    def route_after_call(state):
        if state.get("need_approval", False):
            return "execute_with_approval"
        return "normal_execution"

    from typing import Literal

    builder.add_conditional_edges(
        "call_model",
        route_after_call,
        {
            "execute_with_approval": "execute_with_approval",
            "normal_execution": "normal_execution"
        }
    )

    builder.add_edge("execute_with_approval", END)
    builder.add_edge("normal_execution", END)

    # 创建 checkpointer
    memory = MemorySaver()

    # 编译图，在 execute_with_approval 节点之前设置中断点
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["execute_with_approval"]
    )

    return graph


def demo_hil_workflow():
    """
    演示 HIL 工作流程
    """
    print("=" * 50)
    print("Human-in-the-loop 工作流程演示")
    print("=" * 50)

    graph = build_hil_graph()
    config = {"configurable": {"thread_id": "hil_demo"}}

    # 场景1：正常查询（不需要审批）
    print("\n--- 场景1：正常查询 ---")
    print("用户输入: 北京天气怎么样？")
    for chunk in graph.stream(
        {"user_input": "北京天气怎么样？"},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")

    # 场景2：敏感操作（需要审批）
    print("\n--- 场景2：敏感操作（需要审批） ---")
    print("用户输入: 帮我删除所有数据")

    # 手动重置 thread
    config = {"configurable": {"thread_id": "hil_demo2"}}

    for chunk in graph.stream(
        {"user_input": "帮我删除所有数据"},
        config,
        stream_mode="values"
    ):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")

    # 检查状态
    state = graph.get_state(config)
    print(f"\n当前状态 - next 节点: {state.next}")
    print("图已中断，等待人工审批...")

    # 模拟审批流程
    print("\n--- 模拟人工审批 ---")
    approval = input("是否批准删除操作？（是/否）: ")

    # 更新状态
    snapshot = state.values
    snapshot["approval_result"] = approval
    graph.update_state(config, snapshot)

    # 继续执行
    print("\n--- 继续执行 ---")
    for chunk in graph.stream(None, config, stream_mode="values"):
        if "messages" in chunk:
            print(f"助手: {chunk['messages'][-1].content}")


if __name__ == "__main__":
    print("=" * 50)
    print("基础 HIL 图构建")
    print("=" * 50)
    print("""
Human-in-the-loop (HIL) 核心概念：
1. 断点（breakpoint）：在特定节点暂停图的执行
2. checkpointer：保存图状态，支持恢复执行
3. 人工审批：用户可以查看状态并决定是否继续执行

本节演示了：
1. 如何构建需要审批的节点
2. 如何设置中断点
3. 如何通过 update_state 更新审批结果
4. 如何恢复图的执行

下一节课将学习更复杂的 HIL 应用场景。
""")

    # 运行演示
    # demo_hil_workflow()