# -*- coding: utf-8 -*-
"""
【案例 1】SummarizationMiddleware - 上下文压缩中间件
======================================================

本案例展示如何使用 SummarizationMiddleware 自动压缩历史对话，
减少 token 使用，提高响应速度。

核心特性：
1. 自动压缩：当消息 token 超过阈值时触发
2. 智能保留：保留最近的 N 条消息
3. 摘要生成：将旧消息发送给摘要模型生成压缩版本
4. 无缝集成：通过 middleware 参数直接注入

要点：
1. 理解上下文压缩的工作原理
2. 掌握 SummarizationMiddleware 的配置参数
3. 理解压缩前后的 token 节省效果
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 2. 导入 LangChain 核心组件
# ============================================================
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import ensure_config
from pydantic import BaseModel, Field
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 60)
print("案例 1: SummarizationMiddleware 上下文压缩")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def search_patent(query: str) -> str:
    """搜索专利数据库"""
    return f"专利搜索结果: 找到与 '{query}' 相关的 3 项专利..."

@tool
def analyze_technology(tech_desc: str) -> str:
    """分析技术可行性"""
    return f"技术分析: '{tech_desc}' 的实现可行性评估完成..."

tools = [search_patent, analyze_technology]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")
    department: str = Field(..., description="所属部门")
    max_history_tokens: Optional[int] = Field(default=1000, description="历史消息 token 阈值")

# ============================================================
# 5. 配置 SummarizationMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

summarization_middleware = SummarizationMiddleware(
    # 使用哪个模型进行摘要（可以用更小的模型节省成本）
    # model=ChatDeepSeek(model="deepseek-chat", temperature=0.1),
    messages_to_keep=5,  # 保留最近 5 条消息
    summary_prompt="请将以下对话历史进行摘要，保留关键决策点和技术细节：\n\n{messages}\n\n摘要:"
)

print(f"配置: 保留最近 5 条消息 + 摘要")
print(f"触发条件: 消息 token 超过阈值（默认）")
print(f"摘要提示词: 请将以下对话历史进行摘要，保留关键决策点...")

# ============================================================
# 6. 创建 Agent
# ============================================================
print("\n【创建 Agent】")
print("-" * 50)

# 注意：需要实际模型才能运行，这里仅展示配置方式
# agent = create_agent(
#     model=ChatDeepSeek(model="deepseek-chat", temperature=0.2),
#     tools=tools,
#     middleware=[summarization_middleware],
#     context_schema=UserContext,
#     debug=True,
# )

print("Agent 创建配置（需要实际模型才能运行）：")
print("  model: deepseek-chat")
print("  tools: [search_patent, analyze_technology]")
print("  middleware: [SummarizationMiddleware]")
print("  context_schema: UserContext")

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
压缩前（20 条消息，约 1000+ tokens）：
┌─────────────────────────────────────────────────┐
│ 用户: 如何评估某项技术的专利风险？              │
│ AI: 我来帮你分析...                            │
│ 用户: 那具体怎么搜索专利呢？                    │
│ AI: 可以使用专利数据库...                      │
│ ... (更多对话历史)                             │
└─────────────────────────────────────────────────┘

压缩触发条件：
  - 消息数量 > messages_to_keep (5条)
  - Token 数量 > 阈值（默认约 1000）

压缩后（5-6 条消息，约 300-500 tokens）：
┌─────────────────────────────────────────────────┐
│ [摘要] 用户关注技术专利风险评估，涉及搜索和     │
│       分析方法讨论...                          │
│ 用户: 最新关于AI芯片的专利有哪些？             │
│ AI: 让我搜索一下...                           │
│ 用户: 帮我分析这些专利的技术可行性            │
│ AI: 根据搜索结果...                           │
│ 用户: 谢谢                                     │
│ AI: 不客气，还有问题随时问我                  │
└─────────────────────────────────────────────────┘

Token 节省：约 50-70%
""")

# ============================================================
# 8. 关键配置参数
# ============================================================
print("\n" + "=" * 60)
print("关键配置参数")
print("=" * 60)

参数说明 = """
| 参数                  | 默认值   | 说明                          |
|---------------------|---------|------------------------------|
| messages_to_keep    | 5       | 保留最近 N 条消息             |
| max_tokens_before   | 2000    | 超过此 token 数触发压缩       |
| summary_prompt      | 预设模板 | 摘要生成的提示词模板          |
| model               | 主模型   | 用于生成摘要的模型（可选）    |
"""
print(参数说明)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)