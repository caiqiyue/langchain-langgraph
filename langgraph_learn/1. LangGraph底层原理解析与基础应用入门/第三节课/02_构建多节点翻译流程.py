# -*- coding: utf-8 -*-
"""
【案例2】构建多节点翻译工作流
============================================

本案例展示如何在LangGraph中构建更复杂的多节点工作流。

要点：
1. 定义多个功能节点（LLM节点 + Action节点）
2. 节点间传递中间状态信息
3. 通过边建立节点间的数据流转
4. 实现翻译等复杂任务
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
import getpass

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 设置OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# ============================================================
# 2. 定义状态模式
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Optional

# 定义输入的模式
class InputState(TypedDict):
    question: str
    llm_answer: Optional[str]  # 表示 answer 可以是 str 类型，也可以是 None

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 合并成更全面的字典类型
class OverallState(InputState, OutputState):
    pass

# ============================================================
# 3. 定义多个节点
# ============================================================
def llm_node(state: InputState):
    """LLM节点：接收用户问题，调用GPT模型生成回复"""
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    response = llm.invoke(messages)

    return {"llm_answer": response.content}

def action_node(state: InputState):
    """Action节点：将LLM的回复翻译成法语"""
    messages = [
        ("system", "无论你接收到什么语言的文本，请翻译成法语"),
        ("human", state["llm_answer"])
    ]

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    response = llm.invoke(messages)

    return {"answer": response.content}

# ============================================================
# 4. 构建图
# ============================================================
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 添加节点
builder.add_node("llm_node", llm_node)
builder.add_node("action_node", action_node)

# 添加边
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "action_node")
builder.add_edge("action_node", END)

# 编译图
graph = builder.compile()

# ============================================================
# 5. 调用图
# ============================================================
print("测试多节点翻译工作流：")

# 测试1
result = graph.invoke({"question": "你好，请你详细的介绍一下你自己"})
print(f"问题: 你好，请你详细的介绍一下你自己")
print(f"法语答案: {result['answer']}")
print()

# 测试2
result = graph.invoke({"question": "请问什么是人工智能？"})
print(f"问题: 请问什么是人工智能？")
print(f"法语答案: {result['answer']}")
