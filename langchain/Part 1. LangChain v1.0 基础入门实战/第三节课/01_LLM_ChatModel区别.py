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


"""

一、先理解：LLM 和 ChatModel 到底是什么
1. LLM（传统语言模型）

最早的大模型：

GPT-2
GPT-3
text-davinci-003
LLaMA 早期版本

它们本质上只有：

输入一段文本 → 输出一段文本

所以：

prompt = "翻译：你好"

result = llm.invoke(prompt)

本质：

字符串 -> 字符串

即：

str -> str
2. ChatModel（聊天模型）

后来 OpenAI 提出了 ChatML 格式。

模型不再只接收文本，而是：

[
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."}
]

模型开始理解：

system
user
assistant

于是：

messages -> message

即：

List[Message] -> AIMessage

例如：

messages = [
    {"role": "system", "content": "你是翻译助手"},
    {"role": "user", "content": "你好"}
]

模型就能知道：

system 是系统规则
user 是用户提问

这比纯字符串强太多。

二、为什么 ChatModel 比 LLM 更高级

这是核心。

1. ChatModel 有“角色”

传统 LLM：

你是翻译助手。
请翻译：
你好

其实模型根本不知道：

哪句是系统规则
哪句是用户输入

全靠 Prompt Engineering。

而 ChatModel：

[
  SystemMessage(...),
  HumanMessage(...)
]

模型天然知道：

role	含义
system	系统指令
user	用户
assistant	AI

因此：

对话更稳定
Prompt 更清晰
更容易控制
2. ChatModel 天然支持多轮对话

LLM 时代：

你必须自己拼接历史：

prompt = ""
用户：你好
AI：你好，请问需要什么帮助？
用户：今天天气怎么样
""

非常麻烦。

ChatModel：

messages = [
    HumanMessage("你好"),
    AIMessage("你好"),
    HumanMessage("今天天气")
]

模型天然理解上下文。

3. ChatModel 支持工具调用（最重要）

现代 AI Agent：

function calling
tool calling
MCP
ReAct
LangGraph

全部建立在：

message-based protocol

上。

因为：

AI 不只是输出文本。

还可能输出：

{
  "tool": "search_weather",
  "args": {
      "city": "上海"
  }
}

这已经不是：

str -> str

了。

因此：

传统 LLM 抽象不够用了。

4. ChatModel 支持多模态

现在 content 已经不只是文本。

例如：

{
  "role": "user",
  "content": [
      {"type": "text", "text": "这是什么"},
      {"type": "image_url", "image_url": "..."}
  ]
}

因此：

ChatModel 实际上已经变成：

消息协议

而不是：

文本生成器
三、为什么 LangChain 还保留 LLM

因为历史兼容。

很多老模型：

只有 completion 接口
不支持 chat

例如：

text-davinci-003
某些 HuggingFace 模型

因此 LangChain 必须兼容：

from langchain.llms import OpenAI

但现代开发：

几乎全部使用：

ChatModel

包括：

GPT-4
Claude
Gemini
Qwen
DeepSeek

全部都是 ChatModel。

四、你代码里的核心知识点

这里：

response = model.invoke(messages)

重点是：

invoke 是统一调用接口

LangChain 统一规定：

.invoke()

无论：

LLM
ChatModel
Runnable
Chain
Agent

全部都能：

.invoke()

这叫：

Runnable Interface

LangChain 最核心设计。

五、response 为什么不是字符串

这里：

type(response)

输出其实是：

AIMessage

不是：

str

因为：

ChatModel 输出的是“消息对象”。

里面除了 content：

还有：

response.content
response.tool_calls
response.response_metadata
response.id

例如：

AIMessage(
    content="Hello world",
    tool_calls=[...]
)

这就是：

为什么现代 Agent 必须基于 ChatModel。

六、现代 LangChain 的真实情况

实际上：

ChatModel 已经成为主流

现在：

LLM ≈ 历史兼容层
ChatModel ≈ 真正现代接口

你甚至会发现：

很多所谓的 “LLM”

底层其实也是：

chat/completions

只是 LangChain 做了一层包装。

七、你可以这样理解
LLM

像：

单次文本补全机器
ChatModel

像：

会话协议 + 多模态 + 工具调用 + Agent 操作系统
八、现在最重要的认知

现代 AI 开发：

核心已经不是：

文本生成

而是：

消息流（Message Flow）

所以：

LangGraph
Agent
Tool Calling
MCP

本质都是：

消息状态机

而 ChatModel 就是这个体系的基础。

九、最后给你一个非常重要的总结
LLM 时代
Prompt -> Text
ChatModel 时代
Messages -> AIMessage
Agent 时代
State(Messages) -> Tool Calls -> New Messages -> Final Answer

这就是：

为什么 LangChain 后来整个架构：

Runnable
Message
ChatModel
Agent
LangGraph

全部围绕：

Message-Based Architecture

来设计。
"""