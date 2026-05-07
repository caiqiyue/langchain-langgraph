# -*- coding: utf-8 -*-
"""
【案例 2】LangChain 表达式语言（LCEL）基础
============================================

本案例展示 LangChain 表达式语言的基本用法，为理解 LangGraph 打基础

要点：
1. LCEL 管道运算符 | 的使用
2. Runnable 接口的 invoke 方法
3. DAG（有向无环图）概念
"""

# ============================================================
# 1. LCEL 基础用法
# ============================================================
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 初始化模型
llm = ChatOpenAI(model="gpt-4o")

# 创建 Prompt 模板
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
        ("human", "{input}"),
    ]
)

# 使用 LCEL 管道符组合组件
chain = prompt | llm

# ============================================================
# 2. 调用链
# ============================================================
print("=" * 50)
print("案例 2: LCEL 管道组合")
print("=" * 50)

response = chain.invoke(
    {
        "input_language": "English",
        "output_language": "Chinese",
        "input": "I love programming.",
    }
)

print(f"输入: I love programming.")
print(f"输出: {response.content}")

# ============================================================
# 3. LCEL 核心概念
# ============================================================
print("\n" + "=" * 50)
print("LCEL 核心概念说明")
print("=" * 50)
print("""
LCEL（LangChain Expression Language）特点：
1. 使用 | 管道运算符组合 Runnable 组件
2. 构建 DAG（有向无环图）
3. 支持 invoke、stream、batch 等调用方式

LangGraph 的出现就是为了解决 LCEL 无法处理循环的问题
""")