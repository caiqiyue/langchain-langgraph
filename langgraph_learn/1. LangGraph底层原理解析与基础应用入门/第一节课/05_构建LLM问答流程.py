# -*- coding: utf-8 -*-
"""
【案例 5】构建 LLM 问答流程
============================================

本案例展示如何将大模型集成到 LangGraph 构建问答系统

要点：
1. 在节点中使用 ChatOpenAI 模型
2. 构建多节点图结构
3. 实现状态在节点间传递
"""

# ============================================================
# 1. 导入依赖
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
import getpass
import os

# 配置 API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# ============================================================
# 2. 定义状态
# ============================================================
class InputState(TypedDict):
    """输入状态"""
    question: str

class OutputState(TypedDict):
    """输出状态"""
    answer: str

class OverallState(InputState, OutputState):
    """合并状态"""
    pass

# ============================================================
# 3. 定义 LLM 节点
# ============================================================
def llm_node(state: InputState):
    """
    LLM 节点 - 使用 GPT 模型处理问题
    """
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
builder.add_node("llm_node", llm_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)
graph = builder.compile()

# ============================================================
# 5. 测试调用
# ============================================================
print("=" * 50)
print("案例 5: 构建 LLM 问答流程")
print("=" * 50)

final_answer = graph.invoke({"question": "你好，我用来测试"})
print(f"问题: 你好，我用来测试")
print(f"回答: {final_answer['answer']}")