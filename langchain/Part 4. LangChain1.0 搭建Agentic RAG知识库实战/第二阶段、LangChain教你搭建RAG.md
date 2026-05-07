# <center>第二阶段、LangChain框架搭建RAG

## 一、 环境准备与依赖安装

```python
!python --version```

```python
!pip list | grep langchain```

## 二、加载模型

```python
## 加载模型
from langchain_deepseek import ChatDeepSeek
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

# 加载.env环境变量
load_dotenv(override=True)

# 使用 DeepSeek 模型（避免 OpenAI 地区限制问题）
model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 使用本地嵌入模型（不需要 API 调用）
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

print("✅ 模型加载成功")
# print(model.invoke("Hello, world!"))
# print(embeddings.embed_query("Hello, world!")[:10])```

## 三、文档加载

```python
## 2.文档加载
from langchain_community.document_loaders import TextLoader, Docx2txtLoader

# 读取基础数据文档
loader = TextLoader("sample_document.txt", encoding="utf-8")
documents = loader.load()

# 读取敏感数据文档
sensitive_loader = TextLoader("sensitive_document.txt", encoding="utf-8")
sensitive_documents = sensitive_loader.load()

print(documents[0].page_content)```

## 四、文档切分

```python
## 3.文档切分
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 定义文档切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,                      # 切分文本块大小
    chunk_overlap=50,                    # 文本块重叠大小
    separators=["\n\n", "\n", " ", ""]   # 按照换行符、空格等符号进行切分
)

# 基础数据文档切分
texts = text_splitter.split_documents(documents)

# 敏感数据文档切分
sensitive_texts = text_splitter.split_documents(sensitive_documents)

print(f"分割后的文本块数量: {len(texts)}")
print(texts[0].page_content)```

## 五、文档向量存储与检索


```python
!pip install rank_bm25 faiss-cpu # 或 faiss-gpu```

### 5.1 创建向量存储（Faiss向量数据库）

```python
from langchain_community.vectorstores import FAISS

# ================================1.普通数据入库=================================
# 创建并保存向量数据库，用于普通数据的检索
vector_store = FAISS.from_documents(texts, embeddings)
vector_store.save_local("faiss_index")

# 从本地加载向量数据库
vector_store = FAISS.load_local(
    "faiss_index",                        # 本地索引文件路径名称
    embeddings,                           # 嵌入模型
    allow_dangerous_deserialization=True  # 必须要加这个参数，否则会报错，允许反序列化
)
print("✅ 普通数据向量数据库创建并保存成功")

# =================================2.敏感数据入库=================================

# 创建并保存向量数据库，用于敏感数据的检索
sensitive_vector_store = FAISS.from_documents(sensitive_texts, embeddings)
sensitive_vector_store.save_local("sensitive_faiss_index")

# 从本地加载向量数据库
sensitive_vector_store = FAISS.load_local(
    "sensitive_faiss_index",                # 本地索引文件路径名称
    embeddings,                             # 嵌入模型
    allow_dangerous_deserialization=True    # 必须要加这个参数，否则会报错，允许反序列化
)
print("✅ 敏感数据向量数据库创建并保存成功")```

### 5.2 加载并创建检索器

```python
# 定义BM25Retriever，是一种基于关键词匹配的检索器
from langchain_community.retrievers import BM25Retriever
# 定义EnsembleRetriever，是一种将多个检索器组合起来的检索器
from langchain_classic.retrievers import EnsembleRetriever

# ================================1.普通数据入库=================================

# 1.创建BM25检索器
bm25_retriever = BM25Retriever.from_documents(texts)
bm25_retriever.k = 3

# 2.创建向量数据库检索器
faiss_retriever = vector_store.as_retriever(
    search_type="similarity",    # 相似度搜索
    search_kwargs={"k": 3}       # 返回top3结果
)

# 3.创建混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers=[faiss_retriever, bm25_retriever],  # 组合faiss和bm25检索器
    weights=[0.5, 0.5]                             # 给faiss和bm25检索器设置权重，分别为0.5
)
print("✅ 普通数据检索器建立成功")

# =================================2.敏感数据入库=================================

# 1.创建BM25检索器
sensitive_bm25_retriever = BM25Retriever.from_documents(sensitive_texts)
sensitive_bm25_retriever.k = 3

# 2.创建向量数据库检索器
sensitive_faiss_retriever = sensitive_vector_store.as_retriever(
    search_type="similarity",    # 相似度搜索
    search_kwargs={"k":3}       # 返回top3结果
)

# 3.创建混合检索器
sensitive_ensemble_retriever = EnsembleRetriever(
    retrievers=[sensitive_faiss_retriever, sensitive_bm25_retriever], # 组合faiss和bm25检索器
    weights=[0.5, 0.5]                   # 给faiss和bm25检索器设置权重，分别为0.5
)
print("✅ 敏感数据检索器建立成功")
```

## 六、 基础RAG链构建

```python
# 导入提示词ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
# 导入 RunnablePassthrough，用于将输入传递给下一个组件
from langchain_core.runnables import RunnablePassthrough
# 导入 StrOutputParser，用于将模型输出解析为字符串
from langchain_core.output_parsers import StrOutputParser

# 1.格式化文档的辅助函数
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 2.创建提示模板
template = """你是一个专业的问答助手。请根据以下提供的上下文信息来回答用户的问题。
如果上下文中没有相关信息，请诚实地告诉用户你不知道，不要编造答案。

上下文信息：
{context}

问题: {question}

回答:"""

prompt = ChatPromptTemplate.from_template(template)

# 3.创建检索链,文本检索阶段，用于将文本检索结果格式化为字符串
chain =  ensemble_retriever | format_docs

# 调用检索链，执行文本检索
retrieval = chain.invoke("LangChain是什么？")
print(f"检索到的内容：{retrieval}")
print("=" * 60)

# 4.创建大模型回答检索链，大模型生成阶段
retrieval_chain = (
    {"context": ensemble_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 调用大模型回答检索链，执行大模型生成
content = retrieval_chain.invoke("LangChain是什么？")
print(f"大模型回复内容：{content}")```
