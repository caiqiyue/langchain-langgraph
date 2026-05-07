# -*- coding: utf-8 -*-
"""
第四节课说明
==================================================

本节课涵盖以下内容：

before_model 中间件：
1. SummarizationMiddleware - 上下文压缩
2. PIIMiddleware - PII信息脱敏
3. ModelCallLimitMiddleware - 模型调用限制

wrap_model_call 中间件：
4. ContextEditingMiddleware - 上下文管理
5. ModelFallbackMiddleware - 模型故障切换
6. LLMToolSelectorMiddleware - 智能工具选择

wrap_tool_call 中间件：
7. ToolRetryMiddleware - 自动重试
8. LLMToolEmulator - 工具模拟

after_model 中间件：
9. HumanInTheLoopMiddleware - 人工审批
10. ToolCallLimitMiddleware - 工具调用限制

学习要点：
- 掌握各类中间件的配置和使用
- 理解不同Hook点的适用场景
- 学会在实际项目中选择合适的中间件
"""