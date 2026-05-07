# -*- coding: utf-8 -*-
"""
【案例 1】LLM 和 ChatModel 的区别
==========================================

本案例展示 LangChain 区分的两种模型类型

要点：
1. LLM：文本进，文本出
2. ChatModel：消息进，消息出
3. 历史原因和设计考虑
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 1: LLM 和 ChatModel 的区别")
print("=" * 50)

# ============================================================
# 1. 两种模型类型对比
# ============================================================
print("\n1. 两种模型类型对比")
print("-" * 30)

print("""
┌─────────────────────────────────────────────────────────────┐
│  LLM (Large Language Model)                                  │
│  - 输入：纯文本                                              │
│  - 输出：纯文本                                              │
│  - 代表：text-davinci-003, LLaMA                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ChatModel (Chat Language Model)                             │
│  - 输入：消息列表 [SystemMessage, HumanMessage, ...]         │
│  - 输出：AIMessage                                          │
│  - 代表：GPT-4, Claude, Gemini, 通义千问                    │
└─────────────────────────────────────────────────────────────┘
""")

from langchain_community.chat_models.tongyi import ChatTongyi

# ChatModel 例子
model = ChatTongyi(model="qwen3-max", temperature=0.7)

# ChatModel 输入：消息列表
messages = [
    {"role": "system", "content": "你是一个有帮助的助手"},
    {"role": "user", "content": "翻译成英文：你好世界"}
]

response = model.invoke(messages)
print(f"ChatModel 输入类型: {type(messages)}")
print(f"ChatModel 输出类型: {type(response)}")
print(f"ChatModel 输出: {response.content}")

# ============================================================
# 2. 为什么需要区分？
# ============================================================
print("\n2. 为什么 LangChain 要区分？")
print("-" * 30)

print("""
1. 更好的类型安全
   - 消息有明确角色（system/user/assistant）
   - 可以验证消息结构

2. 支持多模态
   - ChatModel 的 content 可以是文本+图片
   - LLM 只有纯文本

3. 更清晰的语义
   - 明确谁在说话
   - 便于管理和调试

4. 历史原因
   - GPT-2: 只有 LLM（语言模型）
   - GPT-3: 引入 ChatML
   - GPT-3.5+: 完全基于消息格式
""")

# ============================================================
# 【补充】实际上它们调用的是同一个 API
# ============================================================
print("\n" + "=" * 50)
print("底层：它们调用的是同一个 API")
print("=" * 50)
print("""
无论是 LLM 还是 ChatModel：

OpenAI API:
- LLM: POST /v1/completions
- ChatModel: POST /v1/chat/completions

区别只是输入格式不同。

LangChain 区分它们是为了：
- 更清晰的 API
- 更好的类型提示
- 支持更复杂的功能（多模态、工具调用等）
""")
