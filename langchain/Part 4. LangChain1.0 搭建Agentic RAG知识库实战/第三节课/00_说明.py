# -*- coding: utf-8 -*-
"""
第三节课说明
==================================================

本节课涵盖以下内容：

1. Tool与Middleware的区别
   - Tool：封装业务功能，LLM显式调用
   - Middleware：封装流程控制，自动触发

2. 将RAG封装为Tool
   - 定义工具函数
   - StructuredTool.from_function
   - 工具描述编写

3. 知识库检索工具
   - query_retrieval_knowledge：LangChain知识库
   - sensitive_knowledge_tool：敏感知识库
   - TavilySearch：网络搜索

学习要点：
- 理解Tool与Middleware的设计哲学
- 掌握将RAG封装为Tool的方法
- 学会编写有效的工具描述
"""