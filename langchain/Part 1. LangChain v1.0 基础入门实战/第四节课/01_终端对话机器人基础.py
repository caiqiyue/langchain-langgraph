# -*- coding: utf-8 -*-
"""
【案例 1】终端对话机器人基础
==========================================

本案例展示构建一个基础终端对话机器人

要点：
1. 模型初始化
2. 消息历史管理
3. 主循环
4. 流式输出
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 1: 终端对话机器人基础")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ============================================================
# 1. 初始化
# ============================================================
print("\n1. 初始化")
print("-" * 30)

model = ChatTongyi(
    model="qwen3-max",
    temperature=0.7,
    max_tokens=512
)

system_message = SystemMessage(content="""你叫小智，是一名乐于助人的智能助手。

请在对话中：
- 保持友好、有耐心、温和的语气
- 回答问题专业且易懂
- 适当使用 emoji 增添趣味""")

messages = [system_message]

print(f"模型初始化完成: {model.__class__.__name__}")
print(f"系统提示已设置: {len(system_message.content)} 字符")

# ============================================================
# 2. 主循环伪代码
# ============================================================
print("\n2. 主循环逻辑")
print("-" * 30)

print("""
while True:
    user_input = input("👤 你：")
    if user_input.lower() in ["exit", "quit"]:
        break

    # 1. 保存用户消息
    messages.append(HumanMessage(content=user_input))

    # 2. 流式输出 AI 回复
    print("🤖 小智：", end="", flush=True)
    full_reply = ""
    for chunk in model.stream(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_reply += chunk.content
    print()

    # 3. 保存 AI 回复
    messages.append(AIMessage(content=full_reply))

    # 4. 限制历史长度
    MAX_MESSAGES = 50
    if len(messages) > MAX_MESSAGES:
        messages = [system_message] + messages[-(MAX_MESSAGES-1):]
""")

# ============================================================
# 3. 模拟对话
# ============================================================
print("\n3. 模拟对话示例")
print("-" * 30)

simulated_conversation = [
    ("你好！", "你好！有什么可以帮助你的吗？😊"),
    ("你叫什么名字？", "我叫小智，是你的智能助手！"),
    ("今天天气如何？", "今天天气晴朗，温度大约25度，非常适合出门走走！☀️"),
]

print("模拟对话:")
for user, bot in simulated_conversation:
    print(f"👤 用户: {user}")
    print(f"🤖 AI: {bot}")
    print()

print("\n" + "=" * 50)
print("实际运行：复制完整代码到终端执行")
print("=" * 50)
