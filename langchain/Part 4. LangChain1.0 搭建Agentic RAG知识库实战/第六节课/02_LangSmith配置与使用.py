# -*- coding: utf-8 -*-
"""
【案例 2】LangSmith 配置与使用
=================================

本案例展示如何配置和使用 LangSmith 进行 Agent 追踪。

配置步骤：
1. 创建 LangSmith 账户
2. 获取 API Key
3. 设置环境变量
4. 运行 Agent，自动追踪

环境变量：
- LANGCHAIN_TRACING_V2：启用追踪
- LANGSMITH_API_KEY：API 密钥
- LANGSMITH_PROJECT：项目名称

要点：
1. 掌握 LangSmith 配置方法
2. 学会启用自动追踪
3. 理解如何查看追踪结果
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: LangSmith 配置与使用")
print("=" * 60)

# ============================================================
# 2. 环境变量配置
# ============================================================
print("\n【环境变量配置】")
print("-" * 50)

print("""
# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = "your-api-key"
os.environ["LANGSMITH_PROJECT"] = "My_Agentic_RAG"
""")

# ============================================================
# 3. 完整配置示例
# ============================================================
print("\n【完整配置示例】")
print("-" * 50)

print("""
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = "ls_xxxxx"
os.environ["LANGSMITH_PROJECT"] = "Agentic_RAG_Demo"

# 初始化模型和工具
model = ChatDeepSeek(model="deepseek-chat")
web_search = TavilySearch(max_results=2)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="你是一个智能助手。"
)

# 执行（自动被追踪）
result = agent.invoke(
    {"messages": [{"role": "user", "content": "2024年诺贝尔物理学奖是谁？"}]}
)
""")

# ============================================================
# 4. LangSmith Dashboard 功能
# ============================================================
print("\n【LangSmith Dashboard 功能】")
print("-" * 50)

功能表 = """
| 功能 | 说明 |
|------|------|
| Trace List | 查看所有追踪记录 |
| Trace Detail | 查看单个追踪的详细信息 |
| Run Tree | 可视化执行树 |
| Token Usage | Token 消耗统计 |
| Feedback | 质量反馈管理 |
| Filter | 按时间/标签/元数据筛选 |
"""
print(功能表)

# ============================================================
# 5. 查看追踪结果
# ============================================================
print("\n【追踪结果查看】")
print("-" * 50)

print("""
登录 LangSmith Dashboard (https://smith.langchain.com)

1. 选择你的项目
2. 查看 Trace List
3. 点击任意 Trace 查看详情
4. 可看到：
   - 完整的调用链
   - 每个 Run 的输入/输出
   - Token 消耗
   - 执行时间
   - 错误信息（如有）
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)