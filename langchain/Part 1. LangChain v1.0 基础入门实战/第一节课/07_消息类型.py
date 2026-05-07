# -*- coding: utf-8 -*-
"""
【案例 7】消息类型详解
==========================================

本案例展示 LangChain 的消息类型系统
消息是构建对话的基础

要点：
1. 各种消息类型的创建
2. 消息角色的作用
3. 消息列表的构建
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 7: 消息类型详解")
print("=" * 50)

from langchain_core.messages import (
    HumanMessage,      # 用户消息
    AIMessage,          # AI 助手消息
    SystemMessage,      # 系统提示
    ToolMessage,        # 工具调用结果
    BaseMessage         # 基类
)

# ============================================================
# 1. 创建各种消息
# ============================================================
print("\n1. 创建各种消息")
print("-" * 30)

system_msg = SystemMessage(content="你是一个专业的Python导师。")
human_msg = HumanMessage(content="什么是装饰器？")
ai_msg = AIMessage(content="装饰器是 Python 中修改函数行为的语法糖。")

print(f"SystemMessage: {system_msg.content[:30]}...")
print(f"HumanMessage: {human_msg.content}")
print(f"AIMessage: {ai_msg.content}")

# ============================================================
# 2. 消息属性
# ============================================================
print("\n2. 消息属性")
print("-" * 30)

print(f"\nAIMessage 属性:")
print(f"  content: {ai_msg.content}")
print(f"  type: {ai_msg.type}")
print(f"  id: {ai_msg.id}")
print(f"  additional_kwargs: {ai_msg.additional_kwargs}")

# ============================================================
# 3. 消息列表构建
# ============================================================
print("\n3. 消息列表构建")
print("-" * 30)

messages = [
    SystemMessage(content="你是一个专业的Python导师。"),
    HumanMessage(content="什么是装饰器？"),
    AIMessage(content="装饰器是 Python 中修改函数行为的语法糖。"),
    HumanMessage(content="给我一个例子"),
    AIMessage(content="""下面是一个简单的装饰器例子：

```python
def my_decorator(func):
    def wrapper():
        print("开始执行")
        func()
        print("执行结束")
    return wrapper

@my_decorator
def say_hello():
    print("你好！")

say_hello()
```
输出：
开始执行
你好！
执行结束
""")
]

print(f"消息列表长度: {len(messages)}")
for i, msg in enumerate(messages):
    role = msg.__class__.__name__.replace("Message", "")
    preview = msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
    print(f"  {i+1}. [{role}]: {preview}")

# ============================================================
# 4. 调用模型
# ============================================================
print("\n4. 调用模型")
print("-" * 30)

from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(model="qwen3-max", temperature=0.7)

# 使用消息列表调用
response = model.invoke(messages)
print(f"\n用户: 给我一个装饰器的例子")
print(f"AI: {response.content[:100]}...")

# ============================================================
# 【补充】消息角色详解
# ============================================================
print("\n" + "=" * 50)
print("消息角色优先级")
print("=" * 50)
print("""
| 角色        | 优先级 | 作用                          |
|-------------|--------|-------------------------------|
| system      | 最高   | 设定模型身份、行为规则          |
| developer   | 次高   | 开发者提示（OpenAI 新增）      |
| user        | 高     | 用户当前输入                   |
| assistant   | 中     | AI 历史回复                   |
| tool        | 低     | 工具调用结果                   |

【为什么 system 优先级最高？】
因为模型会首先参考 system 消息来确定自己的行为方式。
无论用户说什么，system 的设定都应该被遵守。
""")
