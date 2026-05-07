# -*- coding: utf-8 -*-
"""
【案例 8】Prompt 模板详解
==========================================

本案例展示 LangChain 的 Prompt 模板系统
Prompt 是与 LLM 交互的核心

要点：
1. PromptTemplate - 简单模板
2. ChatPromptTemplate - 消息模板
3. partial_variables - 预填充变量
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 8: Prompt 模板详解")
print("=" * 50)

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# ============================================================
# 1. PromptTemplate - 简单模板
# ============================================================
print("\n1. PromptTemplate - 简单模板")
print("-" * 30)

# from_template 方式
template1 = PromptTemplate.from_template(
    "为{product}设计一个创意广告语，要求：{style}"
)
formatted1 = template1.format(product="智能手表", style="年轻时尚")
print(f"模板1: {formatted1}")

# 直接构造方式
template2 = PromptTemplate(
    input_variables=["name", "hobby"],
    template="{name}最喜欢的爱好是{hobby}。"
)
formatted2 = template2.format(name="张三", hobby="游泳")
print(f"模板2: {formatted2}")

# ============================================================
# 2. ChatPromptTemplate - 消息模板
# ============================================================
print("\n2. ChatPromptTemplate - 消息模板")
print("-" * 30)

chat_template = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的{profession}。
请用专业但易懂的语言回答问题。"""),
    ("human", "{user_question}")
])

# format_messages 返回消息列表
messages = chat_template.format_messages(
    profession="Python导师",
    user_question="什么是生成器？"
)

print(f"生成了 {len(messages)} 条消息:")
for i, msg in enumerate(messages):
    role = msg.type if hasattr(msg, 'type') else "unknown"
    preview = msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
    print(f"  {i+1}. [{role}]: {preview}")

# ============================================================
# 3. partial_variables - 预填充变量
# ============================================================
print("\n3. partial_variables - 预填充变量")
print("-" * 30)

"""
【应用场景】
系统提示词通常是不变的，只有用户输入是变的。
使用 partial_variables 可以预填充系统设定。
"""

system_template = """你是一个专业的{department}客服。
请遵循以下规则：
1. 礼貌、耐心地回答
2. 如无法解决，寻求上级帮助
3. 保持专业形象"""

template = PromptTemplate(
    input_variables=["user_question", "department"],
    template=system_template + "\n\n客户问题：{user_question}",
    partial_variables={
        "department": "技术支持"  # 预填充，调用时不需要提供
    }
)

# 使用时只需提供 user_question
formatted = template.format(user_question="密码忘记了怎么办？")
print(f"预填充后的提示:")
print(formatted)

# ============================================================
# 4. Few-shot 示例
# ============================================================
print("\n4. Few-shot 示例")
print("-" * 30)

few_shot_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译专家，将中文翻译成英文。"),
    ("human", "你好"),
    ("ai", "Hello"),
    ("human", "谢谢"),
    ("ai", "Thank you"),
    ("human", "{user_input}"),
])

messages = few_shot_template.format_messages(user_input="再见")
print(f"Few-shot 翻译示例:")
for msg in messages:
    role = msg.type if hasattr(msg, 'type') else msg.__class__.__name__
    print(f"  [{role}]: {msg.content}")

# ============================================================
# 【补充】模板变量语法
# ============================================================
print("\n" + "=" * 50)
print("PromptTemplate 变量语法")
print("=" * 50)
print("""
| 语法                  | 说明                      |
|-----------------------|--------------------------|
| {variable}            | 标准变量替换             |
| partial_variables     | 预填充变量（可选）        |

【注意】
- 变量名必须匹配 input_variables
- 预填充的变量在 format() 时可以省略
- 支持嵌套模板（模板中使用另一个模板）
""")
