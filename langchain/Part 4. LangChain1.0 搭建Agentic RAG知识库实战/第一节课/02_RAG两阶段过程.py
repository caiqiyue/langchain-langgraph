# -*- coding: utf-8 -*-
"""
【案例 2】RAG 两阶段过程 - 知识库构建与问答
==============================================

RAG 分为两个阶段：
阶段一（准备/离线）：数据 → 文档解析 → 切分 → 向量化 → 存储
阶段二（问答/在线）：用户问题 → 向量化 → 检索 → 增强 → 生成

要点：
1. 掌握文档加载和切分
2. 掌握向量数据库存储
3. 掌握检索和生成流程
"""

print("=" * 60)
print("案例 2: RAG 两阶段过程")
print("=" * 60)

# ============================================================
# 1. 阶段一：知识库构建
# ============================================================
print("""
┌─────────────────────────────────────────────────────────────┐
│ 阶段一：知识库构建（离线）                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 数据接入                                                │
│     - 文档加载（TextLoader, DocxLoader, PDFLoader）       │
│                                                             │
│  2. 文档解析                                                │
│     - 文本提取、内容清洗                                      │
│                                                             │
│  3. 文档切分                                                │
│     - RecursiveCharacterTextSplitter                        │
│     - chunk_size, chunk_overlap 参数                        │
│                                                             │
│  4. 向量化                                                  │
│     - Embedding 模型（OpenAIEmbeddings）                    │
│                                                             │
│  5. 存储                                                    │
│     - FAISS / Chroma / Pinecone                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 2. 阶段二：问答流程
# ============================================================
print("\n" + "=" * 60)
print("阶段二：问答流程（在线）")
print("=" * 60)

print("""
┌─────────────────────────────────────────────────────────────┐
│ 阶段二：问答流程（在线）                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 用户提问                                                │
│     "LangChain 是什么？"                                   │
│                                                             │
│  2. 问题向量化                                              │
│     question → embedding → query_vector                    │
│                                                             │
│  3. 相似度检索                                             │
│     query_vector → FAISS → Top-K 相关文档                  │
│                                                             │
│  4. 构建增强提示                                            │
│     context = retrieved_docs + system_prompt + question    │
│                                                             │
│  5. LLM 生成                                                │
│     context → LLM → answer                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 3. 代码示例
# ============================================================
print("\n" + "=" * 60)
print("代码示例")
print("=" * 60)

代码 = """
# 阶段一：构建知识库
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1. 加载文档
loader = TextLoader("knowledge.txt")
documents = loader.load()

# 2. 切分文档
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

# 3. 向量化并存储
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("faiss_index")

# 阶段二：问答
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 4. 加载向量数据库
vectorstore = FAISS.load_local("faiss_index", embeddings)
retriever = vectorstore.as_retriever()

# 5. 检索并生成
docs = retriever.get_relevant_documents("LangChain 是什么？")
context = "\\n".join([doc.page_content for doc in docs])

prompt = ChatPromptTemplate.from_template(
    "基于以下内容回答问题：\\n{context}\\n\\n问题：{question}"
)
"""
print(代码)

print("""
✅ RAG 两阶段总结

阶段一（离线）：
- 文档加载 → 切分 → 向量化 → 存储

阶段二（在线）：
- 问题向量化 → 相似度检索 → 构建增强提示 → LLM 生成

关键参数：
- chunk_size：每个片段的字符数
- chunk_overlap：相邻片段的重叠数
- Top-K：检索返回的文档数量
""")