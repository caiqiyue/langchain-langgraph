# -*- coding: utf-8 -*-
"""
【案例 2】将 RAG 封装为 Tool
================================

本案例展示如何将 RAG 检索功能封装为 Tool，
使 Agent 能够通过 LLM 决策来调用检索。

封装步骤：
1. 定义工具函数
2. 定义输入参数 Schema
3. 编写工具描述（至关重要）
4. 使用 StructuredTool.from_function 创建工具

工具描述的四大要素：
1. 核心功能：工具做什么
2. 适用范围：什么时候用
3. 返回格式：返回什么
4. 限制说明：什么情况下不能用

要点：
1. 学会定义工具函数
2. 掌握编写有效工具描述的方法
3. 理解 StructuredTool.from_function 的用法
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: 将 RAG 封装为 Tool")
print("=" * 60)

# ============================================================
# 2. 定义工具函数
# ============================================================
print("\n【定义工具函数】")
print("-" * 50)

print("""
from pydantic import BaseModel, Field

# 定义工具输入参数
class QAWithRetrievalArgs(BaseModel):
    query: str = Field(description="用户的问题")

def query_retrieval_knowledge(query: str) -> str:
    \"\"\"
    一个基于 LangChain 知识库检索的问答工具。
    专门用于回答与 LangChain 相关的技术问题。

    ⚠️ 重要：此工具仅适用于 LangChain 相关问题！
    如果问题与 LangChain 无关，请使用网络搜索工具。
    \"\"\"
    # 检查是否与 LangChain 相关
    langchain_keywords = ['langchain', 'langgraph', 'langsmith', ...]
    query_lower = query.lower()
    is_related = any(kw in query_lower for kw in langchain_keywords)

    if not is_related:
        return "❌ 检测到此问题与 LangChain 知识库无关..."

    # 执行检索
    retrieval_chain = ensemble_retriever | format_docs
    docs = retrieval_chain.invoke(query)

    return docs

# 创建 StructuredTool
qa_tool = StructuredTool.from_function(
    func=query_retrieval_knowledge,
    name="query_retrieval_knowledge",
    description="...（详见下方）",
    args_schema=QAWithRetrievalArgs,
    return_direct=False
)
""")

# ============================================================
# 3. 工具描述的重要性
# ============================================================
print("\n【工具描述的重要性】")
print("-" * 50)

print("""
工具描述决定了 LLM 是否正确调用工具。

好描述示例：
\"\"\"
🎯 专用于回答 LangChain 技术相关问题的知识库检索工具。

适用范围：
  - LangChain、LangGraph、LangSmith、LCEL 相关技术
  - Agent、Retriever、Embedding、RAG 等概念
  - Prompt 工程、模型配置等

⚠️ 限制：仅包含 LangChain 相关文档

返回格式：
  - 返回检索到的相关文档片段
  - 如果没有找到相关内容，返回提示信息

如果问题与 LangChain 无关，请使用网络搜索工具 tavily_search_results_json。
\"\"\"

描述要点：
1. 明确核心功能
2. 列出适用范围
3. 说明限制条件
4. 指定返回格式
5. 提示替代方案
""")

# ============================================================
# 4. 完整工具定义
# ============================================================
print("\n【完整工具定义示例】")
print("-" * 50)

print("""
# 知识库检索工具
qa_tool = StructuredTool.from_function(
    func=query_retrieval_knowledge,
    name="query_retrieval_knowledge",
    description=(
        "🎯 专用于回答 LangChain 技术相关问题的知识库检索工具。\\n"
        "适用范围：LangChain、LangGraph、LangSmith、LCEL、Agent、RAG 等相关技术。\\n"
        "⚠️ 限制：仅包含 LangChain 相关文档，不适用于其他领域问题。\\n"
        "如果问题与 LangChain 无关，请使用网络搜索工具 tavily_search_results_json。"
    ),
    args_schema=QAWithRetrievalArgs,
    return_direct=False
)

# 网络搜索工具
web_search = TavilySearch(max_results=2)

# 敏感知识库工具
sensitive_knowledge_tool = StructuredTool.from_function(
    func=query_sensitive_knowledge,
    name="query_sensitive_knowledge",
    description=(
        "🔴 高风险操作：敏感知识库查询工具\\n"
        "用于查询机密文档、内部资料、敏感信息等受限数据。\\n"
        "⚠️ 警告：此操作需要人工审核批准！\\n"
        ...
    ),
    args_schema=SensitiveKnowledgeQueryArgs,
    return_direct=False
)

# 工具列表
tools = [qa_tool, web_search, sensitive_knowledge_tool]
""")

# ============================================================
# 5. 工具描述编写检查清单
# ============================================================
print("\n【工具描述检查清单】")
print("-" * 50)

检查清单 = """
□ 1. 功能描述：工具做什么？
□ 2. 适用范围：什么时候用？
□ 3. 限制条件：什么情况下不能用？
□ 4. 返回格式：返回什么？
□ 5. 依赖说明：需要什么前提条件？
□ 6. 替代方案：不能用什么代替？
□ 7. 注意事项：有什么特别提醒？
"""
print(检查清单)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)