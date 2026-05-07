# -*- coding: utf-8 -*-
"""
【案例 3】流式输出与 stream_mode
=================================

本案例介绍 Agent 的流式输出模式，帮助你观察执行过程。

stream_mode 参数：
- "values"    : 返回每步后的完整状态（适合调试）
- "updates"   : 仅返回状态变更部分（适合前端增量更新）
- "messages"  : 返回 LLM 生成的 token 流（适合打字机效果）

要点：
1. 理解不同 stream_mode 的区别
2. 掌握如何观察 Agent 执行过程
3. 学会选择合适的输出模式
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
print("案例 3: 流式输出与 stream_mode")
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
    system_prompt="你是一个简洁的助手。"
)

# ============================================================
# 4. stream_mode="values" - 观察完整状态
# ============================================================
print("\n" + "=" * 60)
print("stream_mode='values' - 完整状态流（适合调试）")
print("=" * 60)

问题 = "北京天气怎么样？顺便计算一下 25 加 10"

print(f"\n问题: {问题}")
print("\n逐步执行：")

step = 0
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": 问题}]},
    stream_mode="values"
):
    step += 1
    messages = chunk["messages"]
    last_msg = messages[-1]
    msg_type = getattr(last_msg, "type", "unknown")

    print(f"\n--- 步骤 {step} ---")
    print(f"消息类型: {msg_type}")

    if msg_type == "ai":
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                print(f"决策: 调用 {tc['name']}")
        else:
            print(f"最终回答: {last_msg.content[:80]}...")
    elif msg_type == "tool":
        print(f"工具结果: {last_msg.content}")

# ============================================================
# 5. stream_mode 对比总结
# ============================================================
print("\n" + "=" * 60)
print("✅ stream_mode 模式对比总结")
print("=" * 60)
print("""
┌────────────┬─────────────────────────────────────┬──────────────────┐
│  模式       │  输出内容                            │  适用场景         │
├────────────┼─────────────────────────────────────┼──────────────────┤
│ values     │ 每步后的完整状态                     │ 调试、学习        │
│ updates    │ 仅状态变更部分                       │ 前端增量更新      │
│ messages   │ LLM token 流                        │ 打字机效果        │
└────────────┴─────────────────────────────────────┴──────────────────┘

开发建议：
- 学习原理：使用 values 模式
- 生产环境：根据需求选择
- 调试问题：使用 values 观察完整流程
""")