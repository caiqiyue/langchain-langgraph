# -*- coding: utf-8 -*-
"""
【案例 1】langchain-core 核心抽象
==========================================

本案例展示 langchain-core 包的核心抽象
langchain-core 是 LangChain 生态的基石

要点：
1. PromptTemplate 抽象
2. Message 抽象
3. OutputParser 抽象
4. Runnable 统一接口
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 1: langchain-core 核心抽象")
print("=" * 50)

# ============================================================
# 1. langchain-core 包含什么？
# ============================================================
print("\n1. langchain-core 核心内容")
print("-" * 30)
print("""
langchain-core 包含：

1. 核心抽象类
   - BaseChatModel / BaseLLM
   - BasePromptTemplate
   - BaseOutputParser
   - BaseTool

2. 数据结构
   - HumanMessage / AIMessage / SystemMessage
   - Document
   - Input / Output

3. LCEL 核心
   - Runnable 接口
   - 管道运算符 |
   - 配置传递机制
""")

# ============================================================
# 2. 验证组件类型
# ============================================================
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

print("\n2. 验证组件是否都实现了 Runnable 接口")
print("-" * 30)

components = [
    ("PromptTemplate", PromptTemplate.from_template("{text}")),
    ("ChatPromptTemplate", ChatPromptTemplate.from_messages([("human", "{text}")])),
    ("StrOutputParser", StrOutputParser()),
    ("HumanMessage", HumanMessage(content="test")),
]

for name, component in components:
    is_runnable = isinstance(component, Runnable)
    print(f"  {name}: {'✅' if is_runnable else '❌'}")

# ============================================================
# 3. 四大核心抽象
# ============================================================
print("\n3. 四大核心抽象")
print("-" * 30)

# 3.1 PromptTemplate
prompt = PromptTemplate.from_template("翻译成英文：{text}")
print(f"\n3.1 PromptTemplate:")
print(f"  类型: {type(prompt).__name__}")
print(f"  输入变量: {prompt.input_variables}")
formatted = prompt.format(text="你好")
print(f"  格式化结果: {formatted}")

# 3.2 Messages
print(f"\n3.2 Messages:")
print(f"  HumanMessage: {type(HumanMessage(content='test')).__name__}")
print(f"  AIMessage: {type(AIMessage(content='test')).__name__}")
print(f"  SystemMessage: {type(SystemMessage(content='test')).__name__}")

# 3.3 OutputParser
print(f"\n3.3 OutputParser:")
parser = StrOutputParser()
print(f"  StrOutputParser: {type(parser).__name__}")
result = parser.invoke("原始文本")
print(f"  解析结果: {result}")

# 3.4 Runnable
print(f"\n3.4 Runnable:")
print(f"  所有 LangChain 组件都实现了 Runnable 接口")
print(f"  因此可以用 | 运算符组合")

# ============================================================
# 【补充】为什么需要 langchain-core？
# ============================================================
print("\n" + "=" * 50)
print("为什么需要 langchain-core？")
print("=" * 50)
print("""
【设计思想】

想象建筑行业：
- 钢筋、水泥是"核心材料"
- 不依赖任何建筑风格
- 具体建成什么房子，是后面的事

langchain-core 就是 LangChain 的"钢筋水泥"：

1. 轻量级：无任何第三方厂商依赖
2. 定义接口：Model、Prompt、Tool、Chain 的抽象基类
3. LCEL 核心：Runnable 接口、管道运算符

这样设计的好处：
- 核心稳定：厂商包可以独立更新
- 易于扩展：添加新厂商只需实现接口
- 按需安装：用哪个装哪个
""")
