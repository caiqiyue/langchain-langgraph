# -*- coding: utf-8 -*-
"""
【案例 3】ModelCallLimitMiddleware - 模型调用限制中间件
==========================================================

本案例展示如何使用 ModelCallLimitMiddleware 限制 Agent 的模型调用次数，
防止死循环或意外的高消耗。

核心特性：
1. 安全防护：防止 Agent 陷入无限循环
2. 简单配置：通过 max_calls 参数设置最大次数
3. 自动熔断：达到限制后自动停止
4. 灵活策略：error/continue 两种退出行为

要点：
1. 理解防止死循环的重要性
2. 掌握 ModelCallLimitMiddleware 配置
3. 理解两种退出行为的区别
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
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import ensure_config
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 3: ModelCallLimitMiddleware 模型调用限制")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def complex_calculation(x: int) -> int:
    """执行复杂计算"""
    return x * 2

@tool
def get_weather(city: str) -> str:
    """获取天气信息"""
    return f"{city}的天气：晴天，温度25°C"

tools = [complex_calculation, get_weather]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 ModelCallLimitMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

# 方式1: error 模式 - 超限时抛出异常
limit_middleware_error = ModelCallLimitMiddleware(
    run_limit=3,
    exit_behavior='error'
)
print("【error 模式】")
print(f"  run_limit: 3")
print(f"  exit_behavior: error")
print(f"  效果: 达到限制后抛出 ModelCallLimitExceeded 异常")

# 方式2: continue 模式 - 超限后续执行
limit_middleware_continue = ModelCallLimitMiddleware(
    run_limit=3,
    exit_behavior='continue'
)
print("\n【continue 模式】")
print(f"  run_limit: 3")
print(f"  exit_behavior: continue")
print(f"  效果: 达到限制后阻止工具调用，但继续执行")

# ============================================================
# 6. 退出行为对比
# ============================================================
print("\n【退出行为对比】")
print("-" * 50)

行为对比 = """
| 行为        | 触发后动作                     | 适用场景              |
|------------|-------------------------------|---------------------|
| error      | 抛出异常，中断执行              | 生产环境，严格控制    |
| continue   | 阻止调用，但继续执行流程        | 开发调试，允许降级    |
"""
print(行为对比)

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【场景】设计一个需要多次工具调用的复杂任务

用户输入：
┌─────────────────────────────────────────────────┐
│ 请按照以下步骤计算：                            │
│ 1. 计算 5 的两倍                               │
│ 2. 用第一步的结果再计算两倍                    │
│ 3. 用第二步的结果再计算两倍                    │
│ 4. 用第三步的结果再计算两倍                    │
│ 5. 最后告诉我北京的天气                         │
└─────────────────────────────────────────────────┘

【正常执行流程】（无限制）
  用户输入 → 模型思考 → 调用计算工具(1)
                      → 模型思考 → 调用计算工具(2)
                      → 模型思考 → 调用计算工具(3)
                      → 模型思考 → 调用计算工具(4)
                      → 模型思考 → 调用天气工具(5)
                      → 返回结果

【触发限制流程】（run_limit=3）
  用户输入 → 模型思考 → 调用计算工具(1) ✓
                      → 模型思考 → 调用计算工具(2) ✓
                      → 模型思考 → 调用计算工具(3) ✓
                      → ⚠️ ModelCallLimitMiddleware 触发！
                      → 抛出异常或阻止后续调用
                      → 返回错误信息或降级结果
""")

# ============================================================
# 8. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware

# 配置中间件
limit_middleware = ModelCallLimitMiddleware(
    run_limit=3,
    exit_behavior='error'
)

# 创建 Agent
agent = create_agent(
    model=ChatDeepSeek(model="deepseek-chat", temperature=0.1),
    tools=tools,
    middleware=[limit_middleware],
    context_schema=UserContext,
    debug=False,
)

# 执行（可能触发限制）
try:
    result = agent.invoke({
        "messages": [HumanMessage(content=complex_query)]
    })
except Exception as e:
    if "limit" in str(e).lower():
        print("模型调用次数超限！")
""")

# ============================================================
# 9. 典型应用场景
# ============================================================
print("\n" + "=" * 60)
print("典型应用场景")
print("=" * 60)

场景说明 = """
| 场景                    | 配置建议              | 原因                |
|------------------------|---------------------|-------------------|
| 简单问答                | run_limit=1-2       | 单次调用足够       |
| 工具使用                | run_limit=3-5       | 多数工具调用1-3次  |
| 复杂推理                | run_limit=5-10      | 涉及多步推理       |
| 开发调试                | run_limit=10-20     | 允许更多尝试       |
| 生产环境                | run_limit=5 + continue | 防止死循环但允许降级 |
"""
print(场景说明)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)