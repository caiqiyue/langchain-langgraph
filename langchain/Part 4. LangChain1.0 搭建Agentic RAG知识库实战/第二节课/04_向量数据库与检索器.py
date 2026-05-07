# -*- coding: utf-8 -*-
"""
【案例 4】向量数据库与检索器
===========================

本案例展示如何使用 FAISS 向量数据库存储文档向量，
以及如何创建多种类型的检索器。

向量数据库：
- FAISS：Facebook AI Similarity Search，本地部署
- Chroma：嵌入式向量数据库
- Pinecone：云端向量数据库

检索器类型：
- VectorStore Retriever：向量相似度检索
- BM25 Retriever：关键词检索
- Ensemble Retriever：混合检索（向量+关键词）

要点：
1. 掌握 FAISS 向量数据库的创建和使用
2. 理解向量检索的原理
3. 学会创建混合检索器
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 4: 向量数据库与检索器")
print("=" * 60)

# ============================================================
# 2. 导入向量数据库相关组件
# ============================================================
print("\n【向量数据库】")
print("-" * 50)

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

print("已导入组件:")
print("  - FAISS: 本地向量数据库")
print("  - BM25Retriever: 关键词检索器")
print("  - EnsembleRetriever: 混合检索器")

# ============================================================
# 3. 创建向量数据库
# ============================================================
print("\n【创建 FAISS 向量数据库】")
print("-" * 50)

print("""
# 假设 texts 是切分后的文档列表
# embeddings 是已初始化的嵌入模型

# 创建向量数据库
vector_store = FAISS.from_documents(
    documents=texts,           # 文档列表
    embedding=embeddings       # 嵌入模型
)

# 保存到本地
vector_store.save_local("faiss_index")

# 从本地加载
vector_store = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
""")

# ============================================================
# 4. 创建检索器
# ============================================================
print("\n【创建检索器】")
print("-" * 50)

print("""
# 1. 创建向量数据库检索器
faiss_retriever = vector_store.as_retriever(
    search_type="similarity",      # similarity / MMR
    search_kwargs={"k": 3}        # 返回 top3 结果
)

# 2. 创建 BM25 检索器
bm25_retriever = BM25Retriever.from_documents(texts)
bm25_retriever.k = 3

# 3. 创建混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers=[faiss_retriever, bm25_retriever],
    weights=[0.5, 0.5]           # 各50%权重
)
""")

# ============================================================
# 5. 检索器类型对比
# ============================================================
print("\n【检索器类型对比】")
print("-" * 50)

对比表 = """
| 类型      | 原理           | 优点                    | 缺点              |
|---------|--------------|-----------------------|-----------------|
| 向量检索   | 语义相似度       | 理解语义、相似词匹配        | 对关键词不敏感     |
| BM25检索  | 关键词TF-IDF    | 精确匹配关键词            | 不理解语义        |
| 混合检索   | 向量+关键词加权   | 结合两者优点              | 需调参权重        |
"""
print(对比表)

# ============================================================
# 6. 检索流程图
# ============================================================
print("\n【检索流程】")
print("-" * 50)

print("""
【向量检索流程】
用户问题 → Embeddings → 向量 → FAISS搜索 → 相似文档

【BM25检索流程】
用户问题 → TF-IDF分析 → 关键词打分 → 排序 → 相关文档

【混合检索流程】
用户问题 → 向量检索 → [权重0.5]
         → BM25检索 → [权重0.5]
         → 加权合并 → 最终结果
""")

# ============================================================
# 7. 检索参数说明
# ============================================================
print("\n【检索参数】")
print("-" * 50)

print("""
search_type 选项：
  - similarity：相似度检索，返回最相似的文档
  - similarity_score_threshold：设置相似度阈值
  - MMR（最大边际相关性）：在相关性和多样性间平衡

search_kwargs 选项：
  - k：返回的文档数量
  - fetch_k：初选数量（MMR 使用）
  - lambda_mult：相关性-多样性平衡（MMR 使用）

weights（混合检索）：
  - [0.5, 0.5]：向量和 BM25 各占一半
  - [0.7, 0.3]：更侧重语义相似性
  - [0.3, 0.7]：更侧重关键词匹配
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)