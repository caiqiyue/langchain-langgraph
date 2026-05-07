# -*- coding: utf-8 -*-
"""
【案例 5】基础 RAG 链构建
===========================

本案例展示如何使用 LCEL（LangChain Expression Language）
构建完整的 RAG 检索和生成链。

RAG 链组成：
1. 检索链：从向量数据库检索相关文档
2. 生成链：将检索结果和问题发送给 LLM 生成回答

LCEL 语法：
- |：管道操作，将前一个输出传给下一个
- {}：字典，用于组合多个输入

要点：
1. 掌握 LCEL 基础语法
2. 学会构建检索链和生成链
3. 理解 LCEL 的惰性求值机制
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 5: 基础 RAG 链构建")
print("=" * 60)

# ============================================================
# 2. 导入 LCEL 组件
# ============================================================
print("\n【LCEL 组件】")
print("-" * 50)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

print("已导入组件:")
print("  - ChatPromptTemplate：聊天提示词模板")
print("  - RunnablePassthrough：传递输入")
print("  - StrOutputParser：输出字符串解析器")

# ============================================================
# 3. 创建提示模板
# ============================================================
print("\n【提示模板】")
print("-" * 50)

# 定义提示模板
template = """你是一个专业的问答助手。请根据以下提供的上下文信息来回答用户的问题。
如果上下文中没有相关信息，请诚实地告诉用户你不知道，不要编造答案。

上下文信息：
{context}

问题: {question}

回答:"""

prompt = ChatPromptTemplate.from_template(template)

print(f"提示模板:\n{prompt}")

# ============================================================
# 4. 格式化文档辅助函数
# ============================================================
print("\n【文档格式化函数】")
print("-" * 50)

print("""
def format_docs(docs):
    '''将多个文档合并为一个字符串'''
    return "\\n\\n".join(doc.page_content for doc in docs)

# 作用：将检索返回的文档列表合并成字符串
# 例如：
#   docs = [doc1, doc2, doc3]
#   format_docs(docs) => "doc1内容\\n\\ndoc2内容\\n\\ndoc3内容"
""")

# ============================================================
# 5. 构建检索链
# ============================================================
print("\n【构建检索链】")
print("-" * 50)

print("""
# 方式1：简单检索链
retrieval_chain = ensemble_retriever | format_docs

# 执行检索
results = retrieval_chain.invoke("用户问题")
print(results)

# 方式2：带参数的检索
retrieval_chain = ensemble_retriever | format_docs
""")

# ============================================================
# 6. 构建生成链
# ============================================================
print("\n【构建生成链】")
print("-" * 50)

print("""
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
print(answer)
""")

# ============================================================
# 7. LCEL 管道图示
# ============================================================
print("\n【LCEL 管道图示】")
print("-" * 50)

print("""
【完整 RAG 链执行流程】

用户问题: "LangChain是什么？"
                    │
                    ▼
┌───────────────────────────────────────────────┐
│  {"context": ..., "question": "LangChain是什么？"} │
└───────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────┐
│              ChatPromptTemplate               │
│   系统提示 + context + question                │
└───────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────┐
│              LLM (ChatDeepSeek)              │
│   理解问题 + 分析上下文 + 生成回答             │
└───────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────┐
│              StrOutputParser                  │
│   将 AIMessage 转为字符串                     │
└───────────────────────────────────────────────┘
                    │
                    ▼
最终回答: "LangChain 是一个用于构建..."
""")

# ============================================================
# 8. LCEL 语法说明
# ============================================================
print("\n【LCEL 语法说明】")
print("-" * 50)

print("""
| 语法 | 说明 | 示例 |
|------|------|------|
| A \| B | 将 A 的输出传给 B | retriever \| format_docs |
| {k: v} | 创建字典 | {"context": ..., "question": ...} |
| RunnablePassthrough() | 透传输入 | RunnablePassthrough() |

【Runnable 组件】
  - 一切皆 Runnable
  - 可以链式调用
  - 支持 stream/batch/invoke 多种调用方式
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)