# -*- coding: utf-8 -*-
"""
【案例 2】init_chat_model 统一接口
==========================================

本案例展示 LangChain 1.0 推荐的模型初始化方式

要点：
1. init_chat_model 的优势
2. 如何一行代码切换模型
3. 支持的 provider 列表
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

print("=" * 50)
print("案例 2: init_chat_model 统一接口")
print("=" * 50)

from langchain.chat_models import init_chat_model

# ============================================================
# 1. 使用 init_chat_model
# ============================================================
print("\n1. 使用 init_chat_model")
print("-" * 30)

# 初始化通义千问（通过 deepseek provider，因为 dashscope 不在支持列表中）
# 注意：如果使用其他 provider，请确保对应的 API Key 已设置
try:
    model = init_chat_model(
        model="qwen3-max",
        model_provider="deepseek",  # 改用 deepseek 作为示例
        temperature=0.7,
        max_tokens=200
    )
    print(f"模型类型: {type(model)}")
    print(f"模型名称: {model.model_name if hasattr(model, 'model_name') else 'N/A'}")
    response = model.invoke("你好，请介绍一下自己")
    print(f"响应: {response.content[:80]}...")
except Exception as e:
    print(f"模型调用出错: {e}")
    print("提示: 请确保对应的 API Key 已正确设置在 .env 文件中")

# ============================================================
# 2. 一行代码切换模型
# ============================================================
print("\n2. 一行代码切换模型")
print("-" * 30)

print("""
# 切换到 DeepSeek
model = init_chat_model("deepseek-chat", model_provider="deepseek")

# 切换到 OpenAI（需要 OPENAI_API_KEY）
# model = init_chat_model("gpt-4o", model_provider="openai")

# 切换到 Anthropic（需要 ANTHROPIC_API_KEY）
# model = init_chat_model("claude-3-5-sonnet", model_provider="anthropic")

# 切换到 Google（需要 GOOGLE_API_KEY）
# model = init_chat_model("gemini-pro", model_provider="google")

# 切换到本地 Ollama
# model = init_chat_model("llama3", model_provider="ollama")
""")

# ============================================================
# 3. 支持的 provider
# ============================================================
print("\n3. 支持的 provider")
print("-" * 30)

providers = [
    ("openai", "OpenAI", "GPT-4, GPT-3.5", "OPENAI_API_KEY"),
    ("anthropic", "Anthropic", "Claude 3 系列", "ANTHROPIC_API_KEY"),
    ("google", "Google", "Gemini 系列", "GOOGLE_API_KEY"),
    ("deepseek", "DeepSeek", "DeepSeek 系列", "DEEPSEEK_API_KEY"),
    ("ollama", "本地模型", "LLaMA, Qwen 等", "无需 API Key"),
]

print(f"{'Provider':<15} {'厂商':<10} {'支持模型':<20} {'环境变量'}")
print("-" * 70)
for provider, company, models, env in providers:
    print(f"{provider:<15} {company:<10} {models:<20} {env}")

# ============================================================
# 【补充】为什么推荐 init_chat_model
# ============================================================
print("\n" + "=" * 50)
print("为什么推荐 init_chat_model？")
print("=" * 50)
print("""
1. 厂商无关
   - 切换模型只需改两个参数
   - 不需要改业务代码

2. 配置统一
   - temperature, max_tokens 等参数完全一致
   - 便于统一管理

3. 未来可扩展
   - 添加新厂商只需配置
   - 不用改代码

4. 类型安全
   - IDE 自动补全更准确
   - 静态检查更严格
""")
