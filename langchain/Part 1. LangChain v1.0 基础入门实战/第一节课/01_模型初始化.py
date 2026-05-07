# -*- coding: utf-8 -*-
"""
【案例 1】模型初始化 - 通义千问 qwen3-max
============================================

本案例展示如何使用 LangChain 初始化通义千问模型

要点：
1. 配置 DashScope API
2. 使用 ChatTongyi 封装类
3. 简单的模型调用
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# 设置 DashScope 配置
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# ============================================================
# 2. 使用 langchain-community 的 ChatTongyi
# ============================================================
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage

print("=" * 50)
print("案例 1: 模型初始化 - 通义千问 qwen3-max")
print("=" * 50)

# 初始化模型
model = ChatTongyi(
    model="qwen3-max",
    temperature=0.7,
    max_tokens=200
)

print(f"\n模型类型: {type(model).__name__}")
print(f"模型名称: {model.model_name}")

# ============================================================
# 3. 简单的对话调用
# ============================================================
messages = [
    SystemMessage(content="你是一个有帮助的助手"),
    HumanMessage(content="用一句话介绍自己")
]

response = model.invoke(messages)

print(f"\n用户: 用一句话介绍自己")
print(f"AI: {response.content}")
