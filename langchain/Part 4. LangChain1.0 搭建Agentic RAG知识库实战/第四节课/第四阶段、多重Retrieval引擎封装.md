## <center>第四阶段、多重Retrieval引擎封装

### 1. BM25与向量检索原理

#### 1.1 BM25 原理

**BM25（Best Matching 25）算法**：

公式：Score(D, Q) = Σ IDF(qi) × (tf(t, D) × (k1 + 1)) / (tf(t, D) + k1 × (1 - b + b × |D|/avgdl))

| 参数 | 说明 |
|------|------|
| TF(t, D) | 词 t 在文档 D 中的词频 |
| IDF(qi) | 逆文档频率 |
| k1, b | 调节参数（通常 k1=1.5, b=0.75） |
| \|D\| | 文档长度 |
| avgdl | 平均文档长度 |

**核心思想**：
- 词在文档中出现越多，越相关
- 但词太常见（the, is）不重要，需要 IDF 抑制
- 长文档会稀释关键词影响，需要长度归一化

#### 1.2 向量检索原理

**向量检索流程**：

```
1. Embedding：将文本转换为向量
   "LangChain 是什么" → [0.12, -0.34, 0.56, ..., 0.78]

2. 索引：将文档向量存入向量数据库
   doc1_vector, doc2_vector, doc3_vector, ...

3. 查询：
   query → embed_query → query_vector
   query_vector 与所有 doc_vector 计算相似度
   返回最相似的 top-k
```

**常用相似度度量**：
- 余弦相似度：cos(θ) = A·B / (|A| × |B|)
- 点积：直接计算向量内积
- 欧氏距离：||A - B||

**FAISS 加速技术**：
- IVF（倒排索引）：先聚类再搜索
- HNSW（层次导航）：图索引快速导航

#### 1.3 BM25 vs 向量检索

| 维度 | BM25 | 向量检索 |
|------|------|---------|
| 原理 | TF-IDF | 语义 Embedding |
| 优点 | 精确匹配关键词 | 理解语义相似 |
| 缺点 | 不理解语义 | 对关键词不精确 |
| 速度 | 快 | 较慢（需向量计算） |
| 适用 | 专业术语、缩写 | 同义词、语义理解 |

### 2. 混合检索器配置

#### 2.1 创建检索器

```python
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import EnsembleRetriever

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
```

#### 2.2 search_type 选项

| search_type | 说明 | 适用场景 |
|------------|------|---------|
| similarity | 返回最相似的文档 | 简单检索 |
| similarity_score_threshold | 低于阈值不返回 | 需要过滤低相关性 |
| MMR | 平衡相关性和多样性 | 需要多样化结果 |

#### 2.3 MMR（最大边际相关性）

**目标**：返回既相关又多样的文档

**公式**：MMR = argmax_{di ∈ R\S} [λ × sim(di, Q) - (1-λ) × max_{dj ∈ S} sim(di, dj)]

| 参数 | 说明 |
|------|------|
| di | 候选文档 |
| Q | 查询 |
| S | 已选文档 |
| λ | 相关性和多样性的平衡系数 |

**示例（k=3, fetch_k=10）**：
1. 初选 10 个候选文档
2. 选择第 1 个最相关的文档
3. 选择第 2 个：相关但与已选最不相似的
4. 选择第 3 个：继续平衡相关性和多样性

**配置示例**：
```python
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,              # 最终返回 3 个
        "fetch_k": 10,       # 初选 10 个
        "lambda_mult": 0.5   # 0.5 表示平衡
    }
)
```

#### 2.4 参数调整指南

| 参数 | 说明 | 调整建议 |
|------|------|---------|
| k | 返回文档数 | 3-10，根据上下文窗口大小 |
| weights | 混合权重 | 通用 0.5/0.5，专业文档降低向量权重 |
| lambda_mult | MMR 平衡 | 0.5 平衡，<0.5 多样，>0.5 相关 |

#### 2.5 混合检索

**原理**：
1. BM25 检索返回结果 A
2. 向量检索返回结果 B
3. 加权合并：Score = w1 × A + w2 × B

**权重选择**：
- [0.5, 0.5]：各占一半
- [0.7, 0.3]：侧重向量（语义理解）
- [0.3, 0.7]：侧重 BM25（精确匹配）

**适用场景**：
- 专业文档：提高 BM25 权重
- 语义复杂：提高向量权重
- 通用场景：各占一半

### 3. 拓展思考

#### 3.1 BM25 的深层数学原理

&emsp;&empsp;BM25 的公式看似复杂，但其背后有清晰的概率解释：

**TF-IDF 的概率基础**：
- IDF 反映了词在整个文档集中的区分度
- 稀有词区分度高，IDF 高
- 常见词（如"的"、"是"）区分度低，IDF 低

**BM25 与语言模型的关系**：

BM25 本质上是词在文档中出现概率的估计：
```
P(t|D) ∝ (tf(t,D) / |D|)  # 词在文档中的频率
P(t|C) ∝ (tf(t,C) / |C|)  # 词在整个语料中的频率

BM25 score ∝ log(P(t|D) / P(t|C))
```

这解释了为什么 BM25 被称为"概率检索模型"。

#### 3.2 向量检索的ANN算法对比

&emsp;&empsp;在 billion 级别数据量下，暴力搜索（FLAT）不可行，需要 ANN（Approximate Nearest Neighbor）算法：

| 算法 | 原理 | 速度 | 精度 | 内存 |
|------|------|------|------|------|
| HNSW | 图索引 | 最快 | 最高 | 高 |
| IVF | 倒排索引 | 快 | 中 | 中 |
| PQ | 向量量化 | 最快 | 较低 | 低 |
| LSH | 局部敏感哈希 | 中 | 中 | 高 |

**HNSW 的分层导航思想**：

```
Layer 2: ● ──── ●          ← 粗粒度，快速导航
              │
Layer 1: ● ── ● ── ● ── ●  ← 中等粒度
              │
Layer 0: ● ● ● ● ● ● ● ●  ← 细粒度，精确搜索
```

**选择建议**：
- 数据量 < 100万 → FLAT 或 HNSW
- 数据量 100万-1亿 → HNSW 或 IVF
- 数据量 > 1亿 → PQ + HNSW

#### 3.3 混合检索的加权策略

&emsp;&empsp;混合检索的权重不是固定的，需要根据场景调整：

**动态权重公式**：
```python
def dynamic_weights(query, retrievers):
    # 检测查询类型
    if is_exact_match_query(query):
        # 精确查询，侧重 BM25
        return {"bm25": 0.7, "vector": 0.3}
    elif is_semantic_query(query):
        # 语义查询，侧重向量
        return {"bm25": 0.3, "vector": 0.7}
    else:
        # 通用查询，平衡
        return {"bm25": 0.5, "vector": 0.5}

def is_exact_match_query(query):
    # 包含引号、专业术语、数量词
    return bool(re.search(r'[""''\d]+', query))

def is_semantic_query(query):
    # 包含"是什么"、"如何"、"为什么"等
    return bool(re.search(r'(是什么|如何|为什么|概念|原理)', query))
```

#### 3.4 MMR 的多样性-相关性权衡

&emsp;&empsp;MMR（最大边际相关）的 `lambda_mult` 参数控制多样性：

```
lambda_mult = 0：只考虑多样性 → 可能返回不相关文档
lambda_mult = 1：只考虑相关性 → 可能返回冗余文档
lambda_mult = 0.5：平衡 → 推荐默认值
```

**可视化理解**：

```
lambda_mult = 0.3（高多样性）:
  doc1 [相关 0.9, 多样 0.1] → 选择
  doc2 [相关 0.7, 多样 0.8] → 选择（多样性高）
  doc3 [相关 0.8, 多样 0.3] → 选择

lambda_mult = 0.7（高相关性）:
  doc1 [相关 0.9, 多样 0.1] → 选择
  doc2 [相关 0.8, 多样 0.3] → 选择（相关性高）
  doc3 [相关 0.7, 多样 0.8] → 可能不选
```

#### 3.5 Reranker 的深度解析

&emsp;&empsp;Reranker 是提升检索质量的关键步骤，位于初步检索之后：

**两阶段检索架构**：
```
Query → [粗召回阶段] → Top-100 → [精排阶段] → Top-10
                        ↓
              向量检索/BM25/混合检索
                                    ↓
                         Cross-Encoder Reranker
```

**为什么需要 Reranker？**

1. **向量检索的局限**：向量模型是"单次前向传播"，无法精排
2. **粗召回的目的**：快速缩小范围
3. **精排的作用**：用更强大的模型重新打分

**Cohere Reranker 的原理**：
```python
# 输入：Query + Top-K 候选文档
# 输出：重新排序后的文档列表

# Cross-Encoder 方式：Query 和 Doc 一起输入
# score = cross_encoder(query, doc_i)
```