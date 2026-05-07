# -*- coding: utf-8 -*-
"""
【案例 10】批处理与并发控制
==========================================

本案例展示 LangChain 的批处理功能
用于一次性处理多个请求

要点：
1. batch() 批量调用
2. batch_as_completed() 逐个返回
3. 并发控制
"""

import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 10: 批处理与并发控制")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnableConfig

model = ChatTongyi(model="qwen3-max", temperature=0.7)

questions = [
    "什么是 Python？",
    "什么是 JavaScript？",
    "什么是 Rust？",
    "什么是 Go？",
    "什么是 Java？"
]

# ============================================================
# 1. batch() 批量调用
# ============================================================
print("\n1. batch() 批量调用")
print("-" * 30)

print(f"准备处理 {len(questions)} 个问题...")

start = time.time()
responses = model.batch(questions)
end = time.time()

print(f"总耗时: {end - start:.2f} 秒")
print(f"\n结果:")
for i, resp in enumerate(responses):
    preview = resp.content[:40] + "..." if len(resp.content) > 40 else resp.content
    print(f"  {i+1}. {preview}")

# ============================================================
# 2. batch_as_completed() 逐个返回
# ============================================================
print("\n2. batch_as_completed() 逐个返回")
print("-" * 30)

print("先完成先返回:")
for future in model.batch_as_completed(questions):
    index, response = future
    preview = response.content[:30] + "..." if len(response.content) > 30 else response.content
    print(f"  [完成 {index}] {preview}")

# ============================================================
# 3. 并发控制
# ============================================================
print("\n3. 并发控制")
print("-" * 30)

"""
【并发控制的作用】
- 避免超出 API 速率限制
- 避免客户端资源耗尽
- 配合服务端的限流策略
"""

import asyncio

async def async_batch_with_control():
    config = RunnableConfig(
        max_concurrency=2,     # 最多 2 个并发
        timeout=30.0,          # 单任务超时
        metadata={"task": "batch_demo"}
    )

    print(f"并发数限制: 2")
    start = time.time()
    responses = await model.abatch(questions, config=config)
    end = time.time()

    print(f"耗时: {end - start:.2f} 秒")
    return responses

asyncio.run(async_batch_with_control())

# ============================================================
# 【补充】batch 原理
# ============================================================
print("\n" + "=" * 50)
print("batch 原理")
print("=" * 50)
print("""
【batch 的实现】

LangChain 的 batch 不是调用模型提供商的批量 API
（虽然有些提供商有批量 API）

而是：
1. 收集所有输入
2. 使用线程池/异步并发调用
3. 收集所有结果

【并发控制原理】

max_concurrency = 2 意味着：
- 同时最多只有 2 个任务在执行
- 第 3 个任务要等前 2 个中有一个完成

示意图：
Task1 ────────────────────────────────>
Task2 ─────────────────>
Task3 ───────（等待）──────>

【什么时候适合高并发？】
- I/O 密集型：API 调用（等待网络响应）
- CPU 密集型：不适合（单核占满时是竞争）

【什么时候不适合高并发？】
- 本地模型推理（GPU/CPU 密集型）
- 资源有限的服务器
""")
