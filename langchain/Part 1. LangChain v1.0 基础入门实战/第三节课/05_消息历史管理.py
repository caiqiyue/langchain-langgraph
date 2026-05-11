# -*- coding: utf-8 -*-
"""
【案例 5】消息历史管理
==========================================

本案例展示如何管理对话历史
避免 token 超出限制

要点：
1. trim_messages 修剪消息
2. 保留重要消息的策略
3. 滑动窗口模式
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
print("案例 5: 消息历史管理")
print("=" * 50)

from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage
)
from langchain_core.messages import trim_messages

# ============================================================
# 1. trim_messages 修剪消息
# ============================================================
print("\n1. trim_messages 修剪消息")
print("-" * 30)

messages = [
    SystemMessage(content="你是一个有帮助的助手。"),
    HumanMessage(content="你好！"),
    AIMessage(content="你好！有什么可以帮助你的吗？"),
    HumanMessage(content="我想学习 Python"),
    AIMessage(content="Python 是一种高级编程语言，适合初学者学习...（很长的回复）"),
    HumanMessage(content="谢谢！"),
]

print(f"原始消息数量: {len(messages)}")

# 修剪消息
trimmed = trim_messages(
    messages,
    max_tokens=50,
    strategy="last",  # 从头保留还是从尾？"last" = 保留最近
    include_system=True,  # 是否保留 system message
)

print(f"修剪后消息数量: {len(trimmed)}")
print("\n修剪后的消息:")
for msg in trimmed:
    role = msg.__class__.__name__.replace("Message", "")
    preview = msg.content[:20] + "..." if len(msg.content) > 20 else msg.content
    print(f"  [{role}]: {preview}")

# ============================================================
# 2. 策略对比
# ============================================================
print("\n2. 消息管理策略对比")
print("-" * 30)

print("""
| 策略           | 说明                       | 适用场景        |
|---------------|--------------------------|---------------|
| 全部保留       | 保留所有消息               | 短对话        |
| 固定窗口       | 只保留最近 N 条             | 一般场景      |
| 摘要 + 滑动窗口 | 保留摘要 + 最近 N 条        | 长对话        |
| 重要性筛选     | 保留重要的消息              | 复杂场景      |

【为什么需要管理历史？】
1. LLM 有上下文窗口限制
2. API 按 token 计费
3. 太多历史会让模型分心
""")

# ============================================================
# 【补充】token 估算
# ============================================================
print("\n" + "=" * 50)
print("Token 估算规则")
print("=" * 50)
print("""
Token 是 LLM 处理文本的最小单位：

英文：
- 1 token ≈ 4 个字符
- 1 token ≈ 0.75 个单词

中文：
- 1 token ≈ 1-2 个汉字（取决于复杂度）

示例：
"Hello, world!" → 约 6 tokens
"你好世界" → 约 4 tokens
"Python 是一门高级编程语言" → 约 10 tokens
""")
