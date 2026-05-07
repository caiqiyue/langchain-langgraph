# -*- coding: utf-8 -*-
"""
【案例 1】Agent 概念入门 - 理解 Agent 的基本组成
==================================================

本案例帮助你理解 Agent 的三大核心组成部分：
1. LLM（大模型）= 大脑（项目经理）- 负责思考、规划、决策
2. Tools（工具） = 手脚（执行专员）- 联网搜索、数学计算、数据库查询
3. Agent = 大脑 + 手脚 + 循环机制 - 自主完成复杂任务

要点：
1. 理解 Agent 与普通 LLM 调用的区别
2. 掌握 Agent 的三大组成要素
3. 理解"思考-行动-观察"循环机制
"""

# ============================================================
# 1. 环境配置
# ============================================================
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 2. 导入 LangChain 核心组件
# ============================================================
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

print("=" * 60)
print("案例 1: Agent 概念入门 - 理解 Agent 的基本组成")
print("=" * 60)

# ============================================================
# 3. 定义一个简单的工具（Tools = 执行专员的手脚）
# ============================================================
@tool
def multiply(a: int, b: int) -> int:
    """
    计算两个整数的乘积。

    参数:
        a (int): 第一个整数
        b (int): 第二个整数

    返回:
        int: 两个数的乘积
    """
    return a * b

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息（模拟数据）。

    参数:
        city (str): 城市名称

    返回:
        str: 天气信息
    """
    weather_data = {
        "北京": "晴朗，气温25°C，适合外出",
        "上海": "多云，气温28°C，稍有闷热",
        "广州": "小雨，气温30°C，记得带伞",
        "深圳": "晴天，气温29°C，适宜活动"
    }
    return weather_data.get(city, f"抱歉，暂不支持查询{city}的天气")

# ============================================================
# 4. 初始化大模型（LLM = 大脑/项目经理）
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

print(f"\n模型类型: {type(model).__name__}")
print(f"模型名称: {model.model_name if hasattr(model, 'model_name') else 'qwen3-max'}")

# ============================================================
# 5. 普通 LLM vs Agent 的区别
# ============================================================
print("\n" + "-" * 50)
print("普通 LLM 调用（没有工具，只能依靠训练知识）:")
print("-" * 50)

# 普通调用：LLM 只能依靠训练知识回答，无法获取实时信息
普通回答 = model.invoke([
    ("human", "北京今天的天气怎么样？适合穿什么？")
])
print(f"北京天气问题: {普通回答.content[:100]}...")

print("\n" + "-" * 50)
print("Agent 调用（有工具，可以执行计算、查询实时信息）:")
print("-" * 50)

# ============================================================
# 6. 构建 Agent（LLM + Tools + 循环机制）
# ============================================================
from langchain.agents import create_agent

# 创建 Agent：模型 + 工具列表 + 系统提示词
agent = create_agent(
    model=model,
    tools=[multiply, get_weather],  # 给 Agent 装备工具
    system_prompt="""你是一个智能助手，能够：
1. 查询天气（使用 get_weather 工具）
2. 进行数学计算（使用 multiply 工具）

请根据用户的问题，自主决定是否需要调用工具。"""
)

# ============================================================
# 7. 调用 Agent 执行任务
# ============================================================
print("\n用户问题：北京的天气怎么样？如果气温高于25度就说热，低于25度就说凉快")

# Agent 会自动：思考 -> 选择工具 -> 执行 -> 观察结果 -> 再次思考...
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "北京的天气怎么样？如果气温高于25度就说热，低于25度就说凉快"
    }]
})

# 获取最终回答
最终回答 = result["messages"][-1].content
print(f"\nAgent 回答: {最终回答}")

# ============================================================
# 8. 观察 Agent 的思考过程（查看中间步骤）
# ============================================================
print("\n" + "=" * 60)
print("Agent 完整执行过程（ReAct 循环）:")
print("=" * 60)

# 重新执行，这次查看所有消息
result_full = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "帮我计算一下 15 乘以 8 等于多少"
    }]
})

# 打印每一步
for i, msg in enumerate(result_full["messages"]):
    if hasattr(msg, "type"):
        if msg.type == "human":
            print(f"\n[步骤 {i}] 用户: {msg.content}")
        elif msg.type == "ai":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"[步骤 {i}] AI 思考: 我需要调用工具")
                for tc in msg.tool_calls:
                    print(f"         -> 工具: {tc['name']}, 参数: {tc['args']}")
            else:
                print(f"[步骤 {i}] AI 回答: {msg.content}")
        elif msg.type == "tool":
            print(f"[步骤 {i}] 工具结果: {msg.content}")