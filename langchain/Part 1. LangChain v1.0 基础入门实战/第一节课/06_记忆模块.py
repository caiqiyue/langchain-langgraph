# -*- coding: utf-8 -*-
"""
【案例 6】记忆模块 Memory
==========================================

本案例展示 LangChain 的 Memory 模块
用于保存对话历史，实现多轮对话

要点：
1. ConversationBufferMemory 的用法
2. 保存和加载对话历史
3. 将记忆注入到新的对话中
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 6: 记忆模块 Memory")
print("=" * 50)

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage

# 初始化模型和记忆
model = ChatTongyi(model="qwen3-max", temperature=0.7)
memory = ConversationBufferMemory(
    return_messages=True,  # 返回消息对象，而非字符串
    memory_key="history"   # 在 state 中使用的 key 名
)

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
    memory.save_context(
        {"input": user_msg},      # 用户输入
        {"output": ai_msg}       # AI 回复
    )

print(f"保存了 {len(conversation)} 轮对话")

# ============================================================
# 2. 加载记忆
# ============================================================
print("\n2. 加载记忆")
print("-" * 30)

history = memory.load_memory_variables({})
print(f"记忆中的消息数: {len(history['history'])}")
print("\n记忆内容:")
for msg in history["history"]:
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
history_messages = [("system", system_prompt)]

# 添加历史对话
for msg in history["history"]:
    if isinstance(msg, HumanMessage):
        history_messages.append(("user", msg.content))
    else:
        history_messages.append(("ai", msg.content))

# 添加新问题
history_messages.append(("user", "还记得我叫什么名字吗？"))

# 调用模型
from langchain_core.messages import SystemMessage, HumanMessage

messages = []
for role, content in history_messages:
    if role == "system":
        messages.append(SystemMessage(content=content))
    else:
        messages.append(HumanMessage(content=content))

response = model.invoke(messages)
print(f"\n问: 还记得我叫什么名字吗？")
print(f"答: {response.content}")

# ============================================================
# 【补充】其他 Memory 类型
# ============================================================
print("\n" + "=" * 50)
print("Memory 类型对比")
print("=" * 50)
print("""
| 类型                      | 特点               | 适用场景         |
|--------------------------|-------------------|-----------------|
| ConversationBufferMemory  | 简单存储所有历史    | 短对话          |
| ConversationSummaryMemory | 用 LLM 总结历史    | 长对话          |
| VectorStoreRetrievedMemory | 向量检索相关历史   | 超长对话        |
| CombinedMemory           | 组合多种 Memory    | 复杂场景        |

【为什么需要 Memory 管理？】
1. LLM 有上下文窗口限制
2. API 按 token 计费
3. 太多历史会让模型分心
""")
