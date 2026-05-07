# -*- coding: utf-8 -*-
"""
【案例 2】ReAct 执行循环 - 理解 Agent 的"思考-行动-观察"机制
================================================================

本案例深入解析 ReAct（Reasoning + Acting）范式，这是 Agent 自主决策的核心。

ReAct 循环的四个步骤：
1. Thought (推理)   - 大模型思考：我现在应该做什么？
2. Action (行动)    - 选择并调用合适的工具
3. Observation (观察) - 获取工具返回的结果
4. 循环决策        - 根据观察结果，决定下一步行动或结束

要点：
1. 理解 ReAct 循环的四个阶段
2. 观察 Agent 如何自主决定调用哪个工具
3. 理解循环终止条件
"""

# ============================================================
# 1. 环境配置
# ============================================================
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# 2. 导入核心组件
# ============================================================
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

print("=" * 60)
print("案例 2: ReAct 执行循环 - 思考-行动-观察机制")
print("=" * 60)

# ============================================================
# 3. 定义多个工具（模拟不同的执行能力）
# ============================================================
@tool
def search_news(keyword: str) -> str:
    """
    搜索新闻信息（模拟）。

    参数:
        keyword (str): 搜索关键词

    返回:
        str: 搜索结果
    """
    news_db = {
        "AI": "2024年AI领域最新进展：GPT-5即将发布，多模态能力大幅提升",
        "Python": "Python 3.13 正式发布，带来性能大幅提升",
        "LangChain": "LangChain 1.0 正式发布，Agent 开发更简单"
    }
    return news_db.get(keyword, f"暂无关于'{keyword}'的最新新闻")

@tool
def calculate(expression: str) -> str:
    """
    执行数学计算（模拟）。

    参数:
        expression (str): 数学表达式，如 "25 + 10"

    返回:
        str: 计算结果
    """
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

@tool
def get_time(city: str) -> str:
    """
    获取城市当前时间（模拟）。

    参数:
        city (str): 城市名称

    返回:
        str: 当前时间
    """
    time_zones = {
        "北京": "当前北京时间：2024-12-15 14:30",
        "纽约": "当前纽约时间：2024-12-15 01:30（凌晨）",
        "东京": "当前东京时间：2024-12-15 15:30"
    }
    return time_zones.get(city, f"暂不支持查询{city}的时间")

# ============================================================
# 4. 初始化模型并创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=[search_news, calculate, get_time],
    system_prompt="""你是一个智能助手，可以通过以下工具为用户提供服务：
1. search_news - 搜索新闻（参数：keyword）
2. calculate - 数学计算（参数：expression）
3. get_time - 查询时间（参数：city）

请根据用户问题自主选择合适的工具。"""
)

# ============================================================
# 5. 观察 ReAct 循环过程
# ============================================================
print("\n" + "=" * 60)
print("案例：用户问 'AI的最新消息是什么？顺便帮我算一下 100-30 等于多少'")
print("=" * 60)

# 第一次交互：多工具调用
result1 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "AI的最新消息是什么？顺便帮我算一下 100-30 等于多少"
    }]
})

print("\n执行过程详情：")
for i, msg in enumerate(result1["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "human":
        print(f"\n[步骤 {i}] 👤 用户: {msg.content}")

    elif msg_type == "ai":
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[步骤 {i}] 🧠 AI 思考:")
            print(f"         问题分析：需要搜索AI新闻 AND 计算数学")
            for tc in msg.tool_calls:
                print(f"         决定调用工具: {tc['name']}")
                print(f"         输入参数: {tc['args']}")
        else:
            print(f"[步骤 {i}] 🤖 AI 最终回答: {msg.content[:150]}...")

    elif msg_type == "tool":
        print(f"[步骤 {i}] 🔧 工具返回: {msg.content}")

# ============================================================
# 6. 第二个例子：复杂多步骤任务
# ============================================================
print("\n" + "=" * 60)
print("案例2：需要多轮循环的复杂任务")
print("=" * 60)

result2 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "请先查一下Python的新闻，然后告诉我Python和AI有什么关系？"
    }]
})

print("\n执行过程：")
for i, msg in enumerate(result2["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "human":
        print(f"\n[步骤 {i}] 👤 用户: {msg.content}")

    elif msg_type == "ai":
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[步骤 {i}] 🧠 AI 思考: 需要先搜索Python新闻")
            for tc in msg.tool_calls:
                print(f"         调用: {tc['name']}({tc['args']})")
        else:
            print(f"[步骤 {i}] 🤖 AI: {msg.content[:200]}...")

    elif msg_type == "tool":
        print(f"[步骤 {i}] 🔧 工具结果: {msg.content}")

# ============================================================
# 7. ReAct 循环终止条件说明
# ============================================================
print("\n" + "=" * 60)
print("ReAct 循环终止条件：")
print("=" * 60)
print("""
1. 达到最终答案 - Agent 认为已经收集足够信息回答问题
2. 达到最大迭代次数 - 防止无限循环（默认 recursion_limit）
3. 达到时间上限 - 防止长时间运行

实际应用中：
- 简单问题：1-2 次循环（问天气 -> 调用工具 -> 回答）
- 复杂问题：可能需要 5-10 次循环（多步推理、多次工具调用）
""")

print("\n" + "=" * 60)
print("✅ ReAct 循环机制总结")
print("=" * 60)
print("""
Agent 的自主性体现在：
1. 自主判断是否需要调用工具
2. 自主选择调用哪个工具
3. 自主决定调用顺序（串行/并行）
4. 自主整合多次工具结果给出最终回答
""")