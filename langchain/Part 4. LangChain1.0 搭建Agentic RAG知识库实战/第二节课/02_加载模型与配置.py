# -*- coding: utf-8 -*-
"""
【案例 2】加载模型 - LLM 与 Embeddings
========================================

本案例展示如何加载 LLM（大语言模型）和 Embeddings（嵌入模型）。

两种模型的作用：
1. LLM：理解用户问题，生成回答
2. Embeddings：将文本转换为向量，用于相似度检索

要点：
1. 掌握 ChatDeepSeek 的初始化方法
2. 掌握 OpenAIEmbeddings 的初始化方法
3. 理解两种模型的不同用途
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: 加载模型 - LLM 与 Embeddings")
print("=" * 60)

# ============================================================
# 2. 加载 LLM（大语言模型）
# ============================================================
print("\n【加载 LLM】")
print("-" * 50)

from langchain_deepseek import ChatDeepSeek
from langchain_openai.embeddings import OpenAIEmbeddings

# 使用 DeepSeek 模型（避免 OpenAI 地区限制问题）
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0
)

print(f"LLM 模型: {model.model_name if hasattr(model, 'model_name') else 'deepseek-chat'}")
print(f"LLM 类型: {type(model).__name__}")

# ============================================================
# 3. 加载 Embeddings（嵌入模型）
# ============================================================
print("\n【加载 Embeddings】")
print("-" * 50)

# 使用 OpenAI 的嵌入模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

print(f"Embeddings 模型: {embeddings.model}")
print(f"Embeddings 类型: {type(embeddings).__name__}")

# ============================================================
# 4. 测试模型调用
# ============================================================
print("\n【测试 LLM 调用】")
print("-" * 50)

# 测试 LLM
response = model.invoke("你好，请简要介绍一下自己。")
print(f"LLM 回复: {response.content[:100]}...")

# ============================================================
# 5. 测试 Embeddings
# ============================================================
print("\n【测试 Embeddings】")
print("-" * 50)

# 测试 Embeddings
text = "这是一个测试文本，用于生成向量表示"
vector = embeddings.embed_query(text)
print(f"文本: {text}")
print(f"向量维度: {len(vector)}")
print(f"向量前5个值: {vector[:5]}")

# ============================================================
# 6. 两种模型的区别
# ============================================================
print("\n" + "=" * 60)
print("LLM vs Embeddings 对比")
print("=" * 60)

对比表 = """
| 维度         | LLM                    | Embeddings              |
|-------------|----------------------|----------------------|
| 全称         | Large Language Model | Text Embeddings       |
| 作用         | 理解和生成文本        | 将文本转为向量         |
| 输入         | 文本（用户问题）       | 文本（文档/查询）     |
| 输出         | 文本（回答）          | 向量（用于相似度计算）|
| 调用场景     | 生成回答时           | 存储和检索文档时       |
| 成本         | 较高                  | 较低                  |
"""
print(对比表)

# ============================================================
# 7. RAG 中的使用场景
# ============================================================
print("\n【RAG 中的使用场景】")
print("-" * 50)

print("""
RAG 工作流程：

1. 文档入库阶段（使用 Embeddings）
   文档 → Embeddings → 向量 → 存储到向量数据库

2. 用户查询阶段（使用 Embeddings + LLM）
   用户问题 → Embeddings → 向量 → 相似度检索 → 检索相关文档

3. 回答生成阶段（使用 LLM）
   用户问题 + 检索文档 → LLM → 生成回答

注意：
  - Embeddings 在文档入库和检索时各用一次
  - LLM 只在最后生成回答时使用
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)