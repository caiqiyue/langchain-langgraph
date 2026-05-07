# -*- coding: utf-8 -*-
"""
第三阶段：核心概念与组件 - 代码案例索引
==========================================

本文件夹包含 LangChain 核心概念与组件的所有代码案例

文件列表：
01_LLM_ChatModel区别.py    - LLM 和 ChatModel 的区别
02_init_chat_model.py      - init_chat_model 统一接口
03_模型参数详解.py         - temperature、max_tokens 等参数
04_消息类型详解.py         - 消息类型系统
05_消息历史管理.py         - 消息历史修剪
06_PromptTemplate.py        - PromptTemplate 详解
07_ChatPromptTemplate.py    - ChatPromptTemplate 消息模板
08_Content_Blocks.py        - 标准化内容块
09_结构化输出.py           - Pydantic + with_structured_output
10_JsonOutputParser.py      - JsonOutputParser

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "第三阶段_代码案例/01_LLM_ChatModel区别.py"

配置：
    API_KEY = 从环境变量 DASHSCOPE_API_KEY 读取
    BASE_URL = https://dashscope.aliyuncs.com/compatible-mode/v1
    模型 = qwen3-max
"""

print("=" * 50)
print("第三阶段：核心概念与组件")
print("=" * 50)
print("""
本阶段代码案例列表：

01_LLM_ChatModel区别.py    - LLM 和 ChatModel 的区别
02_init_chat_model.py      - init_chat_model 统一接口
03_模型参数详解.py         - temperature、max_tokens 等参数
04_消息类型详解.py         - 消息类型系统
05_消息历史管理.py         - 消息历史修剪
06_PromptTemplate.py        - PromptTemplate 详解
07_ChatPromptTemplate.py    - ChatPromptTemplate 消息模板
08_Content_Blocks.py        - 标准化内容块
09_结构化输出.py           - Pydantic + with_structured_output
10_JsonOutputParser.py      - JsonOutputParser
""")
