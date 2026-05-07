# -*- coding: utf-8 -*-
"""
【案例】Supervisor 基础架构实现
============================================

本案例展示如何使用 LangGraph 实现 Supervisor 多代理架构

要点：
1. Supervisor 作为中央控制器协调各个代理
2. 通过 next 字段决定下一步调用哪个代理
3. 每个子代理完成后向 Supervisor 汇报

案例说明：
构建一个简单的 Supervisor 多代理系统，包含：
- chat: 自然语言对话代理
- coder: 代码生成代理
- sqler: SQL查询代理
"""

# ============================================================
# 1. 环境配置
# ============================================================
import getpass
import os

from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")

# ============================================================
# 2. 定义状态模式
# ============================================================
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str

# ============================================================
# 3. 定义子代理
# ============================================================
def chat(state: AgentState):
    """自然语言对话代理"""
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chat")]
    return {"messages": final_response}

def coder(state: AgentState):
    """代码生成代理"""
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="coder")]
    return {"messages": final_response}

def sqler(state: AgentState):
    """SQL查询代理"""
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="sqler")]
    return {"messages": final_response}

# ============================================================
# 4. 定义 Supervisor
# ============================================================
from typing import Literal
from typing_extensions import TypedDict

members = ["chat", "coder", "sqler"]
options = members + ["FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""
    next: Literal[*options]

from langchain_core.messages import HumanMessage

def supervisor(state: AgentState):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- chat: Responds directly to user inputs using natural language.\n"
        "- coder: Activated for tasks that require mathematical calculations or specific coding needs.\n"
        "- sqler: Used when database queries or explicit SQL generation is needed.\n\n"
        "Given the following user request, respond with the worker to act next."
        " Each worker will perform a task and respond with their results and status."
        " When finished, respond with FINISH."
    )

    messages = [{"role": "system", "content": system_prompt},] + state["messages"]

    response = llm.with_structured_output(Router).invoke(messages)

    next_ = response["next"]

    if next_ == "FINISH":
        next_ = END

    return {"next": next_}

# ============================================================
# 5. 构建图
# ============================================================
builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("coder", coder)
builder.add_node("sqler", sqler)

# 每个子代理完成后向主管汇报
for member in members:
    builder.add_edge(member, "supervisor")

# 条件边根据 next 字段路由
builder.add_conditional_edges("supervisor", lambda state: state["next"])

# 设置入口点
builder.add_edge(START, "supervisor")

# 编译图
graph = builder.compile()

# ============================================================
# 6. 测试运行
# ============================================================
print("=" * 50)
print("案例：Supervisor 基础架构")
print("=" * 50)

# 测试1：简单对话
print("\n--- 测试1：简单对话 ---")
for chunk in graph.stream({"messages": "你好，请你介绍一下你自己"}, stream_mode="values"):
    print(chunk)

# 测试2：代码生成
print("\n--- 测试2：代码生成 ---")
for chunk in graph.stream({"messages": "帮我生成一个二分查找的Python代码"}, stream_mode="values"):
    print(chunk)

print("\n" + "=" * 50)
print("案例说明：")
print("=" * 50)
print("""
本案例实现了 Supervisor 多代理架构。

架构特点：
1. Supervisor 作为中央控制器
2. 每个子代理完成工作后向 Supervisor 汇报
3. Supervisor 决定下一步调用哪个代理或结束

与 Network 架构的区别：
- Network: 每个代理可以直接与其他代理通信
- Supervisor: 所有通信都通过 Supervisor 中转
""")