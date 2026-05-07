# -*- coding: utf-8 -*-
"""
【案例 3】文档加载与切分
==========================

本案例展示如何使用 LangChain 的 Document Loaders 加载文档，
以及如何使用 Text Splitters 切分文档。

文档加载器：
- TextLoader：加载纯文本文件
- Docx2txtLoader：加载 Word 文档
- PDFPlumberLoader：加载 PDF 文件

文档切分器：
- RecursiveCharacterTextSplitter：递归字符切分

切分参数：
- chunk_size：文本块大小
- chunk_overlap：文本块重叠大小

要点：
1. 掌握多种文档加载方法
2. 理解切分参数的作用
3. 学会配置 RecursiveCharacterTextSplitter
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 3: 文档加载与切分")
print("=" * 60)

# ============================================================
# 2. 导入文档加载器
# ============================================================
print("\n【文档加载器】")
print("-" * 50)

from langchain_community.document_loaders import TextLoader, Docx2txtLoader

# 注意：这里仅展示代码结构，需要实际文件才能运行
print("""
# 读取文本文件
loader = TextLoader("sample_document.txt", encoding="utf-8")
documents = loader.load()

# 读取 Word 文档
loader = Docx2txtLoader("document.docx")
documents = loader.load()

# 读取 PDF 文件
from langchain_community.document_loaders import PDFPlumberLoader
loader = PDFPlumberLoader("document.pdf")
documents = loader.load()
""")

# ============================================================
# 3. 文档结构说明
# ============================================================
print("\n【Document 对象结构】")
print("-" * 50)

print("""
LangChain 的 Document 对象包含两个主要属性：

document.page_content  # 文档内容（文本）
document.metadata       # 元数据（来源、页码等）

示例：
Document(
    page_content="这是文档的内容文本...",
    metadata={"source": "document.txt", "page": 1}
)
""")

# ============================================================
# 4. 导入文档切分器
# ============================================================
print("\n【文档切分器】")
print("-" * 50)

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 定义文档切分器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,                      # 文本块大小（字符数）
    chunk_overlap=50,                    # 文本块重叠大小
    separators=["\n\n", "\n", " ", ""]   # 切分符优先级
)

print(f"切分器配置:")
print(f"  chunk_size: 500（每个文本块最多500字符）")
print(f"  chunk_overlap: 50（相邻块重叠50字符）")
print(f"  separators: [\\n\\n, \\n, ' ', '']（按优先级尝试切分）")

# ============================================================
# 5. 切分参数详解
# ============================================================
print("\n【切分参数详解】")
print("-" * 50)

print("""
chunk_size（文本块大小）：
  - 控制每个文本块的最大字符数
  - 太小：丢失上下文；太大：检索精度下降
  - 推荐值：300-1000 字符

chunk_overlap（文本块重叠）：
  - 相邻文本块之间的重叠字符数
  - 作用：避免重要信息被切分点切断
  - 推荐值：chunk_size 的 10-20%

separators（切分符）：
  - 按优先级尝试的切分符列表
  - \n\n：段落分隔（最优先）
  - \n：行分隔
  - " "：单词分隔
  - ""：字符分隔（最后手段）
""")

# ============================================================
# 6. 切分效果示意
# ============================================================
print("\n【切分效果示意】")
print("-" * 50)

print("""
原始文本：
"第一段内容，包含很多文字...\\n\\n第二段内容...\\n\\n第三段内容..."

切分结果（chunk_size=50, chunk_overlap=10）：
┌─────────────────────────┐
│ 块1: 第一段内容...      │ ← 50字符
│     [重叠区域]           │ ← 10字符重叠
├─────────────────────────┤
│     [重叠区域]           │
│ 块2: ...续第一段+第二段  │ ← 50字符
│     [重叠区域]           │
├─────────────────────────┤
│     [重叠区域]           │
│ 块3: ...续第二段+第三段  │ ← 50字符
└─────────────────────────┘
""")

# ============================================================
# 7. 切分代码示例
# ============================================================
print("\n" + "=" * 60)
print("切分代码示例")
print("=" * 60)

print("""
# 假设 documents 是已加载的文档列表
texts = text_splitter.split_documents(documents)

print(f"分割后的文本块数量: {len(texts)}")
print(f"第一个文本块: {texts[0].page_content}")
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)