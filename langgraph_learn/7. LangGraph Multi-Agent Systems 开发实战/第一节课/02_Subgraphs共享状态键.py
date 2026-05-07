# -*- coding: utf-8 -*-
"""
【案例 1】Subgraphs 共享状态键通信
============================================

本案例展示如何使用 LangGraph 实现父子图之间通过共享状态键进行通信

要点：
1. 父图和子图的状态模式中有共同的键（通道）
2. 子图可以访问和更新父图的共享状态
3. 父图 -> 子图 -> 父图的信息传递流程

案例说明：
设计一个评分系统，分为两个主要部分：
- 父图负责处理初步的用户输入，并生成响应
- 子图则进一步处理这些响应，进行内容精简和质量评估
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os

# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url="http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)

# ============================================================
# 2. 定义父图的状态模式
# ============================================================
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应

# 父图节点：使用大模型处理用户输入，并生成响应
def parent_node(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}

# ============================================================
# 3. 定义子图的状态模式
# ============================================================
# 定义子图中的状态
class SubgraphState(TypedDict):
    # 这个 key 是和 父图（ParentState）共享的，
    final_answer: str
    # 这个key 是 子图 (subgraph) 中独享的
    summary_answer: str

# ============================================================
# 4. 定义子图的节点逻辑
# ============================================================
from langchain_core.messages import SystemMessage, HumanMessage

# 第一个节点：将父图生成的响应缩减为一个简洁的总结
def subgraph_node_1(state: SubgraphState):
    system_prompt = """
    Please summary the content you receive to 50 words or less
    """
    messages = state['final_answer']  # 这里接收父图传递过来的响应
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"summary_answer": response}

# 第二个节点：根据完整的响应及其总结进行综合的评分
def subgraph_node_2(state: SubgraphState):
    messages = f"""
    This is the full content of what you received：{state["final_answer"]} \n
    This information is summarized for the full content:{state["summary_answer"]}
    Please rate the text and summary information, returning a scale of 1 to 10. Note: Only the score value needs to be returned.
    """
    response = llm.invoke([HumanMessage(content=messages)])
    # 发送共享状态密钥（'final_answer'）的更新
    return {"final_answer": response.content}

# ============================================================
# 5. 定义子图的图结构并且进行编译
# ============================================================
from langgraph.graph import START, StateGraph

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()

# ============================================================
# 6. 定义父图的图结构，并将子图作为节点添加至父图
# ============================================================
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node)

# 将编译后的子图作为一个节点添加到父图中
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()

# ============================================================
# 7. 测试运行
# ============================================================
print("=" * 50)
print("案例：Subgraphs 共享状态键通信")
print("=" * 50)

# 测试1：基本调用
import asyncio

async def test_basic():
    print("\n--- 测试1：基本调用 ---")
    async for chunk in graph.astream({"user_input": "我现在想学习大模型，应该关注哪些技术？"}, stream_mode='values'):
        print(chunk)

asyncio.run(test_basic())

# 测试2：查看子图输出
async def test_with_subgraphs():
    print("\n--- 测试2：查看子图输出 ---")
    async for chunk in graph.astream({"user_input": "如何理解RAG？"}, stream_mode='values', subgraphs=True):
        print(chunk)

asyncio.run(test_with_subgraphs())

print("\n" + "=" * 50)
print("案例说明：")
print("=" * 50)
print("""
本案例实现了父图和子图借助共享的状态键（final_answer）进行通信。

关键点：
1. 父图中的 final_answer 状态键被子图共享
2. 子图可以读取和更新父图的共享状态
3. 这种通信模式是多代理架构的底层构建模式

通信流程：
用户输入 -> 父图node_1处理 -> 子图subgraph处理（读取和更新final_answer）-> 返回结果
""")