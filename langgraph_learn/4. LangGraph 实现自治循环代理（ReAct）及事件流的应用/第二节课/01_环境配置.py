"""
环境配置与 LangSmith 追踪设置
==============================

本文件演示如何配置 LangSmith 以追踪和可视化 ReAct Agent 的执行过程。
"""

import os

# -----------------------------------------------------------------------------
# 1. LangSmith 配置
# -----------------------------------------------------------------------------
# LangSmith 是 LangChain 的追踪和监控平台
# 注册地址：https://www.langchain.com/langsmith

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key"  # 替换为你的 LangSmith API_KEY
os.environ["LANGCHAIN_PROJECT"] = "langGraph_ReAct"         # 项目名称

# 验证环境变量是否设置成功
print(os.getenv("LANGCHAIN_TRACING_V2"))
print(os.getenv("LANGCHAIN_API_KEY"))
print(os.getenv("LANGCHAIN_PROJECT"))