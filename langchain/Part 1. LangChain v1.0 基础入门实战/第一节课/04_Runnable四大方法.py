# -*- coding: utf-8 -*-
"""
【案例 4】Runnable 四大方法
==========================================

本案例展示 Runnable 接口的四大核心方法
任何 LangChain 组件都实现了 Runnable 接口

要点：
1. invoke() - 同步调用
2. batch() - 批量调用
3. stream() - 流式调用
4. ainvoke() - 异步调用
"""

import os
import time
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
print("案例 4: Runnable 四大方法")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建链
prompt = ChatPromptTemplate.from_template("用一句话形容：{topic}")
model = ChatTongyi(model="qwen3-max", temperature=0.7)
parser = StrOutputParser()
chain = prompt | model | parser

# ============================================================
# 1. invoke() - 同步调用
# ============================================================
print("\n" + "-" * 30)
print("1. invoke() - 同步调用")
print("-" * 30)

result = chain.invoke({"topic": "大海"})
print(f"输入: {{'topic': '大海'}}")
print(f"输出: {result}")

# ============================================================
# 2. batch() - 批量调用
# ============================================================
print("\n" + "-" * 30)
print("2. batch() - 批量调用")
print("-" * 30)

inputs = [
    {"topic": "太阳"},
    {"topic": "月亮"},
    {"topic": "星星"}
]

start = time.time()
responses = chain.batch(inputs)
end = time.time()

print(f"输入列表: {[inp['topic'] for inp in inputs]}")
print(f"耗时: {end - start:.2f} 秒")
print("输出列表:")
for i, resp in enumerate(responses):
    print(f"  {i+1}. {resp}")

# ============================================================
# 3. stream() - 流式调用
# ============================================================
print("\n" + "-" * 30)
print("3. stream() - 流式调用（打字机效果）")
print("-" * 30)

print("流式输出: ", end="", flush=True)
full = ""
for chunk in chain.stream({"topic": "春天"}):
    if chunk:
        print(chunk, end="", flush=True)
        full += chunk
print()

# ============================================================
# 4. ainvoke() - 异步调用
# ============================================================
print("\n" + "-" * 30)
print("4. ainvoke() - 异步调用")
print("-" * 30)

import asyncio

async def async_demo():
    result = await chain.ainvoke({"topic": "异步测试"})
    return result

result = asyncio.run(async_demo())
print(f"异步调用结果: {result}")

# ============================================================
# 【补充】方法对比
# ============================================================
print("\n" + "=" * 50)
print("四大方法对比")
print("=" * 50)
print("""
| 方法      | 特性               | 适用场景           |
|-----------|-------------------|-------------------|
| invoke()  | 同步，阻塞，单输入  | 最常用            |
| batch()   | 同步，批量，多输入  | 并行处理多个请求   |
| stream()  | 同步，流式，迭代器  | 打字机效果        |
| ainvoke() | 异步，非阻塞，单输入 | FastAPI 等异步框架 |
""")
