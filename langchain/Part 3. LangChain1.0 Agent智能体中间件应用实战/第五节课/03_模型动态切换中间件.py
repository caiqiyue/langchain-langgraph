# -*- coding: utf-8 -*-
"""
【案例 3】@wrap_model_call 模型动态切换中间件
=============================================

本案例展示如何使用 @wrap_model_call 装饰器实现模型动态切换，
根据对话上下文在运行时切换不同的模型。

核心特性：
1. 基于 @wrap_model_call 装饰器
2. 根据对话状态动态选择模型
3. 支持复杂条件判断
4. 完全控制请求和响应

切换策略：
1. 长对话切换到大模型（处理复杂上下文）
2. 包含特定关键词切换到大模型
3. 简单查询使用小模型（节省成本）

要点：
1. 掌握 @wrap_model_call 的完整用法
2. 理解模型切换的策略设计
3. 学会在中间件中访问状态和上下文
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
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse
)
from langchain_core.tools import tool
from typing import Callable, List

print("=" * 60)
print("案例 3: 模型动态切换中间件")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def get_weather(city: str):
    """查询天气"""
    return f"{city} 的天气是晴天"

# ============================================================
# 4. 定义上下文类型
# ============================================================
from typing import TypedDict

class Context(TypedDict):
    """上下文类型"""
    user_role: str  # 用户角色

# ============================================================
# 5. 配置两个模型
# ============================================================
print("\n【模型配置】")
print("-" * 50)

# 小模型 - 快速、便宜
small_model = ChatDeepSeek(model="deepseek-chat", temperature=0)
print(f"小模型: deepseek-chat (快速、便宜)")

# 大模型 - 智能、昂贵
large_model = ChatDeepSeek(model="deepseek-chat", temperature=0.7)
print(f"大模型: deepseek-chat (更智能、但更贵)")

# ============================================================
# 6. 定义复杂任务关键词
# ============================================================
hard_keywords = (
    "证明", "推导", "严谨", "规划", "复杂",
    "多步骤", "chain of thought", "reason step by step",
    "数学", "逻辑证明", "约束求解"
)

# ============================================================
# 7. 动态模型切换中间件
# ============================================================
print("\n【动态模型切换逻辑】")
print("-" * 50)

print("""
切换策略：
1. 对话轮数 > 5 → 切换到大模型
2. 用户输入包含复杂关键词 → 切换到大模型
3. 其他情况 → 使用小模型

判断逻辑：
┌─────────────────────────────────────────┐
│  获取消息列表                           │
└─────────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ 轮数 > 5 ?    │
        └───────┬───────┘
           是/      \\否
           │         │
           ▼         ▼
        切换      ┌───────────────┐
        大模型    │ 包含复杂关键词 ?│
                 └───────┬───────┘
                    是/    \\否
                    │       │
                    ▼       ▼
                 切换      使用
                 大模型    小模型
""")

# ============================================================
# 8. 完整中间件实现
# ============================================================
print("\n" + "=" * 60)
print("完整中间件实现")
print("=" * 60)

print("""
@wrap_model_call
def dynamic_model_router(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    '''
    根据对话上下文动态切换模型
    '''
    # 获取当前对话状态
    state = request.state
    messages = state.get("messages", [])
    print(f"当前对话轮数: {len(messages)}")

    # 获取运行时上下文
    runtime_context = request.runtime.context
    print(f"运行时上下文: {runtime_context}")

    # 切换条件判断
    should_use_large = False

    # 条件1: 长对话（超过5轮）
    if len(messages) > 5:
        print("检测到长对话，切换到大模型")
        should_use_large = True

    # 条件2: 包含复杂任务关键词
    elif messages:
        last_msg = messages[-1].content if messages else ""
        if any(kw in last_msg for kw in hard_keywords):
            print(f"检测到复杂任务，切换到大模型")
            should_use_large = True

    # 执行模型切换
    if should_use_large:
        request = request.override(model=large_model)
        print(">>> 已切换到大模型")
    else:
        print(">>> 使用小模型")

    # 继续处理
    return handler(request)
""")

# ============================================================
# 9. 创建 Agent
# ============================================================
print("\n【创建 Agent】")
print("-" * 50)

print("""
# 使用小模型作为默认模型
agent = create_agent(
    model=small_model,  # 默认使用小模型
    tools=[get_weather],
    middleware=[dynamic_model_router],
    context_schema=Context
)
""")

# ============================================================
# 10. 切换效果对比
# ============================================================
print("\n【切换效果对比】")
print("-" * 50)

效果对比 = """
| 场景                    | 模型选择 | Token 成本 | 响应速度 |
|-----------------------|---------|-----------|---------|
| 简单问答                | 小模型   | $0.001    | 快      |
| 包含"证明"的数学推导    | 大模型   | $0.01     | 慢      |
| 5轮以上对话             | 大模型   | $0.01     | 慢      |
| 日常闲聊                | 小模型   | $0.001    | 快      |

成本节省：约 90%（简单场景使用小模型）
"""
print(效果对比)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)