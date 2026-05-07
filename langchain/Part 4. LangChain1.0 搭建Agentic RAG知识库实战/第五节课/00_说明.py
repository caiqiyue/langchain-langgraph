# -*- coding: utf-8 -*-
"""
第五节课说明
==================================================

本节课涵盖以下内容：

1. 构建 Agentic RAG 系统
   - 中间件组合设计
   - 工具注册
   - 执行流程

2. 中间件详解
   - SummarizationMiddleware：上下文压缩
   - ToolRetryMiddleware：自动重试
   - ToolLoggingMiddleware：日志记录
   - ToolCallLimitMiddleware：调用限制
   - HumanInTheLoopMiddleware：人工审批
   - dynamic_prompt：动态提示词

3. 中间件执行顺序
   - before_model：上下文压缩
   - wrap_model_call：动态提示词
   - after_model：日志、限制、审批

学习要点：
- 掌握多中间件组合设计
- 理解中间件执行顺序
- 学会构建企业级 Agentic RAG
"""