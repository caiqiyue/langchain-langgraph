# -*- coding: utf-8 -*-
"""
【案例 2】上下文裁剪 trim_messages
=====================================

本案例展示如何使用 trim_messages 控制 Token 消耗。

问题：
- 随着对话进行，messages 会越来越长
- 超过模型上下文限制会报错
- 全部传给 LLM 成本高

解决方案：
- 使用 trim_messages 裁剪过长的历史
- 只保留最近的 N 个 Token
- 平衡上下文完整性和成本

要点：
1. 理解 Token 控制的必要性
2. 掌握 trim_messages 的使用
3. 理解 start_on="human" 的作用
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
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import trim_messages, HumanMessage

print("=" * 60)
print("案例 2: 上下文裁剪 trim_messages")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def search_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city}天气：晴，25°C"

# ============================================================
# 4. 初始化模型
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# ============================================================
# 5. 创建 Agent
# ============================================================
memory = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[search_weather],
    system_prompt="你是一个简洁的助手",
    checkpointer=memory
)

# ============================================================
# 6. 模拟多轮对话（演示裁剪）
# ============================================================
print("\n" + "=" * 60)
print("模拟多轮对话（观察上下文变化）")
print("=" * 60)

config = {"configurable": {"thread_id": "trim_demo"}}

# 模拟多轮对话
对话列表 = [
    "你好，我叫李明",
    "查询北京天气",
    "上海呢？",
    "明天北京天气如何？",
    "我是谁？",
]

for i, query in enumerate(对话列表, 1):
    print(f"\n--- 第 {i} 轮 ---")

    # 获取当前状态
    state = agent.get_state(config)
    msg_count = len(state.values.get("messages", [])) if state else 0
    print(f"当前消息数: {msg_count}")

    # 执行对话
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    }, config=config)

    print(f"用户: {query}")
    print(f"AI: {result['messages'][-1].content}")

# ============================================================
# 7. 手动裁剪示例
# ============================================================
print("\n" + "=" * 60)
print("手动裁剪演示")
print("=" * 60)

# 获取当前所有消息
state = agent.get_state(config)
all_messages = state.values.get("messages", []) if state else []

print(f"裁剪前消息数: {len(all_messages)}")

# 手动裁剪（保留最后3条消息）
MAX_MESSAGES = 3
trimmed_messages = all_messages[-MAX_MESSAGES:] if len(all_messages) > MAX_MESSAGES else all_messages

print(f"裁剪后消息数: {len(trimmed_messages)}")

# ============================================================
# 8. trim_messages 最佳实践
# ============================================================
print("\n" + "=" * 60)
print("✅ trim_messages 最佳实践")
print("=" * 60)
print("""
核心配置：

    trim_messages(
        messages,              # 待裁剪的消息列表
        max_tokens=4000,       # 最大 token 数
        strategy="last",       # 保留策略：last(最新) / first(最旧)
        include_system=True,   # 是否保留系统消息
        start_on="human",     # 从 human 消息开始裁剪
    )

注意事项：
1. max_tokens 根据模型上下文设置（如 128K 模型可设 4000）
2. start_on="human" 确保对话以用户消息开始
3. include_system=True 保留系统提示词
4. 裁剪后消息依然保存在 state 中（完整历史）
""")