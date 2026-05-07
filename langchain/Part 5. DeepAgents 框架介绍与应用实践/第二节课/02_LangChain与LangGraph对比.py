# -*- coding: utf-8 -*-
"""
【案例 2】LangChain 与 LangGraph 对比
=====================================

本案例展示 LangChain 和 LangGraph 的核心差异。

LangChain：
- 提供基础组件（Chain, Runnable, Tool）
- 需要自行组装
- 适合定制化需求

LangGraph：
- 基于 LangChain 的扩展
- 提供状态图结构
- 支持循环和分支
- 适合复杂工作流

要点：
1. 理解 LangChain 的积木式设计
2. 理解 LangGraph 的图结构
3. 掌握两种框架的适用场景
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: LangChain 与 LangGraph 对比")
print("=" * 60)

# ============================================================
# 2. LangChain 特点
# ============================================================
print("\n【LangChain 特点】")
print("-" * 50)

print("""
LangChain 是基础组件库：

组件：
  - Prompt：提示词模板
  - Model：语言模型封装
  - Tool：工具定义
  - Chain：链式调用

特点：
  - 高度模块化
  - 灵活组合
  - 需要自行组装
  - 适合底层开发
""")

# ============================================================
# 3. LangGraph 特点
# ============================================================
print("\n【LangGraph 特点】")
print("-" * 50)

print("""
LangGraph 是编排引擎：

核心概念：
  - StateGraph：状态图
  - Node：节点（执行单元）
  - Edge：边（连接关系）

特点：
  - 支持循环（for/while）
  - 支持条件分支
  - 支持多智能体
  - 状态持久化
  - 适合复杂工作流
""")

# ============================================================
# 4. 代码对比
# ============================================================
print("\n【代码对比】")
print("-" * 50)

print("""
【LangChain Chain】
from langchain import LLMChain, PromptTemplate
chain = LLMChain(llm=model, prompt=prompt)

【LangGraph StateGraph】
from langgraph.graph import StateGraph
graph = StateGraph()
graph.add_node("node_name", func)
graph.add_edge("start", "node_name")
graph.add_edge("node_name", "end")
app = graph.compile()
""")

# ============================================================
# 5. 选择依据
# ============================================================
print("\n【选择依据】")
print("-" * 50)

选择依据 = """
| 需求                  | LangChain | LangGraph |
|-----------------------|-----------|-----------|
| 简单链式调用           | ✅        | ✅        |
| 复杂工作流             | ❌        | ✅        |
| 多轮循环              | ❌        | ✅        |
| 状态持久化            | ❌        | ✅        |
| 高度定制化            | ✅        | ❌        |
| 快速开发              | ❌        | 中       |
"""
print(选择依据)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)