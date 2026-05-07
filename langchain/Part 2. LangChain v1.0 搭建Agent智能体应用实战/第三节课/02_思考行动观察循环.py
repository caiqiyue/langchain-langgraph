# -*- coding: utf-8 -*-
"""
【案例 2】思考-行动-观察 循环 - Agent 认知循环详解
=====================================================

本案例深入解析 Agent 的认知循环机制。

ReAct 循环 = Thought (推理) + Action (行动) + Observation (观察)

循环流程：
┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌───────────────┐                                │
│    │ 1. Thought    │  推理：分析当前状态和目标        │
│    │   (思考)      │  "用户要什么？我需要做什么？"   │
│    └───────┬───────┘                                │
│            ↓                                        │
│    ┌───────────────┐                                │
│    │ 2. Action     │  行动：选择并调用工具           │
│    │   (行动)      │  "我决定调用 search_weather"    │
│    └───────┬───────┘                                │
│            ↓                                        │
│    ┌───────────────┐                                │
│    │ 3. Observation │  观察：获取工具返回结果        │
│    │   (观察)      │  "工具返回：北京：晴天，25°C"   │
│    └───────┬───────┘                                │
│            ↓                                        │
│         继续循环？                                   │
│            │                                        │
│    ┌───────┴───────┐                                │
│    │   是 → 返回1  │                                │
│    │   否 → 结束  │                                │
│    └───────────────┘                                │
│                                                     │
└─────────────────────────────────────────────────────┘

要点：
1. 理解 Thought 的作用：为什么需要"思考"
2. 理解 Action 的选择机制
3. 理解 Observation 如何影响下一步决策
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
print("案例 2: 思考-行动-观察 循环")
print("=" * 60)

# ============================================================
# 3. 定义工具集
# ============================================================
@tool
def search_news(topic: str) -> str:
    """搜索新闻"""
    news = {
        "AI": "最新AI新闻：GPT-5即将发布，能力大幅提升",
        "科技": "科技动态：量子计算取得重大突破"
    }
    return news.get(topic, f"关于{topic}的新闻：这是搜索结果...")

@tool
def get_weather(city: str) -> str:
    """查询天气"""
    weather = {
        "北京": "北京：晴天，25°C，适合外出",
        "上海": "上海：多云，28°C，稍有闷热"
    }
    return weather.get(city, f"{city}的天气：数据获取中...")

@tool
def calculate(expr: str) -> str:
    """数学计算"""
    try:
        result = eval(expr)
        return f"计算 {expr} = {result}"
    except:
        return "计算表达式无效"

@tool
def get_time() -> str:
    """获取当前时间"""
    return "当前时间：2024年12月15日 14:30:00"

# ============================================================
# 4. 创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

agent = create_agent(
    model=model,
    tools=[search_news, get_weather, calculate, get_time],
    system_prompt="""你是一个智能助手，通过思考-行动-观察的循环来完成任务。

对于每个用户问题，你会：
1. Thought (思考)：分析问题，决定是否需要工具
2. Action (行动)：选择并调用合适的工具
3. Observation (观察)：获取工具结果，决定下一步

请仔细观察 Agent 的思考和决策过程。"""
)

# ============================================================
# 5. 演示：简单问题（一轮循环）
# ============================================================
print("\n" + "=" * 60)
print("案例 1：简单问题（只需一轮循环）")
print("=" * 60)

问题1 = "现在几点了？"
print(f"\n用户问题: {问题1}")

result1 = agent.invoke({
    "messages": [{"role": "user", "content": 问题1}]
})

print("\n执行过程:")
for i, msg in enumerate(result1["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "human":
        print(f"\n[输入] 用户: {msg.content}")

    elif msg_type == "ai":
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"[决策] Thought: 需要获取时间，调用 get_time()")
                print(f"[行动] Action: {tc['name']}({tc['args']})")
        else:
            print(f"[回答] {msg.content}")

    elif msg_type == "tool":
        print(f"[观察] Observation: {msg.content}")

# ============================================================
# 6. 演示：需要多轮循环的复杂问题
# ============================================================
print("\n" + "=" * 60)
print("案例 2：复杂问题（需要多轮循环）")
print("=" * 60)

问题2 = "北京的天气怎么样？如果比上海暖和，就告诉我暖和多少度"
print(f"\n用户问题: {问题2}")

result2 = agent.invoke({
    "messages": [{"role": "user", "content": 问题2}]
})

print("\n执行过程:")
循环次数 = 0
for i, msg in enumerate(result2["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "human":
        print(f"\n[输入] 用户: {msg.content}")

    elif msg_type == "ai":
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            循环次数 += 1
            for tc in msg.tool_calls:
                print(f"\n[循环 {循环次数}]")
                print(f"  [Thought] 思考: {循环次数 == 1 and '需要先查询北京和上海的天气' or '需要计算温度差'}")
                print(f"  [Action] 行动: {tc['name']}({tc['args']})")
        else:
            print(f"\n[最终回答]")
            print(f"  {msg.content}")

    elif msg_type == "tool":
        print(f"  [Observation] 观察: {msg.content}")

# ============================================================
# 7. ReAct 循环的终止条件
# ============================================================
print("\n" + "=" * 60)
print("ReAct 循环终止条件")
print("=" * 60)
print("""
循环会在以下情况终止：

1. 【正常完成】
   - Agent 收集到足够信息
   - 可以给用户提供完整答案
   - 例如：查询天气 → 得到结果 → 回答用户

2. 【达到最大迭代】
   - 防止无限循环（recursion_limit）
   - 默认限制：通常 15-50 次
   - 超过限制会抛出异常

3. 【达到时间限制】
   - 某些场景下有时间约束
   - 超过时间自动终止

4. 【工具调用失败】
   - 工具执行出错
   - Agent 可能尝试其他工具或直接回答
""")

# ============================================================
# 8. 实际观察 ReAct 过程
# ============================================================
print("\n" + "=" * 60)
print("实战：观察完整的 ReAct 思考过程")
print("=" * 60)

# 使用 stream_mode 观察每一步
问题3 = "AI和科技的最新消息分别是什么？"
print(f"\n用户问题: {问题3}")

print("\n逐步执行：")
step = 0
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": 问题3}]},
    stream_mode="values"
):
    step += 1
    last_msg = chunk["messages"][-1]
    msg_type = getattr(last_msg, "type", "unknown")

    if msg_type == "ai":
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                print(f"\n步骤 {step} [思考+行动]")
                print(f"  → 调用工具: {tc['name']}")
                print(f"  → 参数: {tc['args']}")
        elif last_msg.content:
            print(f"\n步骤 {step} [最终回答]")
            print(f"  {last_msg.content[:150]}...")

    elif msg_type == "tool":
        print(f"  [观察] {last_msg.content[:60]}...")

print("\n" + "=" * 60)
print("✅ ReAct 循环总结")
print("=" * 60)
print("""
ReAct 循环的核心价值：
1. 可追溯：每一步的思考和行动都有记录
2. 可干预：可以在任意步骤介入
3. 可优化：可以通过改进工具描述提升效果
4. 可调试：方便发现和修复问题

关键提示：
- Thought 不是代码逻辑，而是 LLM 的"思考文本"
- Action 的选择取决于工具描述的质量
- Observation 是下一次决策的重要依据
""")