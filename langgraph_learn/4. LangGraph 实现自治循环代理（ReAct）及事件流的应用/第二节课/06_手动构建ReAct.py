"""
手动构建 ReAct 循环
===================

本文件演示如何手动构建 ReAct Agent，而不是使用 create_react_agent 预置方法。
这有助于理解 ReAct 的底层工作原理。

关键步骤：
1. 定义图状态 (StateGraph)
2. 定义 Router Function (决定下一步路由)
3. 定义模型调用节点
4. 定义工具执行节点
5. 构建图结构
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

# =============================================================================
# Step 1: 定义图状态
# =============================================================================
class State(TypedDict):
    """Agent 状态，包含消息列表"""
    messages: Annotated[list, "The messages in the conversation"]


# =============================================================================
# Step 2: 定义 Router Function
# =============================================================================
def should_continue(state: State):
    """
    Router 函数：根据消息内容决定下一步路径

    Returns:
        "continue": 如果最后一条消息包含工具调用，继续执行工具
        "end": 如果没有工具调用，结束对话
    """
    messages = state["messages"]
    last_message = messages[-1]

    # 如果有工具调用，返回 "continue"
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"


# =============================================================================
# Step 3: 构建手动 ReAct 图
# =============================================================================
def build_manual_react_graph(llm, tools):
    """
    手动构建 ReAct Agent 图

    与 create_react_agent 的区别：
    - 需要手动定义所有节点和边
    - 需要手动实现 Router Function
    - 更加灵活，可以自定义更多逻辑
    """
    # 创建状态图
    workflow = StateGraph(State)

    # 创建工具节点（LangGraph 预置的工具执行节点）
    tool_node = ToolNode(tools)

    # 添加节点
    workflow.add_node("agent", llm)  # 模型节点直接使用 llm
    workflow.add_node("tools", tool_node)  # 工具节点

    # 设置入口点
    workflow.add_edge(START, "agent")

    # 添加条件边（根据 Router Function 的返回值决定下一步）
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",  # 继续执行工具
            "end": END            # 结束对话
        }
    )

    # 工具执行完后回到 agent 继续对话
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# =============================================================================
# Step 4: 对比预置方法和手动构建
# =============================================================================
"""
预置方法 create_react_agent 的优势：
1. 开箱即用，无需手动配置
2. 内置了完整的 ReAct 逻辑
3. 自动处理工具调用和消息更新
4. 支持更多高级功能（流模式、事件追踪等）

手动构建方法的优势：
1. 完全控制图结构
2. 可以自定义更多节点和边
3. 适合学习底层原理
4. 适合需要深度定制的场景

实际开发中，推荐使用 create_react_agent；
学习原理时，推荐使用手动构建方法。
"""


# =============================================================================
# 完整示例
# =============================================================================
if __name__ == "__main__":
    # 导入工具和模型
    from 04_定义外部工具 import tools
    import os
    from langchain_openai import ChatOpenAI

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    llm = ChatOpenAI(model="gpt-4o")

    # 使用手动方法构建
    manual_graph = build_manual_react_graph(llm, tools)

    # 使用预置方法构建
    from langgraph.prebuilt import create_react_agent
    preset_graph = create_react_agent(llm, tools=tools)

    print("Manual ReAct Graph created!")
    print("Preset ReAct Graph created!")