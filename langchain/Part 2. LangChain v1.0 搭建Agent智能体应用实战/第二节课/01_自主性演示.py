# -*- coding: utf-8 -*-
"""
【案例 1】Agent 自主性演示 - 展示 Agent 无需人类干预完成任务
================================================================

本案例展示 Agent 的核心特征之一：自主性（Autonomy）

自主性 = Agent 能够在没有人类直接干预的情况下，
         独立完成"感知-规划-决策-行动"的全过程。

对比：
- 普通 LLM：需要人类明确告诉做什么
- Agent：只需要给目标，自主决定如何实现

要点：
1. 理解自主性的含义
2. 观察 Agent 如何自主判断和行动
3. 对比普通 LLM 与 Agent 的行为差异
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
print("案例 1: Agent 自主性演示")
print("=" * 60)

# ============================================================
# 3. 定义工具集（Agent 的"能力装备"）
# ============================================================
@tool
def search_online(query: str) -> str:
    """
    搜索互联网获取实时信息。

    参数:
        query (str): 搜索关键词

    返回:
        str: 搜索结果摘要
    """
    # 模拟搜索结果
    results = {
        "天气": "北京今天晴朗，气温22-28°C，适宜出行",
        "新闻": "今日要闻：AI技术持续发展，LangChain 1.0正式发布",
        "股价": "AAPL 股价：$178.50，较昨日上涨2.3%"
    }
    return results.get(query, f"关于'{query}'的搜索结果：这是一条模拟的搜索结果")

@tool
def send_email(recipient: str, content: str) -> str:
    """
    发送电子邮件。

    参数:
        recipient (str): 收件人邮箱
        content (str): 邮件内容

    返回:
        str: 发送结果
    """
    return f"✅ 邮件已发送给 {recipient}，内容：{content[:50]}..."

@tool
def create_report(data: str) -> str:
    """
    根据数据创建分析报告。

    参数:
        data (str): 输入数据

    返回:
        str: 生成的报告
    """
    return f"📊 报告已生成：基于{data}的分析报告完成，共5页"

# ============================================================
# 4. 初始化模型并创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# 创建具有自主性的 Agent
agent = create_agent(
    model=model,
    tools=[search_online, send_email, create_report],
    system_prompt="""你是一个智能助手，能够自主完成任务。

当用户给你一个目标时，你应该：
1. 分析目标，确定需要哪些步骤
2. 自主决定调用哪些工具
3. 按照合理的顺序执行
4. 整合结果，给出完整回答

你不需要用户告诉你具体怎么做，只需要用户提供目标。"""
)

# ============================================================
# 5. 展示自主性：给目标，不给具体指令
# ============================================================
print("\n" + "=" * 60)
print("普通 LLM vs Agent：对待同一个问题")
print("=" * 60)

问题 = "帮我了解一下今天的天气情况，然后给老板发一封邮件汇报，并生成一份报告"

print(f"\n用户（只给目标）：'{问题}'")
print("\n" + "不使用工具" * 30)
普通回答 = model.invoke([
    ("human", 问题)
])
print(f"普通 LLM 回答：\n{普通回答.content[:200]}...")

print("\n" + "=" * 60)
print("使用 Agent（自主决策如何实现目标）:")
print("=" * 60)

# ============================================================
# 6. 调用 Agent，观察自主行为
# ============================================================
result = agent.invoke({
    "messages": [{"role": "user", "content": 问题}]
})

print("\n执行过程：")
for i, msg in enumerate(result["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "human":
        print(f"\n[步骤 {i}] 用户目标: {msg.content}")

    elif msg_type == "ai":
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[步骤 {i}] AI 自主决策:")
            for tc in msg.tool_calls:
                print(f"         → 调用工具: {tc['name']}")
                print(f"           输入: {tc['args']}")
        else:
            print(f"[步骤 {i}] AI 最终回答: {msg.content[:150]}...")

    elif msg_type == "tool":
        print(f"[步骤 {i}] 工具执行结果: {msg.content[:80]}...")

# ============================================================
# 7. 自主性总结
# ============================================================
print("\n" + "=" * 60)
print("✅ 自主性 (Autonomy) 总结")
print("=" * 60)
print("""
Agent 自主性的体现：

1. 【目标导向】
   - 用户说"帮我查天气并发邮件"
   - Agent 自主分解为：查天气 → 发邮件 → 报告

2. 【工具选择】
   - 用户没有说"用哪个工具"
   - Agent 自主判断：search_online 查天气，send_email 发邮件

3. 【执行顺序】
   - 用户没有说"先做什么后做什么"
   - Agent 自主决定：先查天气，再发邮件，最后报告

4. 【无需干预】
   - 整个过程 Agent 自主完成
   - 用户只需要提供最终目标

这就是自主性的核心：用户说"要什么"，Agent 决定"怎么做"
""")