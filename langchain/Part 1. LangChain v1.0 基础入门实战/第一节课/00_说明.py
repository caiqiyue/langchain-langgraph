# -*- coding: utf-8 -*-
"""
第一阶段：LangChain 框架介绍 - 代码案例索引
==========================================

本文件夹包含 LangChain 框架介绍的所有代码案例

文件列表：
01_模型初始化.py     - 通义千问模型初始化
02_init_chat_model.py - init_chat_model 统一接口
03_LCEL基础管道.py    - LCEL 管道组合基础
04_Runnable四大方法.py - Runnable 四大方法
05_工具定义.py       - @tool 装饰器
06_记忆模块.py       - Memory 记忆模块
07_消息类型.py       - 消息类型详解
08_Prompt模板.py     - Prompt 模板详解
09_流式输出.py       - 流式输出 Streaming
10_批处理.py         - 批处理与并发控制

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "第一阶段_代码案例/01_模型初始化.py"

配置：
    API_KEY = 从环境变量 DASHSCOPE_API_KEY 读取
    BASE_URL = https://dashscope.aliyuncs.com/compatible-mode/v1
    模型 = qwen3-max
"""

print("=" * 50)
print("第一阶段：LangChain 框架介绍")
print("=" * 50)
print("""
本阶段代码案例列表：

01_模型初始化.py     - 通义千问模型初始化
02_init_chat_model.py - init_chat_model 统一接口
03_LCEL基础管道.py    - LCEL 管道组合基础
04_Runnable四大方法.py - Runnable 四大方法
05_工具定义.py       - @tool 装饰器
06_记忆模块.py       - Memory 记忆模块
07_消息类型.py       - 消息类型详解
08_Prompt模板.py     - Prompt 模板详解
09_流式输出.py       - 流式输出 Streaming
10_批处理.py         - 批处理与并发控制

运行示例：
    python "第一阶段_代码案例/01_模型初始化.py"
""")
