# -*- coding: utf-8 -*-
"""
【案例 2】@dynamic_prompt 装饰器 - 动态提示词中间件
==================================================

本案例展示如何使用 @dynamic_prompt 装饰器创建动态提示词中间件，
根据运行时上下文动态注入不同的 System Prompt。

核心特性：
1. 基于装饰器的简洁写法
2. 运行时上下文感知
3. 条件化提示词注入
4. 无需继承 AgentMiddleware

@dynamic_prompt 装饰器：
- 简化了 wrap_model_call 的写法
- 自动处理 ModelRequest/Response 的封装
- 返回字符串作为动态 System Prompt

要点：
1. 理解 @dynamic_prompt 的简化机制
2. 掌握根据上下文动态生成提示词
3. 理解与 @wrap_model_call 的区别
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
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.tools import tool

print("=" * 60)
print("案例 2: @dynamic_prompt 动态提示词装饰器")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": "晴朗，气温25°C",
        "上海": "多云，气温28°C",
        "广州": "小雨，气温30°C"
    }
    return f"{city}的天气是：{weather_data.get(city, '未知')}"

# ============================================================
# 4. 定义上下文类型
# ============================================================
from typing import TypedDict

class Context(TypedDict):
    """上下文类型"""
    user_role: str  # 用户角色

# ============================================================
# 5. @dynamic_prompt 示例
# ============================================================
print("\n【@dynamic_prompt 装饰器】")
print("-" * 50)

@dynamic_prompt
def role_based_prompt(request: ModelRequest):
    """
    根据用户角色生成不同的 System Prompt

    @dynamic_prompt 装饰器会自动：
    1. 从 request.runtime.context 获取上下文
    2. 执行函数返回提示词字符串
    3. 将提示词作为 System Prompt 注入
    """
    # 获取运行时上下文
    user_role = request.runtime.context.get("user_role", "user")
    print(f"检测到用户角色: {user_role}")

    # 根据角色返回不同的提示词
    if user_role == "expert":
        return """你是一个专业气象分析师，提供详细数据。
请使用专业术语，列出温度、湿度、风速、气压等详细信息。"""

    elif user_role == "beginner":
        return """你是一个友善的天气助手，用简单易懂的语言解释。
请使用比喻和日常用语，避免专业术语，让普通人也能理解。"""

    else:
        return """你是一个简洁的天气助手。
请直接给出天气信息，不需要过多解释。"""

print("装饰器已定义: role_based_prompt")

# ============================================================
# 6. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【执行流程】

用户请求（含上下文
{user_role: "expert"}
    │
    ▼
┌─────────────────────────────────────┐
│  @dynamic_prompt 装饰器             │
│                                     │
│  1. 提取 request.runtime.context   │
│  2. 调用 role_based_prompt(request)│
│  3. 获取返回的提示词字符串          │
└─────────────────────────────────────┘
    │
    ▼
【生成 System Prompt】
┌─────────────────────────────────────┐
│ 你是一个专业气象分析师，提供详细数据。│
│ 请使用专业术语，列出温度、湿度、     │
│ 风速、气压等详细信息。              │
└─────────────────────────────────────┘
    │
    ▼
【注入到消息列表】
messages = [
    SystemMessage(content=提示词),
    HumanMessage(content="北京天气如何？")
]
    │
    ▼
发送给模型
""")

# ============================================================
# 7. @dynamic_prompt vs @wrap_model_call
# ============================================================
print("\n【@dynamic_prompt vs @wrap_model_call】")
print("-" * 50)

对比表 = """
| 维度        | @dynamic_prompt           | @wrap_model_call      |
|------------|-------------------------|----------------------|
| 返回值      | 字符串（System Prompt）   | ModelResponse 对象    |
| 复杂度      | 简单                     | 复杂                 |
| 适用场景    | 动态提示词                | 完整中间件逻辑        |
| 可修改内容   | 仅 System Prompt         | 模型、消息、工具等    |
| 灵活性      | 有限                     | 完全灵活             |
"""
print(对比表)

# ============================================================
# 8. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

# 1. 定义动态提示词函数
@dynamic_prompt
def role_based_prompt(request: ModelRequest):
    user_role = request.runtime.context.get("user_role", "user")

    prompts = {
        "expert": "你是一个专业气象分析师...",
        "beginner": "你是一个友善的天气助手...",
        "default": "你是一个简洁的天气助手..."
    }
    return prompts.get(user_role, prompts["default"])

# 2. 创建 Agent
agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    middleware=[role_based_prompt],
    context_schema=Context
)

# 3. 专家角色调用
response1 = agent.invoke(
    {"messages": [{"role": "user", "content": "北京天气"}]},
    context={"user_role": "expert"}
)
# → 使用专业提示词

# 4. 新手角色调用
response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "北京天气"}]},
    context={"user_role": "beginner"}
)
# → 使用简单提示词
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)