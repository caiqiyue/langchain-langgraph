# -*- coding: utf-8 -*-
"""
第四课：LangGraph 实现自治循环代理（ReAct）及事件流的应用 - 代码案例索引
====================================================================

本文件夹包含LangGraph实现自治循环代理（ReAct）及事件流的应用的所有代码案例

文件列表：
01_ReAct构建原理.py              - LangGraph中ReAct的构建原理
02_天气查询工具定义.py            - 天气查询工具定义
03_数据库操作工具定义.py          - 数据库操作工具定义
04_创建ReAct代理.py              - 使用create_react_agent创建ReAct代理
05_流输出模式_values.py          - Stream模式之values
06_流输出模式_updates.py         - Stream模式之updates
07_流输出模式_debug.py           - Stream模式之debug
08_异步流输出astream.py          - 异步流输出astream
09_事件流astream_events.py       - 使用astream_events获取事件流
10_事件过滤与处理.py              - 事件过滤与自定义处理

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "4. LangGraph 实现自治循环代理（ReAct）及事件流的应用/第一节课/01_ReAct构建原理.py"

配置：
    API_KEY = 从环境变量 OPENAI_API_KEY 读取
    LANGCHAIN_API_KEY = 从环境变量 LANGCHAIN_API_KEY 读取（可选，用于追踪）
    模型 = gpt-4o
"""

print("=" * 50)
print("第四课：LangGraph 实现自治循环代理（ReAct）及事件流的应用")
print("=" * 50)
print("""
本课程序件列表：

01_ReAct构建原理.py              - LangGraph中ReAct的构建原理
02_天气查询工具定义.py            - 天气查询工具定义
03_数据库操作工具定义.py          - 数据库操作工具定义
04_创建ReAct代理.py              - 使用create_react_agent创建ReAct代理
05_流输出模式_values.py          - Stream模式之values
06_流输出模式_updates.py         - Stream模式之updates
07_流输出模式_debug.py           - Stream模式之debug
08_异步流输出astream.py          - 异步流输出astream
09_事件流astream_events.py       - 使用astream_events获取事件流
10_事件过滤与处理.py              - 事件过滤与自定义处理

运行示例：
    python "4. LangGraph 实现自治循环代理（ReAct）及事件流的应用/第一节课/01_ReAct构建原理.py"
""")