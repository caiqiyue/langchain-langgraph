# -*- coding: utf-8 -*-
"""
【案例 4】langchain-community 第三方集成
==========================================

本案例展示 langchain-community 包的典型用法
这是 LangChain 的"功能扩展层"

要点：
1. 文档加载器
2. 向量存储（演示）
3. 第三方 LLM（通义千问）
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 4: langchain-community 第三方集成")
print("=" * 50)

# ============================================================
# 1. 文档加载器
# ============================================================
print("\n1. 文档加载器")
print("-" * 30)
print("""
langchain-community 提供了大量文档加载器：

- TextLoader: 纯文本
- CSVLoader: CSV 文件
- PDFLoader: PDF 文件
- UnstructuredHTMLLoader: HTML 文件
- NotionDBLoader: Notion 数据库
- 等...

文档加载器统一接口：
loader = SomeLoader("path/to/file")
documents = loader.load()

每个 Document 包含：
- page_content: 文本内容
- metadata: 元数据（来源、页码等）
""")

import io
from langchain_community.document_loaders import TextLoader

# 模拟加载文本
sample_text = """
LangChain 是一个用于构建 LLM 应用的框架。

核心组件包括：
1. Models - 统一模型接口
2. Prompts - 提示词模板
3. Chains - 链式调用
4. Agents - 智能体
5. Memory - 对话记忆
"""

loader = TextLoader(io.StringIO(sample_text), encoding="utf-8")
documents = loader.load()

print(f"加载了 {len(documents)} 个文档")
print(f"文档内容长度: {len(documents[0].page_content)} 字符")

# ============================================================
# 2. 第三方 LLM - 通义千问
# ============================================================
print("\n2. 第三方 LLM - 通义千问")
print("-" * 30)

from langchain_community.chat_models.tongyi import ChatTongyi

try:
    qwen = ChatTongyi(model_name="qwen-turbo")
    response = qwen.invoke("用一句话介绍通义千问")
    print(f"qwen-turbo 回复: {response.content}")
except Exception as e:
    print(f"调用失败: {e}")

# ============================================================
# 3. Embedding 模型
# ============================================================
print("\n3. Embedding 模型")
print("-" * 30)
print("""
langchain-community 提供的 Embedding：

- OpenAIEmbeddings: OpenAI 的 embedding
- HuggingFaceEmbeddings: HuggingFace 模型
- DashScopeEmbeddings: 通义千问的 embedding

Embedding 用途：
- 将文本转为向量
- 用于相似度检索
- RAG 的核心技术
""")

# ============================================================
# 【补充】langchain-community vs 官方包
# ============================================================
print("\n" + "=" * 50)
print("langchain-community vs 官方包")
print("=" * 50)
print("""
| 维度       | langchain-openai  | langchain-community |
|------------|-------------------|-------------------|
| 维护方     | OpenAI 官方       | 社区维护          |
| 更新频率   | 即时              | 延迟数周          |
| 功能完整性 | 支持所有新特性     | 仅基础功能        |
| 生产可用性 | ✅ 强烈推荐       | ⚠️ 谨慎使用      |

建议：
- 生产环境：使用官方包（langchain-openai）
- 开发环境：community 包快速验证
- 官方没有的：使用 community 包
""")
