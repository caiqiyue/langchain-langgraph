# -*- coding: utf-8 -*-
"""
第二节课说明
==================================================

本节课涵盖以下内容：

1. 加载模型
   - DeepSeek 模型配置
   - Embeddings 模型配置

2. 文档加载
   - TextLoader 加载文本文件
   - Docx2txtLoader 加载 Word 文档

3. 文档切分
   - RecursiveCharacterTextSplitter
   - chunk_size 和 chunk_overlap 配置

4. 向量存储与检索
   - FAISS 向量数据库
   - BM25 关键词检索
   - EnsembleRetriever 混合检索

5. 基础 RAG 链构建
   - ChatPromptTemplate 提示词模板
   - LCEL 检索链构建
   - StrOutputParser 输出解析

学习要点：
- 掌握 LangChain RAG 完整流程
- 理解向量检索和关键词检索的结合
- 学会使用 LCEL 构建检索链
"""