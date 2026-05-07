# -*- coding: utf-8 -*-
"""
第一阶段：Native RAG核心流程探索 - 代码案例索引
================================================

本文件夹包含 Native RAG 基础概念的代码案例

文件列表：
00_说明.py          - 本索引文件
01_RAG基础概念.py    - RAG 定义与流程
02_RAG两阶段过程.py  - 知识库构建与问答

RAG 核心概念：
- Retrieval：检索
- Augmented：增强
- Generation：生成

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 4. LangChain1.0 搭建Agentic RAG知识库实战/第一节课/01_RAG基础概念.py"
"""

print("=" * 60)
print("第一阶段：Native RAG核心流程探索")
print("=" * 60)
print("""
RAG 核心概念：

R - Retrieval（检索）：从知识库中检索相关信息
A - Augmented（增强）：将检索结果加入提示词
G - Generation（生成）：LLM 基于增强后的提示词生成答案

两阶段过程：
阶段一（准备）：数据接入 → 文档解析 → 文档切分 → 向量化 → 存储
阶段二（问答）：用户提问 → 问题向量化 → 相似度检索 → 构建增强提示 → 生成答案

代码案例：
01_RAG基础概念.py    - RAG 定义与流程
02_RAG两阶段过程.py  - 知识库构建与问答
""")