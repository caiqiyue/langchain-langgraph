# -*- coding: utf-8 -*-
"""
【案例 2】统一模型接口 init_chat_model
==========================================

本案例展示如何使用 LangChain 1.0 的 init_chat_model()
这是官方推荐的模型初始化方式，优势是厂商无关

要点：
1. init_chat_model 的优势
2. 一行代码切换不同模型
3. 厂商无关的编程方式
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# 设置环境变量
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 2: init_chat_model 统一接口")
print("=" * 50)

# ============================================================
# init_chat_model 优势
# ============================================================
"""
【拓展：init_chat_model 的优势】

1. 厂商无关：切换模型只需改参数
   from langchain.chat_models import init_chat_model
   model = init_chat_model("gpt-4o", model_provider="openai")
   model = init_chat_model("qwen3-max", model_provider="dashscope")

2. 配置统一：所有模型用相同接口
   temperature, max_tokens, timeout 等参数完全一致

3. 未来可扩展：添加新厂商只需配置
"""

from langchain.chat_models import init_chat_model

# 使用 init_chat_model 初始化
model = init_chat_model(
    model="qwen3-max",
    model_provider="dashscope",
    temperature=0.7,
    max_tokens=200
)

print(f"\n模型类型: {type(model)}")
print(f"模型名称: {model.model_name if hasattr(model, 'model_name') else 'N/A'}")

# 调用模型
response = model.invoke("你好，请介绍一下通义千问")
print(f"\n响应: {response.content[:100]}...")

# ============================================================
# 【对比】直接使用厂商包的区别
# ============================================================
print("\n" + "-" * 30)
print("【对比】直接使用厂商包 vs init_chat_model")
print("-" * 30)

print("""
方式 1 - 直接使用厂商包:
  from langchain_community.chat_models.tongyi import ChatTongyi
  model = ChatTongyi(model="qwen3-max", ...)
  # 问题：切换到 Claude 需要改代码

方式 2 - init_chat_model（推荐）:
  from langchain.chat_models import init_chat_model
  model = init_chat_model("qwen3-max", model_provider="dashscope", ...)
  # 切换只需改参数：init_chat_model("claude-3", model_provider="anthropic")
""")
