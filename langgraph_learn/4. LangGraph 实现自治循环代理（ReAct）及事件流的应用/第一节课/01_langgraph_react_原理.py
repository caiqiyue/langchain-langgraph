"""
LangGraph 与 ReAct 的工作原理
==============================

本文件演示 LangGraph 中预置 ReAct Agent 的实现原理。

核心概念：
1. ReAct (Reasoning + Acting) = 推理 + 行动
2. LangGraph 预置了 create_react_agent 方法，可以快速构建 ReAct 循环
3. 与 LangChain 中的 ReAct Agent 不同，LangGraph 基于消息传递

关键组件：
- StateGraph: 图的状态管理
- messages: 消息列表，记录对话历史
- tools: 外部工具列表
- Router Function: 决定下一步路由
"""

# =============================================================================
# 1. 状态定义
# =============================================================================
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 定义 Agent 状态
class State(TypedDict):
    messages: Annotated[list, "The messages in the conversation"]

# =============================================================================
# 2. Router Function - 决定是否继续执行
# =============================================================================
def should_continue(state: State):
    """
    Router 函数：根据节点执行结果决定下一步路径
    - 如果最后一条消息包含 tool_calls，说明需要调用工具
    - 否则结束对话
    """
    messages = state["messages"]
    last_message = messages[-1]

    # 如果有工具调用，返回 "continue" 继续执行工具节点
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"


# =============================================================================
# 3. 模型调用节点
# =============================================================================
from typing import Literal
from langchain_core.runnables import RunnableConfig

def call_model(state: State, config: RunnableConfig):
    """
    模型调用节点 - 接收当前消息列表，调用 LLM 生成响应
    """
    messages = state["messages"]

    # 调用模型（这里需要传入 llm 和 tools，实际使用时由外部注入）
    response = config["configurable"]["llm"].bind_tools(config["configurable"]["tools"])
    result = response.invoke(messages)

    return {"messages": [result]}


# =============================================================================
# 4. 工具执行节点
# =============================================================================
def tool_node(state: State):
    """
    工具执行节点 - 执行模型调用的工具
    """
    messages = state["messages"]
    last_message = messages[-1]

    # 调用工具并获取结果
    tool_results = []
    for tool_call in last_message.tool_calls:
        # 执行工具（这里简化处理，实际需要根据 tool_call['name'] 调用对应工具）
        result = f"Tool {tool_call['name']} executed"
        tool_results.append({"role": "tool", "content": result, "tool_call_id": tool_call['id']})

    return {"messages": tool_results}


# =============================================================================
# 5. 构建图结构
# =============================================================================
def build_react_graph(llm, tools):
    """
    构建 ReAct Agent 图
    """
    workflow = StateGraph(State)

    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # 添加边
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "tools", "end": END}
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# =============================================================================
# 6. 使用 LangGraph 预置方法（推荐）
# =============================================================================
"""
LangGraph 提供了 create_react_agent 方法，这是更推荐的使用方式：

from langgraph.prebuilt import create_react_agent

graph = create_react_agent(llm, tools=tools)

预置方法的优势：
1. 开箱即用，无需手动构建图结构
2. 内置了完整的 ReAct 循环
3. 支持多种流模式 (stream_mode)
4. 与 LangSmith 集成方便追踪

参考：https://langchain-ai.github.io/langgraph/reference/prebuilt/
"""


# =============================================================================
# 7. ReAct vs Tool Calling 模式对比
# =============================================================================
"""
LangGraph 支持两种预置 Agent 结构：

1. Tool Calling 模式（函数调用模式）
   - 模型直接决定调用哪个工具
   - 工具选择是确定性的
   - 适用于工具数量较少、场景明确的场景

2. ReAct 模式（推理+行动模式）
   - 模型先推理，再决定行动
   - 支持更复杂的决策流程
   - 适用于需要多步推理的复杂场景

参考：
- LangChain Agents Type: https://python.langchain.com/v0.1/docs/modules/agents/agent_types/
- LangGraph create_react_agent: https://langchain-ai.github.io/langgraph/reference/prebuilt/
"""