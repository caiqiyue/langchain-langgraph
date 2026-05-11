# -*- coding: utf-8 -*-
"""
【案例 6】记忆模块 Memory
==========================================

本案例展示 LangChain 的 Memory 模块
用于保存对话历史，实现多轮对话

要点：
1. InMemoryChatMessageHistory 的用法
2. 保存和加载对话历史
3. 将记忆注入到新的对话中
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / ".env"
load_dotenv(env_path, override=True)

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")
os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 6: 记忆模块 Memory")
print("=" * 50)

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 初始化模型和记忆
model = ChatTongyi(model="qwen3-max", temperature=0.7)
chat_history = InMemoryChatMessageHistory()

# ============================================================
# 1. 保存对话到记忆
# ============================================================
print("\n1. 保存对话到记忆")
print("-" * 30)

conversation = [
    ("你好，我叫张三", "你好张三！很高兴认识你。"),
    ("我喜欢吃火锅", "火锅是很棒的选择！您喜欢什么口味的锅底？"),
    ("我喜欢麻辣锅底", "麻辣锅底确实很过瘾！但要注意不要太过刺激哦。"),
]

# 保存对话
for user_msg, ai_msg in conversation:
    chat_history.add_user_message(user_msg)
    chat_history.add_ai_message(ai_msg)

print(f"保存了 {len(conversation)} 轮对话")

# ============================================================
# 2. 加载记忆
# ============================================================
print("\n2. 加载记忆")
print("-" * 30)

messages = chat_history.messages
print(f"记忆中的消息数: {len(messages)}")
print("\n记忆内容:")
for msg in messages:
    role = "用户" if isinstance(msg, HumanMessage) else "AI"
    preview = msg.content[:25] + "..." if len(msg.content) > 25 else msg.content
    print(f"  [{role}]: {preview}")

# ============================================================
# 3. 利用记忆进行对话
# ============================================================
print("\n3. 利用记忆进行对话")
print("-" * 30)

# 构建带记忆的对话
system_prompt = "你是一个友好的助手，请基于对话历史回答问题。"
history_messages = [SystemMessage(content=system_prompt)]

# 添加历史对话
for msg in messages:
    history_messages.append(msg)

# 添加新问题
history_messages.append(HumanMessage(content="还记得我叫什么名字吗？"))

response = model.invoke(history_messages)
print(f"\n问: 还记得我叫什么名字吗？")
print(f"答: {response.content}")

# ============================================================
# 【补充】Memory 管理策略
# ============================================================
print("\n" + "=" * 50)
print("Memory 管理策略")
print("=" * 50)
print("""
| 策略                      | 特点               | 适用场景         |
|--------------------------|-------------------|-----------------|
| InMemoryChatMessageHistory | 简单存储所有历史    | 短对话/开发测试   |
| 消息修剪 (trim_messages)   | 自动修剪超长历史    | 长对话          |
| 摘要记忆 (SummaryMemory)   | 用 LLM 总结历史    | 超长对话        |
| 向量检索记忆               | 向量检索相关历史   | 超长对话        |

【为什么需要 Memory 管理？】
1. LLM 有上下文窗口限制
2. API 按 token 计费
3. 太多历史会让模型分心

【LangChain 1.0 的变化】
- ConversationBufferMemory → InMemoryChatMessageHistory
- 使用 add_user_message / add_ai_message 添加消息
- 使用 chat_history.messages 获取历史消息
""")
