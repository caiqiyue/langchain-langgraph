# -*- coding: utf-8 -*-
"""
【案例 1】中间件四大分类 - 监控、修改、控制、强制
==================================================

中间件是拦截、修改、控制和增强 Agent 执行流程的机制。
按照功能特性，划分为四大类别：

1. Monitor（监控类）= 观察者 - 记录日志、性能分析、成本核算
2. Modify（修改类）= 优化师 - 上下文压缩、动态注入System Prompt
3. Control（控制类）= 指挥官 - 流程阻断、人工介入、重试机制
4. Enforce（强制类）= 守护者 - 安全过滤、限流、PII脱敏

要点：
1. 理解四大分类的设计哲学
2. 掌握每类中间件的典型应用场景
3. 理解分类对系统可观测性和安全性的意义
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
from langchain.agents.middleware import (
    SummarizationMiddleware,
    PIIMiddleware,
    ModelCallLimitMiddleware,
    ContextEditingMiddleware,
    HumanInTheLoopMiddleware,
    ToolRetryMiddleware
)
from langchain.agents.middleware.context_editing import ClearToolUsesEdit
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Optional

print("=" * 60)
print("案例 1: 中间件四大分类")
print("=" * 60)

# ============================================================
# 3. 定义示例工具
# ============================================================
@tool
def search_database(query: str) -> str:
    """搜索数据库并返回结果"""
    return f"数据库搜索结果：找到与 '{query}' 相关的 3 条记录..."

@tool
def send_notification(user: str, message: str) -> str:
    """发送通知给用户"""
    return f"通知已发送给 {user}: {message}"

@tool
def process_payment(amount: float, card_last4: str) -> str:
    """处理支付（模拟）"""
    return f"支付成功！金额: ${amount}, 卡号尾号: {card_last4}"

# 工具列表
tools = [search_database, send_notification, process_payment]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")
    department: str = Field(..., description="所属部门")
    security_level: str = Field(default="normal", description="安全级别")

# ============================================================
# 5. 四大分类示例
# ============================================================

# ----- 5.1 Monitor（监控类）-----
print("\n" + "-" * 50)
print("【监控类中间件 Monitor】- 系统的观察者")
print("-" * 50)
print("""
核心功能：观察执行状态、日志记录
解决的问题：调试困难、缺乏可观测性
典型应用：
  - LangSmith tracing（官方监控平台）
  - 性能监控中间件
  - 成本追踪中间件

特点：只读不修改，对性能影响 < 1ms
""")

# ----- 5.2 Modify（修改类）-----
print("\n" + "-" * 50)
print("【修改类中间件 Modify】- 系统的优化师")
print("-" * 50)
print("""
核心功能：修改输入/输出、上下文管理
解决的问题：上下文窗口溢出、Prompt优化
典型应用：
  - SummarizationMiddleware（自动压缩历史对话）
  - ContextEditingMiddleware（清理旧工具结果）
  - 动态注入 System Prompt

特点：修改数据流，对性能影响 1-50ms
""")

# ----- 5.3 Control（控制类）-----
print("\n" + "-" * 50)
print("【控制类中间件 Control】- 系统的指挥官")
print("-" * 50)
print("""
核心功能：流程阻断、人工介入
解决的问题：AI幻觉、高风险操作失控
典型应用：
  - HumanInTheLoopMiddleware（敏感操作需人工审批）
  - ToolRetryMiddleware（自动重试机制）
  - 条件分支中间件

特点：可中断执行流程，对性能影响 5-20ms
""")

# ----- 5.4 Enforce（强制类）-----
print("\n" + "-" * 50)
print("【强制类中间件 Enforce】- 系统的守护者")
print("-" * 50)
print("""
核心功能：安全过滤、限流、合规检查
解决的问题：数据泄露、API滥用
典型应用：
  - PIIMiddleware（敏感信息脱敏）
  - ModelCallLimitMiddleware（防止死循环）
  - RateLimitMiddleware（API限流）

特点：强制执行规则，对性能影响 1-5ms
""")

# ============================================================
# 6. 四大分类对比表
# ============================================================
print("\n" + "=" * 60)
print("四大分类对比总结")
print("=" * 60)

对比表 = """
| 分类       | 核心功能           | 解决问题               | 性能影响  |
|-----------|-------------------|----------------------|----------|
| Monitor   | 观察执行状态       | 调试困难、缺乏可观测性   | < 1ms   |
| Modify   | 修改输入/输出      | 上下文溢出、Prompt优化   | 1-50ms  |
| Control   | 流程阻断、人工介入  | AI幻觉、高风险操作失控   | 5-20ms  |
| Enforce   | 安全过滤、限流      | 数据泄露、API滥用       | 1-5ms   |
"""
print(对比表)

# ============================================================
# 7. 实际应用示例
# ============================================================
print("\n" + "=" * 60)
print("实际应用示例")
print("=" * 60)

# 示例1: PIIMiddleware（强制类 - 安全过滤）
print("\n【示例1】PIIMiddleware - 信用卡号脱敏")
print("-" * 50)

piimiddleware_example = PIIMiddleware(
    "credit_card",
    detector=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    strategy="mask",  # 掩码策略
    apply_to_input=True,
    apply_to_output=False,
)

test_input = "我的银行卡号是 4532-1234-5678-9010"
print(f"脱敏前: {test_input}")
print("脱敏后: 银行卡号是 ****-****-****-9010 (模拟)")

# 示例2: ModelCallLimitMiddleware（强制类 - 限流）
print("\n【示例2】ModelCallLimitMiddleware - 防止死循环")
print("-" * 50)

limit_middleware = ModelCallLimitMiddleware(
    run_limit=3,
    exit_behavior='error'
)
print(f"配置: 每次运行最多调用模型 3 次")
print("触发: 达到限制后抛出 ModelCallLimitExceeded 异常")

# 示例3: SummarizationMiddleware（修改类 - 上下文压缩）
print("\n【示例3】SummarizationMiddleware - 自动压缩历史对话")
print("-" * 50)

summarization_middleware = SummarizationMiddleware(
    messages_to_keep=5,
    summary_prompt="请将以下对话历史进行摘要：\n\n{messages}\n\n摘要:"
)
print(f"配置: 保留最近 5 条消息 + 摘要")
print("效果: 20条消息压缩为 5-6 条，节省 50-70% tokens")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)