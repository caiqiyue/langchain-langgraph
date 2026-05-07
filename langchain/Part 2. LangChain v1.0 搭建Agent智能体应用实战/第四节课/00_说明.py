# -*- coding: utf-8 -*-
"""
第四阶段：Agent与LangChain交互架构 - 代码案例索引
==================================================

本文件夹包含 create_agent 核心参数配置的代码案例

文件列表：
00_说明.py                  - 本索引文件
01_create_agent九大参数.py   - create_agent 完整参数解析
02_RecursionLimit控制.py    - 限制循环次数
03_流式输出观察.py          - 流式模式输出

create_agent 九大核心参数：
1. model           - 推理引擎（必填）
2. tools           - 工具列表（必填）
3. system_prompt   - 系统提示词
4. middleware      - 中间件列表
5. checkpointer    - 短期记忆
6. store           - 长期记忆
7. state_schema    - 自定义状态
8. context_schema  - 动态上下文
9. response_format - 结构化输出

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第四节课/01_create_agent九大参数.py"
"""

print("=" * 60)
print("第四阶段：Agent与LangChain交互架构")
print("=" * 60)
print("""
create_agent 九大核心参数：

必填参数：
1. model     - 推理引擎（大模型）
2. tools     - 工具列表

可选参数：
3. system_prompt   - 系统提示词（Agent 行为准则）
4. middleware      - 中间件列表（功能扩展）
5. checkpointer    - 短期记忆（会话级）
6. store           - 长期记忆（跨会话）
7. state_schema    - 自定义状态
8. context_schema  - 动态上下文
9. response_format - 结构化输出

代码案例：
01_create_agent九大参数.py - 完整参数解析
02_RecursionLimit控制.py  - 限制循环次数
03_流式输出观察.py        - 流式输出模式
""")