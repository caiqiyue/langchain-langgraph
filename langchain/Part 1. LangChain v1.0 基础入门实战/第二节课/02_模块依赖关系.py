# -*- coding: utf-8 -*-
"""
【案例 2】LangChain 模块依赖关系
==========================================

本案例展示 LangChain 1.0 的模块依赖关系
理解模块化设计

要点：
1. langchain-core 是底座
2. 各包之间的依赖关系
3. 如何选择安装哪些包
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 50)
print("案例 2: LangChain 模块依赖关系")
print("=" * 50)

# ============================================================
# 1. 模块依赖图
# ============================================================
print("\n1. LangChain 1.0 模块架构")
print("-" * 30)
print("""
                    ┌─────────────────────┐
                    │   langchain-core   │  ← 最小公共底座
                    │   (核心抽象+LCEL)   │
                    └──────────┬──────────┘
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      ▼                        ▼                        ▼
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  langchain │      │langchain-community│    │langchain-openai │
│    (主包)   │      │    (社区集成)    │      │  (OpenAI官方)   │
└─────────────┘      └─────────────────┘      └─────────────────┘
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               ▼
                    ┌─────────────────┐
                    │langchain-classic│
                    │   (旧版兼容)     │
                    └─────────────────┘
""")

# ============================================================
# 2. 各包职责
# ============================================================
print("\n2. 各包职责")
print("-" * 30)

packages = [
    ("langchain-core", "核心抽象层", "无厂商依赖"),
    ("langchain", "应用认知架构主包", "create_agent, AgentState"),
    ("langchain-community", "社区第三方集成", "文档加载器、向量存储、第三方 LLM"),
    ("langchain-openai", "OpenAI 官方集成", "ChatOpenAI, OpenAIEmbeddings"),
    ("langchain-dashscope", "通义千问集成", "ChatTongyi（我们使用这个）"),
    ("langchain-classic", "旧版本兼容", "LLMChain, AgentExecutor"),
]

print(f"{'包名':<25} {'职责':<15} {'包含内容'}")
print("-" * 70)
for pkg, role, content in packages:
    print(f"{pkg:<25} {role:<15} {content}")

# ============================================================
# 3. 实际安装选择
# ============================================================
print("\n3. 实际项目的包选择")
print("-" * 30)

scenarios = [
    ("快速验证想法", "langchain + langchain-dashscope"),
    ("企业级项目", "langchain + 多个厂商包"),
    ("本地部署", "langchain + langchain-ollama"),
    ("处理文档", "langchain + langchain-community"),
    ("维护旧项目", "langchain + langchain-classic"),
]

for scenario, packages in scenarios:
    print(f"  {scenario}: {packages}")

# ============================================================
# 【补充】版本对应关系
# ============================================================
print("\n" + "=" * 50)
print("LangChain 版本演进")
print("=" * 50)
print("""
| 版本   | Python 要求 | 主要变化                        |
|--------|------------|--------------------------------|
| v0.x   | Python 3.8+ | 单体包，LLMChain              |
| v1.0   | Python 3.10+| 模块化，create_agent + LangGraph |

升级建议：
- 新项目 → 直接用 v1.0
- 旧项目 → 逐步迁移，用 langchain-classic 过渡
""")
