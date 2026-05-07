# -*- coding: utf-8 -*-
"""
【案例 2】混合检索器配置
===========================

本案例展示如何配置混合检索器 EnsembleRetriever。

配置参数：
- retrievers：检索器列表
- weights：各检索器权重

search_type 选项：
- similarity：相似度检索
- similarity_score_threshold：设置相似度阈值
- MMR：最大边际相关性

MMR（最大边际相关性）：
- 目标：在相关性和多样性间取得平衡
- 原理：每次选择与查询最相似、但与已选文档最不相似的文档

要点：
1. 掌握 EnsembleRetriever 的配置
2. 理解 MMR 的作用
3. 学会调整检索参数
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: 混合检索器配置")
print("=" * 60)

# ============================================================
# 2. 创建检索器
# ============================================================
print("\n【创建检索器】")
print("-" * 50)

print("""
# 1. 创建 BM25 检索器
bm25_retriever = BM25Retriever.from_documents(texts)
bm25_retriever.k = 3

# 2. 创建 FAISS 检索器
faiss_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 3. 创建混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers=[faiss_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)
""")

# ============================================================
# 3. search_type 选项
# ============================================================
print("\n【search_type 选项】")
print("-" * 50)

选项说明 = """
| search_type | 说明 | 适用场景 |
|------------|------|---------|
| similarity | 返回最相似的文档 | 简单检索 |
| similarity_score_threshold | 低于阈值不返回 | 需要过滤低相关性 |
| MMR | 平衡相关性和多样性 | 需要多样化结果 |
"""
print(选项说明)

# ============================================================
# 4. MMR 详解
# ============================================================
print("\n【MMR（最大边际相关性）】")
print("-" * 50)

print("""
MMR 原理：

目标：返回既相关又多样的文档

公式：MMR = argmax_{di ∈ R\\S} [λ × sim(di, Q) - (1-λ) × max_{dj ∈ S} sim(di, dj)]

其中：
  - di：候选文档
  - Q：查询
  - S：已选文档
  - λ：相关性和多样性的平衡系数

示例（k=3, fetch_k=10）：
  1. 初选 10 个候选文档
  2. 选择第 1 个最相关的文档
  3. 选择第 2 个：相关但与已选最不相似的
  4. 选择第 3 个：继续平衡相关性和多样性

配置示例：
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,              # 最终返回 3 个
        "fetch_k": 10,       # 初选 10 个
        "lambda_mult": 0.5   # 0.5 表示平衡
    }
)
""")

# ============================================================
# 5. 参数调整指南
# ============================================================
print("\n【参数调整指南】")
print("-" * 50)

调整指南 = """
| 参数 | 说明 | 调整建议 |
|------|------|---------|
| k | 返回文档数 | 3-10，根据上下文窗口大小 |
| weights | 混合权重 | 通用 0.5/0.5，专业文档降低向量权重 |
| lambda_mult | MMR 平衡 | 0.5 平衡，<0.5 多样，>0.5 相关 |
"""
print(调整指南)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)