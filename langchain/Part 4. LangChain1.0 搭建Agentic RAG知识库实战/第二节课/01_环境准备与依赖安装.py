# -*- coding: utf-8 -*-
"""
【案例 1】环境准备与依赖安装
================================

本案例展示 LangChain RAG 开发的环境准备工作，包括模型加载和依赖安装。

前置要求：
1. Python 3.10+
2. 安装必要的包

安装命令：
```bash
pip install langchain langchain-community langchain-deepseek langchain-openai
pip install rank_bm25 faiss-cpu
pip install python-dotenv
```

要点：
1. 了解 RAG 开发所需的环境
2. 掌握模型初始化方法
3. 理解 Embeddings 的作用
"""

# ============================================================
# 1. 检查 Python 版本
# ============================================================
import sys

print("=" * 60)
print("案例 1: 环境准备与依赖安装")
print("=" * 60)

print(f"\nPython 版本: {sys.version}")
print(f"Python 版本信息: {sys.version_info}")

# ============================================================
# 2. 检查已安装的 LangChain 相关包
# ============================================================
print("\n【已安装的 LangChain 相关包】")
print("-" * 50)

import pkg_resources

langchain_packages = [
    "langchain",
    "langchain-core",
    "langchain-community",
    "langchain-deepseek",
    "langchain-openai",
    "langchain-text-splitters",
    "langchain-classic",
    "faiss-cpu",
    "rank-bm25",
    "pydantic",
    "dotenv"
]

for pkg_name in langchain_packages:
    try:
        version = pkg_resources.get_distribution(pkg_name).version
        print(f"  ✅ {pkg_name}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"  ❌ {pkg_name}: 未安装")

# ============================================================
# 3. 环境说明
# ============================================================
print("\n" + "=" * 60)
print("环境说明")
print("=" * 60)

print("""
【RAG 开发所需的核心组件】

1. 模型层
   - LLM（大语言模型）：DeepSeek / OpenAI / Anthropic
   - Embeddings（嵌入模型）：text-embedding-3-small / bge

2. 数据层
   - Document Loaders：加载各类文档
   - Text Splitters：切分文档
   - Vector Stores：向量数据库（FAISS/Chroma/Pinecone）
   - Retrievers：检索器（向量检索/关键词检索/混合检索）

3. 应用层
   - Prompt Templates：提示词模板
   - Chain：LCEL 链式调用
   - Agent：智能体编排

【推荐配置】
  - LLM: DeepSeek Chat（性价比高，支持中文）
  - Embeddings: text-embedding-3-small（OpenAI）
  - Vector Store: FAISS（本地部署，简单易用）
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)