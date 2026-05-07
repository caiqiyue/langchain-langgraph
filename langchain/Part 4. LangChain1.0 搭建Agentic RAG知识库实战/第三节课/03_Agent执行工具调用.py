# -*- coding: utf-8 -*-
"""
【案例 3】Agent 执行与工具调用
================================

本案例展示如何创建 Agent 并执行工具调用。

Agent 创建步骤：
1. 准备工具列表
2. 初始化 LLM
3. 配置 checkpointer（可选）
4. 调用 create_agent
5. 执行 stream/invoke

执行模式：
- stream：流式输出，实时看到中间步骤
- invoke：完整执行，返回最终结果

要点：
1. 掌握 create_agent 的使用方法
2. 理解 stream 和 invoke 的区别
3. 学会观察 Agent 的决策过程
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 3: Agent 执行与工具调用")
print("=" * 60)

# ============================================================
# 2. 创建 Agent
# ============================================================
print("\n【创建 Agent】")
print("-" * 50)

print("""
from typing import TypedDict
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 定义上下文类型
class Context(TypedDict):
    user_role: str

# 创建 Agent
agent = create_agent(
    tools=tools,                    # 工具列表
    model=model,                    # LLM 模型
    debug=False,                    # 调试模式
    checkpointer=InMemorySaver(),   # 状态持久化
    context_schema=Context           # 上下文类型
)
""")

# ============================================================
# 3. 执行 Agent
# ============================================================
print("\n【执行 Agent】")
print("-" * 50)

print("""
# 配置线程 ID（用于状态持久化）
config = {"configurable": {"thread_id": "test-thread-001"}}

# 执行 Agent
for event in agent.stream(
    {"messages": [{"role": "user", "content": "LangChain支持哪些模型？"}]},
    config=config,
    stream_mode="values",
    context={"user_role": "大模型工程师"}
):
    if "messages" in event:
        last_msg = event["messages"][-1]
        if last_msg.type == "ai":
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                print(f"🤖 决策: 调用 {last_msg.tool_calls[0]['name']}")
            elif last_msg.content:
                print(f"💬 回复: {last_msg.content}")
""")

# ============================================================
# 4. stream vs invoke
# ============================================================
print("\n【stream vs invoke】")
print("-" * 50)

对比 = """
| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| stream | 流式输出 | 实时看到中间步骤 | 代码复杂 |
| invoke | 完整执行 | 代码简单 | 等待完成才能看到结果 |
"""
print(对比)

# ============================================================
# 5. 执行流程图
# ============================================================
print("\n【执行流程图】")
print("-" * 50)

print("""
【Agent 执行流程】

用户输入: "LangChain支持哪些模型？"
    │
    ▼
┌─────────────────────────────────────────────┐
│  Agent 接收消息                              │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  LLM 分析用户问题                            │
│  → 决策：需要调用工具获取信息               │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  调用 query_retrieval_knowledge 工具        │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  检索 LangChain 知识库                      │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  LLM 收到检索结果，生成回答                  │
└─────────────────────────────────────────────┘
    │
    ▼
最终回复: "LangChain 支持多种模型，包括..."
""")

# ============================================================
# 6. 观察工具调用
# ============================================================
print("\n【观察工具调用】")
print("-" * 50)

print("""
# 复杂问题测试
query = "比较RAG和Agentic RAG的区别，并推荐使用场景"

执行过程：
  1. LLM 分析问题
  2. 决定先调用知识库工具获取技术细节
  3. 收到检索结果
  4. 判断是否需要补充信息
  5. 综合分析生成最终回答

观察要点：
  - tool_calls：LLM 决定调用的工具
  - tool_call_id：工具调用 ID
  - tool 输出：工具返回的结果
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)