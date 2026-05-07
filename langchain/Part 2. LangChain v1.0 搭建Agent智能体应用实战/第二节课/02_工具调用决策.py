# -*- coding: utf-8 -*-
"""
【案例 2】Agent 工具调用决策 - 展示 Agent 如何选择工具
========================================================

本案例展示 Agent 的推理与规划能力（Reasoning & Planning）

当用户提出一个问题时，Agent 需要：
1. 理解用户意图
2. 判断是否需要调用工具
3. 选择最合适的工具
4. 构造正确的参数

这整个过程都是 Agent 自主完成的。

要点：
1. 观察 Agent 如何分析用户问题
2. 理解工具选择的过程
3. 理解不同问题类型需要不同工具
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
print("案例 2: Agent 工具调用决策")
print("=" * 60)

# ============================================================
# 3. 定义不同类型的工具
# ============================================================

# --- 搜索工具 ---
@tool
def web_search(query: str) -> str:
    """
    使用搜索引擎搜索网络信息。

    适用场景：
    - 查询实时新闻、天气、股价
    - 查找不知道的知识点
    - 获取最新发生的事件

    参数:
        query (str): 搜索关键词
    """
    search_results = {
        "OpenAI": "OpenAI 成立于2015年，是一家人工智能研究公司",
        "LangChain": "LangChain 是一个用于构建 LLM 应用的框架",
        "Python": "Python 是一种高级编程语言，简洁易学"
    }
    return search_results.get(query, f"搜索结果：{query}的相关信息...")

# --- 计算工具 ---
@tool
def calculator(expression: str) -> str:
    """
    执行数学计算。

    适用场景：
    - 算术运算（加减乘除）
    - 复杂数学表达式
    - 数据统

    参数:
        expression (str): 数学表达式，如 "2+3*5"
    """
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

# --- 知识查询工具 ---
@tool
def query_knowledge(topic: str) -> str:
    """
    查询内置知识库。

    适用场景：
    - 事实性知识查询
    - 概念解释
    - 已知确定的信息

    参数:
        topic (str): 查询主题
    """
    knowledge_db = {
        "水的沸点": "水的沸点是100°C（在标准大气压下）",
        "光的速": "光速约为299,792公里/秒",
        "地球半径": "地球平均半径约为6,371公里"
    }
    return knowledge_db.get(topic, f"关于'{topic}'的知识：这是一个知识库查询结果")

# --- 日期时间工具 ---
@tool
def get_current_time(location: str = "本地") -> str:
    """
    获取当前日期和时间。

    适用场景：
    - 需要知道当前时间
    - 安排日程
    - 时间相关计算

    参数:
        location (str): 地点（可选）
    """
    return f"当前时间（{location}）：2024年12月15日 14:30:00"

# ============================================================
# 4. 初始化模型并创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

agent = create_agent(
    model=model,
    tools=[web_search, calculator, query_knowledge, get_current_time],
    system_prompt="""你是一个智能助手，拥有多种工具可以帮助用户。

工具说明：
- web_search: 搜索网络信息，用于查询实时信息或不知道的知识
- calculator: 数学计算，用于计算数学表达式
- query_knowledge: 查询内置知识库，用于查询确定的事实
- get_current_time: 获取当前时间

请根据用户的问题，自主判断应该使用哪个工具。"""
)

# ============================================================
# 5. 测试不同类型的问题
# ============================================================
test_questions = [
    ("搜索问题", "帮我搜索一下 OpenAI 是什么公司"),
    ("计算问题", "请计算一下 (25 + 15) * 2 除以 4 等于多少"),
    ("知识问题", "水的沸点是多少度？"),
    ("时间问题", "现在几点了？"),
    ("无需工具", "你好，今天心情不错"),
]

print("\n" + "=" * 60)
print("测试不同类型问题的工具选择")
print("=" * 60)

for q_type, question in test_questions:
    print(f"\n{'='*50}")
    print(f"【{q_type}】问题: {question}")
    print("-" * 50)

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    # 分析结果
    ai_msg = result["messages"][-1]
    tool_calls = getattr(ai_msg, "tool_calls", None)

    if tool_calls:
        print(f"Agent 决策：需要调用工具")
        for tc in tool_calls:
            print(f"  → 选择工具: {tc['name']}")
            print(f"    参数: {tc['args']}")
    else:
        print(f"Agent 决策：无需调用工具，直接回答")
        print(f"  回答: {ai_msg.content[:100]}...")

# ============================================================
# 6. 复杂问题：需要多个工具
# ============================================================
print("\n" + "=" * 60)
print("复杂问题：需要多个工具协作")
print("=" * 60)

complex_question = "水的沸点是多少度？如果我要把这个温度从摄氏度转换成华氏度，结果是多少？"

print(f"\n问题: {complex_question}")
print("\n执行过程：")

result = agent.invoke({
    "messages": [{"role": "user", "content": complex_question}]
})

for i, msg in enumerate(result["messages"]):
    msg_type = getattr(msg, "type", "unknown")

    if msg_type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"[步骤 {i}] Agent 决策:")
        for tc in msg.tool_calls:
            print(f"  → 调用工具: {tc['name']}")
            print(f"    参数: {tc['args']}")

    elif msg_type == "tool":
        print(f"[步骤 {i}] 工具结果: {msg.content}")

    elif msg_type == "ai" and not hasattr(msg, "tool_calls"):
        print(f"[最终] Agent 回答: {msg.content}")