# -*- coding: utf-8 -*-
"""
【案例1】构建LLM问答流程
============================================

本案例展示如何将大模型集成到LangGraph框架中构建问答流程。

要点：
1. 使用ChatOpenAI作为LLM
2. 定义LLM节点处理用户问题
3. 通过StateGraph构建问答图
4. 使用invoke方法调用图
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
from typing_extensions import TypedDict

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 合并成更全面的字典类型
class OverallState(InputState, OutputState):
    pass

# ============================================================
# 3. 定义LLM节点
# ============================================================
def llm_node(state: InputState):
    """LLM节点：接收用户问题，调用GPT模型生成回复"""
    messages = [
        ("system", "你是一位乐于助人的智能小助理"),
        ("human", state["question"])
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

# 添加边
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)

# 编译图
graph = builder.compile()

# ============================================================
# 5. 调用图
# ============================================================
print("测试问答流程：")

# 测试1
result = graph.invoke({"question": "你好，我用来测试"})
print(f"问题: 你好，我用来测试")
print(f"答案: {result['answer']}")
print()

# 测试2
result = graph.invoke({"question": "你好，请你详细的介绍一下你自己"})
print(f"问题: 你好，请你详细的介绍一下你自己")
print(f"答案: {result['answer']}")
