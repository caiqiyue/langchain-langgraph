# -*- coding: utf-8 -*-
"""
【案例 1】短期记忆 InMemorySaver
==================================

本案例展示如何使用 InMemorySaver 实现 Agent 的短期记忆。

短期记忆（Checkpointer）的核心概念：
- 存储位置：内存（Python dict）
- 生命周期：与 thread_id 绑定，会话结束则丢失
- 作用：维持同一会话内的上下文连贯

关键要素：
1. Checkpointer：记忆存储对象
2. thread_id：会话唯一标识（用户级隔离）
3. config：配置字典，传入 thread_id

要点：
1. 理解 Checkpointer 的作用
2. 掌握 thread_id 的使用
3. 观察记忆在多轮对话中的效果
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

print("=" * 60)
print("案例 1: 短期记忆 InMemorySaver")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def get_user_info(name: str) -> str:
    """查询用户信息"""
    user_db = {
        "陈明": {"age": 28, "hobby": "旅游、滑雪、喝茶"},
        "张三": {"age": 32, "hobby": "编程、阅读、电影"}
    }
    info = user_db.get(name, {"age": "未知", "hobby": "未知"})
    return f"姓名: {name}, 年龄: {info['age']}岁, 爱好: {info['hobby']}"

# ============================================================
# 4. 初始化模型
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# ============================================================
# 5. 创建带短期记忆的 Agent
# ============================================================
memory = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[get_user_info],
    checkpointer=memory  # 启用短期记忆
)

print("\n✅ Agent 创建成功，已启用 InMemorySaver 短期记忆")

# ============================================================
# 6. 演示记忆功能
# ============================================================
print("\n" + "=" * 60)
print("演示：同一会话内的记忆")
print("=" * 60)

# 配置：thread_id 作为会话 ID
config = {"configurable": {"thread_id": "user_123"}}

# 第一轮对话
print("\n--- 第一轮对话 ---")
response1 = agent.invoke({
    "messages": [{"role": "user", "content": "你好，我叫陈明，好久不见！"}]
}, config=config)
print(f"用户：你好，我叫陈明，好久不见！")
print(f"AI: {response1['messages'][-1].content}")

# 第二轮对话（相同 thread_id，测试记忆）
print("\n--- 第二轮对话（相同 thread_id）---")
response2 = agent.invoke({
    "messages": [{"role": "user", "content": "请问你还记得我叫什么名字吗？"}]
}, config=config)  # 相同 thread_id，自动携带上下文
print(f"用户：请问你还记得我叫什么名字吗？")
print(f"AI: {response2['messages'][-1].content}")

# 查看记忆状态
state = agent.get_state(config)
print(f"\n当前记忆状态：共 {len(state.values['messages'])} 条消息")

# ============================================================
# 7. 测试：新会话无记忆
# ============================================================
print("\n" + "=" * 60)
print("演示：新会话无记忆（不同 thread_id）")
print("=" * 60)

# 新会话
config2 = {"configurable": {"thread_id": "user_456"}}

response3 = agent.invoke({
    "messages": [{"role": "user", "content": "我们之前聊过吗？"}]
}, config=config2)  # 不同 thread_id，无历史记忆
print(f"用户：我们之前聊过吗？")
print(f"AI（新会话）: {response3['messages'][-1].content}")

# ============================================================
# 8. 短期记忆总结
# ============================================================
print("\n" + "=" * 60)
print("✅ 短期记忆（Checkpointer）总结")
print("=" * 60)
print("""
┌─────────────────────────────────────────────────────────────┐
│                  短期记忆 (Checkpointer)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【存储位置】                                                │
│  • InMemorySaver：内存（Python dict）                       │
│  • PostgresSaver：PostgreSQL 数据库                         │
│                                                             │
│  【生命周期】                                                │
│  • 与 thread_id 绑定                                        │
│  • 会话结束 → 记忆丢失                                       │
│  • 进程重启 → InMemorySaver 记忆丢失                         │
│                                                             │
│  【数据隔离】                                                │
│  • 不同 thread_id 完全隔离                                   │
│  • 相同 thread_id 共享记忆                                   │
│                                                             │
│  【适用场景】                                                │
│  ✅ 单会话内的上下文连贯                                      │
│  ✅ 开发/测试环境                                            │
│  ❌ 需要持久化的生产环境                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

关键代码：
    checkpointer = InMemorySaver()
    config = {"configurable": {"thread_id": "唯一ID"}}
    agent.invoke({"messages": [...]}, config=config)
""")