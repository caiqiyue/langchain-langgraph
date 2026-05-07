# -*- coding: utf-8 -*-
"""
【案例 2】RecursionLimit 循环控制
===================================

本案例展示如何限制 Agent 的最大循环次数，防止无限循环。

问题场景：
- Agent 可能陷入无限循环
- 某些复杂问题可能需要很多步骤
- 需要控制资源消耗

解决方案：
- 设置 recursion_limit 限制最大迭代次数
- 达到限制时抛出异常

要点：
1. 理解 recursion_limit 的作用
2. 掌握如何设置限制
3. 理解限制对复杂任务的影响
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# 2. 导入核心组件
# ============================================================
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent

print("=" * 60)
print("案例 2: RecursionLimit 循环控制")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def get_weather(city: str) -> str:
    """查询天气"""
    return f"{city}：晴天，25°C"

@tool
def calculate(expr: str) -> str:
    """计算表达式"""
    return f"结果：{eval(expr)}"

model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

agent = create_agent(
    model=model,
    tools=[get_weather, calculate],
    system_prompt="你是一个有帮助的助手。"
)

# ============================================================
# 4. 正常情况：无限制
# ============================================================
print("\n" + "=" * 60)
print("案例 1：正常执行（无限制）")
print("=" * 60)

config_no_limit = {"configurable": {"thread_id": "no_limit"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "北京天气怎么样？"}]
}, config=config_no_limit)

print(f"问题：北京天气怎么样？")
print(f"回答：{result['messages'][-1].content}")
print(f"循环次数：{len([m for m in result['messages'] if hasattr(m, 'type') and m.type == 'ai'])}")

# ============================================================
# 5. 限制循环次数
# ============================================================
print("\n" + "=" * 60)
print("案例 2：限制最大循环次数")
print("=" * 60)

# 设置 recursion_limit = 3（最多3次迭代）
config_limited = {
    "configurable": {
        "thread_id": "limited_001",
        "recursion_limit": 3  # 最多3次循环
    }
}

try:
    result = agent.invoke({
        "messages": [{"role": "user", "content": "北京天气怎么样？用华氏度怎么说？"}]
    }, config=config_limited)
    print(f"回答：{result['messages'][-1].content}")
except Exception as e:
    print(f"⚠️ 达到限制：{type(e).__name__}")
    print(f"   原因：超过最大循环次数（recursion_limit=3）")

# ============================================================
# 6. 总结
# ============================================================
print("\n" + "=" * 60)
print("✅ RecursionLimit 配置总结")
print("=" * 60)
print("""
配置方式：
    config = {"configurable": {"recursion_limit": N}}

建议值：
- 简单任务：3-5 次
- 复杂任务：10-15 次
- 生产环境：15-30 次

注意事项：
1. 限制太低：复杂任务可能无法完成
2. 限制太高：可能陷入无限循环
3. 可以配合中间件做更精细的控制
""")