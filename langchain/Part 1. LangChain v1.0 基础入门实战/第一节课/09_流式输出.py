# -*- coding: utf-8 -*-
"""
【案例 9】流式输出 Streaming
==========================================

本案例展示 LangChain 的流式输出功能
实现打字机效果，提升用户体验

要点：
1. stream() 方法的使用
2. 流式输出的原理（SSE）
3. 消息块累积
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 9: 流式输出 Streaming")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(model="qwen3-max", temperature=0.7)

# ============================================================
# 1. 基础流式调用
# ============================================================
print("\n1. 基础流式调用")
print("-" * 30)

print("AI: ", end="", flush=True)
full_response = ""

for chunk in model.stream("给我讲一个关于猫的笑话"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
        full_response += chunk.content

print("\n")  # 换行

# ============================================================
# 2. 消息块累积
# ============================================================
print("2. 消息块累积")
print("-" * 30)

print("AI: ", end="", flush=True)
accumulated = None

for chunk in model.stream("解释一下什么是量子计算"):
    # AIMessageChunk 可以通过 + 拼接
    accumulated = chunk if accumulated is None else accumulated + chunk
    print(chunk.content if chunk.content else "", end="", flush=True)

print("\n\n累积消息信息:")
print(f"  类型: {type(accumulated)}")
print(f"  内容长度: {len(accumulated.content)} 字符")
print(f"  内容块数量: {len(accumulated.content_blocks)}")

# ============================================================
# 【补充】SSE 原理
# ============================================================
print("\n" + "=" * 50)
print("Server-Sent Events (SSE) 原理")
print("=" * 50)
print("""
【问题】
HTTP 协议是请求-响应模型，一次请求只能一次响应。
但流式需要服务端分批发数据，客户端逐步显示。

【SSE 解决方案】

1. HTTP 响应头设置：
   Content-Type: text/event-stream
   Cache-Control: no-cache
   Connection: keep-alive

2. 服务端分次发送数据：
   data: {"token": "你"}\n\n
   data: {"token": "好"}\n\n
   data: {"token": "啊"}\n\n
   data: [DONE]\n\n

3. 客户端通过 EventSource 接收：
   const source = new EventSource('/stream');
   source.onmessage = (event) => {
       console.log(event.data);
   };

【LangChain 的处理】
- LangChain 封装了 SSE 协议
- stream() 返回一个生成器
- 每个 chunk 是 AIMessageChunk 对象
- chunk.content 是本次返回的文本片段
""")
