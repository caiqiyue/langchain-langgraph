# -*- coding: utf-8 -*-
"""
【案例 2】Subgraphs 无共享状态键通信
============================================

本案例展示如何使用 LangGraph 实现父子图之间在没有共享状态键的情况下进行通信

要点：
1. 父图和子图的状态模式中没有共同的键（通道）
2. 需要定义状态转换函数，在调用子图前转换输入，返回前转换输出
3. 父图 -> 转换 -> 子图 -> 转换 -> 父图的信息传递流程

案例说明：
设计一个评分系统，与案例1类似但更灵活：
- 父图负责处理用户输入
- 子图完全独立处理自己的逻辑（response_answer, summary_answer, score）
- 通过转换函数在父子图之间传递数据
"""

# ============================================================
# 1. 环境配置
# ============================================================
# 如果用开源模型，可以用Ollama 接入
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url="http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5:72b",
)

# ============================================================
# 2. 定义父图的状态模式和节点
# ============================================================
from typing import TypedDict

# 定义父图中的状态
class ParentState(TypedDict):
    user_input: str   # 用来接收用户的输入
    final_answer: str   # 用来存储大模型针对用户输入的响应

# 父图第一个节点：使用大模型处理用户输入
def parent_node_1(state: ParentState):
    response = llm.invoke(state["user_input"])
    return {"final_answer": response}

# ============================================================
# 3. 定义子图的状态模式（完全独立）
# ============================================================
# 定义子图中的状态
class SubgraphState(TypedDict):
    # 以下三个 key 都是 子图 (subgraph) 中独享的
    response_answer: str   # 接收父图传递过来的响应
    summary_answer: str    # 文本摘要
    score: str            # 评分结果

# ============================================================
# 4. 定义子图的节点逻辑
# ============================================================
from langchain_core.messages import SystemMessage, HumanMessage

# 定义第一个节点，用于接收父图中的响应并且做文本摘要
def subgraph_node_1(state: SubgraphState):
    system_prompt = """
    Please summary the content you receive to 50 words or less
    """
    messages = state['response_answer']  # 这里接收父图传递过来的响应
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"summary_answer": response}

# 定义第二个节点：对完整响应及其总结进行评分
def subgraph_node_2(state: SubgraphState):
    messages = f"""
    This is the full content of what you received：{state["response_answer"]} \n
    This information is summarized for the full content:{state["summary_answer"]}
    Please rate the text and summary information, returning a scale of 1 to 10. Note: Only the score value needs to be returned.
    """
    response = llm.invoke([HumanMessage(content=messages)])
    # 发送评分结果
    return {"score": response.content}

# ============================================================
# 5. 定义子图并编译
# ============================================================
from langgraph.graph import START, StateGraph

subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()

# ============================================================
# 6. 定义父图与子图之间的转换节点（关键！）
# ============================================================
# parent_node_2 用来连接父图与子图之间的网络通信
# 它通过将父节点与子节点的状态做转化来达到此目的
def parent_node_2(state: ParentState):
    # 将父图中的状态转换为子图状态
    response = subgraph.invoke({"response_answer": state["final_answer"]})
    # 将子图状态再转换回父状态
    return {"final_answer": response["score"]}

# ============================================================
# 7. 定义父图的图结构
# ============================================================
builder = StateGraph(ParentState)
builder.add_node("node_1", parent_node_1)

# 注意，我们使用的不是编译后的子图，而是调用子图的 'parent_node_2' 函数
builder.add_node("node_2", parent_node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()

# ============================================================
# 8. 测试运行
# ============================================================
print("=" * 50)
print("案例：Subgraphs 无共享状态键通信")
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
    all_chunk = []
    async for chunk in graph.astream({"user_input": "什么是机器学习？"}, stream_mode='values', subgraphs=True):
        all_chunk.append(chunk)
    print("最终结果:", all_chunk[-1][1]["final_answer"])

asyncio.run(test_with_subgraphs())

print("\n" + "=" * 50)
print("案例说明：")
print("=" * 50)
print("""
本案例实现了父图和子图在完全没有共享状态键的情况下的通信。

关键点：
1. 子图状态（SubgraphState）完全独立于父图状态（ParentState）
2. 通过 parent_node_2 函数进行状态转换
3. 调用子图前：将父图状态转换为子图输入格式
4. 返回结果前：将子图输出转换回父图状态格式

这种模式是最常见的，也是灵活性最高的子图通信方式。
""")