# -*- coding: utf-8 -*-
"""
【案例 7】ToolRetryMiddleware - 工具自动重试中间件
==================================================

本案例展示如何使用 ToolRetryMiddleware 自动重试失败的工具调用，
提高系统的稳定性和可靠性。

核心特性：
1. 自动重试：工具调用失败时自动重试
2. 指数退避：避免过度请求
3. 灵活配置：可配置重试次数和条件
4. 异常过滤：只重试特定类型的异常

要点：
1. 理解指数退避策略
2. 掌握 retry_on 和 on_failure 配置
3. 理解适用场景（网络不稳定、外部 API 限流等）
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
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import ensure_config
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 7: ToolRetryMiddleware 工具自动重试")
print("=" * 60)

# ============================================================
# 3. 定义工具（模拟可能失败的工具）
# ============================================================
@tool
def unreliable_api_call(query: str) -> str:
    """
    模拟不稳定的 API 调用
    前2次调用会失败，第3次成功
    """
    import random
    import time

    # 模拟计数器（实际应用中可能用全局状态）
    if not hasattr(unreliable_api_call, 'call_count'):
        unreliable_api_call.call_count = 0

    unreliable_api_call.call_count += 1
    attempt = unreliable_api_call.call_count

    print(f"  [API 调用] 第 {attempt} 次尝试...")

    # 前2次调用失败
    if attempt <= 2:
        raise ConnectionError(f"API 连接失败（尝试 {attempt}/3）")

    # 第3次成功
    return f"API 查询成功: '{query}' 的结果数据"

@tool
def stable_tool(data: str) -> str:
    """稳定的工具，总是成功"""
    return f"处理完成: {data}"

# 工具列表
tools = [unreliable_api_call, stable_tool]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 ToolRetryMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

retry_middleware = ToolRetryMiddleware(
    max_retries=3,  # 最多重试 3 次
    tools=["unreliable_api_call"],  # 只对不稳定工具启用重试
    retry_on=(ConnectionError, TimeoutError),  # 只重试这些异常
    on_failure="return_message",  # 失败时返回友好消息
    backoff_factor=1.5,  # 退避因子
    initial_delay=0.5,  # 初始延迟 0.5 秒
    max_delay=5.0,  # 最大延迟 5 秒
    jitter=True,  # 添加随机抖动
)

print("配置参数：")
print(f"  max_retries: 3（最多重试 3 次）")
print(f"  tools: ['unreliable_api_call']（只重试此工具）")
print(f"  retry_on: (ConnectionError, TimeoutError)")
print(f"  on_failure: 'return_message'（返回友好消息）")
print(f"  backoff_factor: 1.5（指数退避因子）")
print(f"  initial_delay: 0.5s（初始延迟）")
print(f"  max_delay: 5.0s（最大延迟）")
print(f"  jitter: True（添加随机抖动）")

# ============================================================
# 6. 指数退避图示
# ============================================================
print("\n【指数退避策略】")
print("-" * 50)

print("""
退避时间计算（backoff_factor=1.5, initial_delay=0.5s）：
┌──────────┬────────────────┬─────────────────┐
│ 重试次数  │ 计算公式        │ 实际延迟         │
├──────────┼────────────────┼─────────────────┤
│ 第1次重试 │ 0.5 × 1.5^0    │ ~0.5s (±抖动)   │
│ 第2次重试 │ 0.5 × 1.5^1    │ ~0.75s (±抖动)  │
│ 第3次重试 │ 0.5 × 1.5^2    │ ~1.125s (±抖动) │
└──────────┴────────────────┴─────────────────┘

总等待时间（不含抖动）：约 2.375 秒

抖动的作用：
  - 避免多个客户端同时重试造成"雷鸣群效应"
  - 随机范围：delay × (0.5 ~ 1.5)
""")

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【执行流程】

用户请求: 调用 unreliable_api_call
    │
    ▼
┌─────────────────────────────────┐
│  第 1 次尝试                    │
│  调用 unstable_api_call        │
│  → ConnectionError             │
└─────────────────────────────────┘
    │
    ▼ (等待 ~0.5s)
┌─────────────────────────────────┐
│  第 2 次尝试                    │
│  调用 unstable_api_call        │
│  → ConnectionError             │
└─────────────────────────────────┘
    │
    ▼ (等待 ~0.75s)
┌─────────────────────────────────┐
│  第 3 次尝试                    │
│  调用 unstable_api_call        │
│  → 成功！返回结果               │
└─────────────────────────────────┘
    │
    ▼
返回成功结果给用户
""")

# ============================================================
# 8. 适用场景
# ============================================================
print("\n【适用场景】")
print("-" * 50)

场景说明 = """
| 场景                  | 配置建议                      |
|---------------------|------------------------------|
| 网络请求不稳定        | max_retries=3, initial_delay=1s |
| 外部 API 限流        | max_retries=5, backoff_factor=2.0 |
| 数据库连接超时        | max_retries=2, retry_on=TimeoutError|
| 临时性服务故障        | max_retries=3, on_failure='return_message'|
"""
print(场景说明)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)