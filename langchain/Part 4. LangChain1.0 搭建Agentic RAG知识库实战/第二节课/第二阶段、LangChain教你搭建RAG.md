## <center>第二阶段、LangChain教你搭建RAG

### 1. 环境准备与依赖安装

#### 1.1 环境要求

| 要求 | 说明 |
|------|------|
| Python | 3.10+ |
| 模型 | LLM (DeepSeek/OpenAI) + Embeddings |

#### 1.2 安装命令

```bash
pip install langchain langchain-community langchain-deepseek langchain-openai
pip install rank_bm25 faiss-cpu
pip install python-dotenv
```

#### 1.3 核心组件

| 层级 | 组件 |
|------|------|
| 模型层 | LLM (DeepSeek Chat)、Embeddings (text-embedding-3-small) |
| 数据层 | Document Loaders、Text Splitters、Vector Stores、Retrievers |
| 应用层 | Prompt Templates、Chain (LCEL)、Agent |

### 2. 加载模型与配置

#### 2.1 LLM 与 Embeddings

**LLM（大语言模型）**：理解用户问题，生成回答

**Embeddings（嵌入模型）**：将文本转换为向量，用于相似度检索

#### 2.2 模型加载

```python
from langchain_deepseek import ChatDeepSeek
from langchain_openai.embeddings import OpenAIEmbeddings

# 加载 LLM
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0
)

# 加载 Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

#### 2.3 LLM vs Embeddings 对比

| 维度 | LLM | Embeddings |
|------|-----|------------|
| 全称 | Large Language Model | Text Embeddings |
| 作用 | 理解和生成文本 | 将文本转为向量 |
| 输入 | 文本（用户问题） | 文本（文档/查询） |
| 输出 | 文本（回答） | 向量（用于相似度计算） |
| 调用场景 | 生成回答时 | 存储和检索文档时 |

#### 2.4 RAG 中的使用场景

```
1. 文档入库阶段（使用 Embeddings）
   文档 → Embeddings → 向量 → 存储到向量数据库

2. 用户查询阶段（使用 Embeddings + LLM）
   用户问题 → Embeddings → 向量 → 相似度检索 → 检索相关文档

3. 回答生成阶段（使用 LLM）
   用户问题 + 检索文档 → LLM → 生成回答
```

### 3. 文档加载与切分

#### 3.1 文档加载器

| 加载器 | 用途 |
|--------|------|
| TextLoader | 纯文本文件 |
| Docx2txtLoader | Word 文档 |
| PDFPlumberLoader | PDF 文件 |

```python
from langchain_community.document_loaders import TextLoader, Docx2txtLoader

# 读取文本文件
loader = TextLoader("sample_document.txt", encoding="utf-8")
documents = loader.load()
```

#### 3.2 Document 对象结构

```python
Document(
    page_content="这是文档的内容文本...",
    metadata={"source": "document.txt", "page": 1}
)
```

#### 3.3 文档切分器

**RecursiveCharacterTextSplitter**：递归字符切分

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,                      # 文本块大小（字符数）
    chunk_overlap=50,                    # 文本块重叠大小
    separators=["\n\n", "\n", " ", ""]   # 切分符优先级
)
```

#### 3.4 切分参数详解

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| chunk_size | 每个文本块的最大字符数 | 300-1000 字符 |
| chunk_overlap | 相邻文本块之间的重叠字符数 | chunk_size 的 10-20% |
| separators | 按优先级尝试的切分符 | `\n\n`, `\n`, ` `, `` |

### 4. 向量数据库与检索器

#### 4.1 向量数据库

| 数据库 | 特点 |
|--------|------|
| FAISS | Facebook AI Similarity Search，本地部署 |
| Chroma | 嵌入式向量数据库 |
| Pinecone | 云端向量数据库 |

```python
from langchain_community.vectorstores import FAISS

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
    allow_dangerious_deserialization=True
)
```

#### 4.2 检索器类型

| 类型 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 向量检索 | 语义相似度 | 理解语义、相似词匹配 | 对关键词不敏感 |
| BM25检索 | 关键词TF-IDF | 精确匹配关键词 | 不理解语义 |
| 混合检索 | 向量+关键词加权 | 结合两者优点 | 需调参权重 |

#### 4.3 创建检索器

```python
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
```

#### 4.4 检索流程

```
【向量检索流程】
用户问题 → Embeddings → 向量 → FAISS搜索 → 相似文档

【BM25检索流程】
用户问题 → TF-IDF分析 → 关键词打分 → 排序 → 相关文档

【混合检索流程】
用户问题 → 向量检索 → [权重0.5]
         → BM25检索 → [权重0.5]
         → 加权合并 → 最终结果
```

### 5. 基础RAG链构建

#### 5.1 LCEL 组件

| 组件 | 用途 |
|------|------|
| ChatPromptTemplate | 聊天提示词模板 |
| RunnablePassthrough | 传递输入 |
| StrOutputParser | 输出字符串解析器 |

#### 5.2 提示模板

```python
from langchain_core.prompts import ChatPromptTemplate

template = """你是一个专业的问答助手。请根据以下提供的上下文信息来回答用户的问题。
如果上下文中没有相关信息，请诚实地告诉用户你不知道，不要编造答案。

上下文信息：
{context}

问题: {question}

回答:"""

prompt = ChatPromptTemplate.from_template(template)
```

#### 5.3 文档格式化

```python
def format_docs(docs):
    '''将多个文档合并为一个字符串'''
    return "\n\n".join(doc.page_content for doc in docs)
```

#### 5.4 构建完整 RAG 链

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 完整 RAG 链
rag_chain = (
    {
        "context": ensemble_retriever | format_docs,  # 检索到的文档
        "question": RunnablePassthrough()              # 用户问题（透传）
    }
    | prompt                                          # 提示词模板
    | model                                           # LLM 模型
    | StrOutputParser()                               # 输出解析
)

# 执行完整 RAG
answer = rag_chain.invoke("LangChain是什么？")
```

#### 5.5 LCEL 语法

| 语法 | 说明 | 示例 |
|------|------|------|
| A \| B | 将 A 的输出传给 B | retriever \| format_docs |
| {k: v} | 创建字典 | {"context": ..., "question": ...} |
| RunnablePassthrough() | 透传输入 | RunnablePassthrough() |

**核心原则**：
- 一切皆 Runnable
- 可以链式调用
- 支持 stream/batch/invoke 多种调用方式

### 6. 拓展思考

#### 6.1 Embeddings 的深层技术

&emsp;&empsp;为什么 Embeddings 如此重要？因为它解决了"文本相似度"的计算问题：

**词袋模型 vs 向量表示**：
- 词袋模型（TF-IDF）：词出现的频率，丢失语义和顺序
- Embeddings：通过深度学习将文本映射到稠密向量，保留语义信息

**Embeddings 的质量评估**：

| 维度 | 说明 | 评估方法 |
|------|------|---------|
| 语义保留 | 相似的词/句向量接近 | Cosine Similarity |
| 下游任务 | 在实际任务中表现 | 微调测试 |
| 维度效率 | 维度与效果的平衡 | 不同维度对比 |

**常用 Embeddings 模型对比**：

| 模型 | 维度 | 特点 | 适用场景 |
|------|------|------|---------|
| text-embedding-3-small | 1536 | OpenAI 最新小型化模型 | 成本敏感 |
| text-embedding-3-large | 3072 | OpenAI 最新大型号 | 最高质量 |
| text-embedding-ada-002 | 1536 | 经典稳定版 | 稳定优先 |
| BGE-large-zh | 1024 | 国产优秀，中文优化 | 中文场景 |

#### 6.2 向量数据库的底层原理

&emsp;&empsp;向量数据库是 RAG 系统的核心，理解其原理有助于优化检索效果：

**向量索引算法**：

| 算法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| FLAT | 暴力全量搜索 | 100% 召回率 | 慢 |
| IVF | 聚类后搜索 | 加速 | 精度损失 |
| HNSW | 图索引 | 极速 | 内存占用高 |
| PQ | 向量量化 | 压缩率高 | 精度下降 |

**FAISS 中的索引类型选择**：

```python
# 简单场景：直接暴力搜索
index = faiss.IndexFlatIP(dimension)  # Inner Product = Cosine Similarity

# 中等规模：IVF 倒排索引
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# 大规模场景：HNSW 图索引
index = faiss.IndexHNSWFlat(dimension, m)

# 内存敏感：Product Quantization
index = faiss.IndexPQ(dimension, m, nbits)
```

#### 6.3 文档切分的深层策略

&emsp;&empsp;文档切分看似简单，实际上对检索效果影响巨大：

**切分策略的选择**：

| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 固定大小 | 简单 | 可能切断句子 | 通用场景 |
| 按段落 | 保留语义 | 大小不一 | 结构化文档 |
| 递归切分 | 智能边界 | 复杂 | 混合文档 |
| Semantic Chunking | 最语义化 | 计算成本高 | 精确检索 |

**语义切分算法示例**：
```python
def semantic_chunk(text, threshold=0.7):
    sentences = split_into_sentences(text)
    embeddings = [embed(s) for s in sentences]

    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = cosine_similarity(embeddings[i-1], embeddings[i])
        if similarity > threshold:
            current_chunk.append(sentences[i])
        else:
            chunks.append(current_chunk)
            current_chunk = [sentences[i]]

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
```

#### 6.4 RAG 系统的性能优化

&emsp;&empsp;在生产环境中，RAG 系统的性能优化是关键：

**检索优化**：

1. **混合检索**（BM25 + 向量）：
```python
from langchain.retrievers import EnsembleRetriever

# BM25 检索器
bm25_retriever = BM25Retriever.from_texts(texts)

# 向量检索器
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 混合检索
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # BM25 权重 30%，向量检索权重 70%
)
```

2. **重排序（Reranker）**：
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# 在初步检索后重排序
reranker = CohereRerank(model="rerank-multilingual-v3.0", top_n=3)
compressor = DocumentsCompressorPipeline([reranker])
rerank_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)
```

#### 6.5 RAG 系统的评估体系

&emsp;&empsp;如何评估 RAG 系统的效果？业界有成熟的评估框架：

**RAGAS 评估指标**：

| 指标 | 衡量内容 | 计算方式 |
|------|---------|---------|
| Faithfulness | 答案是否忠实于检索内容 | 答案中来自检索内容的比例 |
| Answer Relevancy | 答案与问题的相关性 | 生成答案与问题的语义相似度 |
| Context Precision | 检索内容的精确度 | 相关内容在检索结果中的排名 |
| Context Recall | 检索内容的召回率 | 检索内容覆盖标准答案的比例 |

**评估代码示例**：
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# 准备测试数据集
test_dataset = [
    {
        "question": "LangChain 是什么？",
        "answer": "LangChain 是一个构建 LLM 应用的框架...",
        "contexts": [" LangChain 是一个框架...", "它支持 Agent 开发..."]
    }
]

# 执行评估
result = evaluate(
    test_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)
```