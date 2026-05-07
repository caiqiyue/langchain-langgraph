# -*- coding: utf-8 -*-
"""
【案例 3】langchain 主包 - create_agent
==========================================

本案例展示 langchain 主包的核心 API
create_agent 是创建智能体的核心函数

要点：
1. create_agent 的用法
2. Agent 的调用方式
3. Agent 执行结果的结构
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 3: langchain 主包 - create_agent")
print("=" * 50)

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi

# ============================================================
# 1. 定义工具
# ============================================================
@tool
def get_weather(city: str) -> str:
    """查询城市天气

    Args:
        city: 城市名称

    Returns:
        天气信息字符串
    """
    weather_db = {
        "北京": "多云转晴，25°C",
        "上海": "小雨，22°C",
        "深圳": "晴天，28°C"
    }
    return weather_db.get(city, "暂无数据")

@tool
def calculate(expression: str) -> str:
    """执行数学计算

    Args:
        expression: 数学表达式，如 "2+3*4"

    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算错误"

# ============================================================
# 2. 创建 Agent
# ============================================================
print("\n2. 创建 Agent")
print("-" * 30)

model = ChatTongyi(model="qwen3-max", temperature=0.7)

# create_agent 的核心参数：
# - model: 智力来源（大语言模型）
# - tools: 能力扩展（工具列表）
agent = create_agent(
    model=model,
    tools=[get_weather, calculate]
)

print(f"Agent 类型: {type(agent)}")
print(f"Agent 可调用方法: {[m for m in dir(agent) if not m.startswith('_')][:5]}...")

# ============================================================
# 3. 调用 Agent
# ============================================================
print("\n3. 调用 Agent")
print("-" * 30)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "北京今天天气怎么样？顺便帮我计算 123 * 456"
    }]
})

print(f"结果类型: {type(result)}")
print(f"结果键: {result.keys()}")

print("\n消息历史:")
for msg in result["messages"]:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    if content:
        preview = content[:50] + "..." if len(str(content)) > 50 else content
        print(f"  [{role}]: {preview}")

# ============================================================
# 【补充】create_agent 底层原理
# ============================================================
print("\n" + "=" * 50)
print("create_agent 底层原理")
print("=" * 50)
print("""
【create_agent 内部实现】

1. 将模型和工具绑定
   - 调用 model.bind_tools(tools)
   - 模型获得调用工具的能力

2. 创建 LangGraph StateGraph
   - nodes: 处理各个步骤
   - edges: 定义流程
   - state: 在步骤间传递数据

3. 配置消息处理逻辑
   - 自动处理 Function Calling
   - 循环直到得到最终回复

【为什么基于 LangGraph？】

因为 Agent 需要：
- 循环：思考 → 工具调用 → 观察结果 → 再思考
- 条件分支：需要工具吗？调用哪个？
- 状态管理：在步骤间传递数据

简单的 Chain 无法满足这些需求。
""")
