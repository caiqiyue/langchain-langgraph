# -*- coding: utf-8 -*-
"""
【案例1】LangChain Chain构建示例
============================================

本案例展示如何使用LangChain表达式语言(LCEL)构建一个简单的翻译Chain。

要点：
1. 使用ChatPromptTemplate构建提示模板
2. 使用|操作符连接prompt和llm
3. 通过invoke方法调用chain
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
import getpass

# 设置OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# ============================================================
# 2. 构建Chain
# ============================================================
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

# 构建提示模板
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
        ("human", "{input}"),
    ]
)

# 使用|操作符连接构建Chain
chain = prompt | llm

# ============================================================
# 3. 调用Chain
# ============================================================
result = chain.invoke(
    {
        "input_language": "English",
        "output_language": "Chinese",
        "input": "I love programming.",
    }
)

print("翻译结果:", result.content)
