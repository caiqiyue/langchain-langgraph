# -*- coding: utf-8 -*-
"""
【案例 6】模块化设计原则
==========================================

本案例介绍软件工程的 SOLID 原则
理解 LangChain 模块化设计背后的思想

要点：
1. SOLID 原则简介
2. 依赖倒置原则
3. 实际应用
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 50)
print("案例 6: 模块化设计原则")
print("=" * 50)

# ============================================================
# 1. SOLID 原则
# ============================================================
print("\n1. SOLID 设计原则")
print("-" * 30)
print("""
SOLID 是软件工程的设计原则：

S - 单一职责原则 (SRP)
  每个模块只做一件事

O - 开闭原则 (OCP)
  对扩展开放，对修改封闭

L - 里氏替换原则 (LSP)
  子类可以替换父类

I - 接口隔离原则 (ISP)
  多个专用接口优于一个通用接口

D - 依赖倒置原则 (DIP)
  高层模块不依赖低层模块，而是依赖抽象
""")

# ============================================================
# 2. 依赖倒置示例
# ============================================================
print("\n2. 依赖倒置原则 (DIP)")
print("-" * 30)

print("""
【不好的设计】紧耦合

def process_with_openai(text):
    model = ChatTongyi(model="qwen3-max")  # 直接依赖具体实现
    return model.invoke(text)

问题：想换 Claude 就要改代码

【好的设计】依赖倒置

def process_with_model(text, model: ChatModel):
    return model.invoke(text)  # 依赖抽象（ChatModel 协议）

调用：
tongyi = ChatTongyi(model="qwen3-max")
claude = ChatAnthropic(model="claude-3-5-sonnet")

result1 = process_with_model("Hello", tongyi)  # 用通义千问
result2 = process_with_model("Hello", claude)   # 换 Claude 也不用改函数
""")

from typing import Protocol

# 定义协议（抽象）
class LLMModel(Protocol):
    def invoke(self, text: str):
        ...

# 使用协议而非具体类
def process_text(text: str, model: LLMModel) -> str:
    """这个函数可以接受任何实现 LLMModel 协议的对象"""
    return model.invoke(text)

print("✅ 依赖抽象而非具体 - 切换模型不需要改业务代码")

# ============================================================
# 3. LangChain 的模块化设计
# ============================================================
print("\n3. LangChain 的模块化设计")
print("-" * 30)

print("""
LangChain 的模块化设计遵循 SOLID：

1. 单一职责
   - langchain-core: 核心抽象
   - langchain: 主入口
   - langchain-community: 第三方集成

2. 依赖倒置
   - 业务代码依赖 Runnable 抽象
   - 不依赖具体厂商实现

3. 接口隔离
   - Runnable 有多个子接口
   - Prompt 有 PromptTemplate、ChatPromptTemplate
""")

# ============================================================
# 【补充】实际项目中的包选择
# ============================================================
print("\n" + "=" * 50)
print("实际项目的包选择策略")
print("=" * 50)

scenarios = [
    ("初创项目，快速验证", "langchain + langchain-community"),
    ("企业级，多厂商支持", "langchain + 多个厂商包"),
    ("本地部署，注重隐私", "langchain + langchain-ollama"),
    ("处理各种文档格式", "+ langchain-community"),
    ("维护旧项目", "langchain + langchain-classic"),
]

print(f"{'场景':<30} {'推荐包组合'}")
print("-" * 60)
for scenario, packages in scenarios:
    print(f"{scenario:<30} {packages}")
