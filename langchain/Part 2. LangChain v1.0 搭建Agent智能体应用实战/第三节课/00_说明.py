# -*- coding: utf-8 -*-
"""
第三阶段：Agent 技术解剖 - 代码案例索引
==========================================

本文件夹包含 Agent 技术架构的代码案例

文件列表：
00_说明.py              - 本索引文件
01_Agent架构解析.py     - Agent 五大核心模块解析
02_思考行动观察循环.py  - 认知循环的四个阶段

Agent 技术架构五大模块：
- 感知模块 (Perception)   - 接收多模态输入
- 认知中枢 (Brain)       - 基于 LLM 进行推理决策
- 记忆系统 (Memory)      - 短期+长期记忆
- 工具生态 (Tools)       - 外部系统交互
- 执行引擎 (Action)      - 执行具体任务

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第三节课/01_Agent架构解析.py"
"""

print("=" * 60)
print("第三阶段：Agent 技术解剖")
print("=" * 60)
print("""
Agent 技术架构五大核心模块：

1. 感知模块 (Perception)   - 输入接口，接收文本/图像/语音
2. 认知中枢 (Brain)        - LLM 推理引擎，进行思考和决策
3. 记忆系统 (Memory)       - 存储历史和知识
4. 工具生态 (Tools)        - 执行外部操作
5. 执行引擎 (Action)       - 任务执行和结果反馈

代码案例：
01_Agent架构解析.py     - 五大模块的代码对应
02_思考行动观察循环.py  - 认知循环的四个阶段
""")