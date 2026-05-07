# -*- coding: utf-8 -*-
"""
【案例 3】模型参数详解
==========================================

本案例深入讲解模型的关键参数

要点：
1. temperature 温度参数
2. max_tokens 最大生成数
3. 重试机制
4. 速率限制
"""

import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 3: 模型参数详解")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi

# ============================================================
# 1. temperature 温度参数
# ============================================================
print("\n1. temperature 温度参数")
print("-" * 30)

print("""
temperature 控制输出的随机性：

- temperature = 0.0：几乎确定输出，适合翻译、代码等需要精确的场景
- temperature = 0.3~0.7：平衡模式，适合一般对话
- temperature = 0.7~1.0：创意模式，适合写作、头脑风暴
- temperature > 1.0：不推荐，过度随机

数学原理：
- LLM 输出是概率分布 P(token)
- temperature 重新加权：P'(token) ∝ P(token)^(1/temperature)
- temperature → 0 时，趋向于 one-hot（最高概率）
- temperature → ∞ 时，趋向于均匀分布
""")

# 不同 temperature 的效果
model = ChatTongyi(model="qwen3-max", temperature=0.0)
response = model.invoke("给我一个 1-10 之间的随机数")
print(f"temperature=0.0: {response.content}")

model = ChatTongyi(model="qwen3-max", temperature=1.0)
response = model.invoke("给我一个 1-10 之间的随机数")
print(f"temperature=1.0: {response.content}")

# ============================================================
# 2. max_tokens 最大生成数
# ============================================================
print("\n2. max_tokens 最大生成数")
print("-" * 30)

print("""
max_tokens 控制单次回复的最大长度：

- 设置太小：回复可能被截断
- 设置太大：浪费 token，增加成本
- 实际是"最大"限制，不是精确控制

注意：LLM 是按 token 计费的
估算规则（英文）：
- 1 token ≈ 4 个字符
- 1 token ≈ 0.75 个单词
""")

model = ChatTongyi(model="qwen3-max", max_tokens=10)
response = model.invoke("写一篇 500 字的文章")
print(f"max_tokens=10 的回复: {response.content}")

model = ChatTongyi(model="qwen3-max", max_tokens=500)
response = model.invoke("写一篇 500 字的文章")
print(f"max_tokens=500 的回复长度: {len(response.content)} 字符")

# ============================================================
# 3. 重试机制
# ============================================================
print("\n3. 重试机制")
print("-" * 30)

print("""
.with_retry() 为模型调用添加重试策略：

参数：
- stop_after_attempt: 最多重试次数
- wait_exponential_jitter: 指数退避 + 随机抖动

指数退避：1s → 2s → 4s → 8s
抖动：避免多个客户端同时重试
""")

model = ChatTongyi(model="qwen3-max", temperature=0.7)
model_with_retry = model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

print("重试机制配置完成")
print(f"原始模型: {type(model)}")
print(f"带重试的模型: {type(model_with_retry)}")

# ============================================================
# 【补充】top_p（核采样）
# ============================================================
print("\n" + "=" * 50)
print("补充：top_p（核采样）")
print("=" * 50)
print("""
top_p 是 temperature 的替代方案：

- 按概率降序排列 tokens
- 从高到低累加概率
- 只保留累加概率达到 top_p 的 tokens
- 通常 top_p = 0.9

注意：通常只调 temperature 或 top_p，不同时调
""")
