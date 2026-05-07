# -*- coding: utf-8 -*-
"""
第二阶段：LangChain中间件(Middleware)入门 - 代码案例索引
=========================================================

本文件夹包含中间件基础概念的代码案例

文件列表：
00_说明.py              - 本索引文件
01_中间件架构原理.py    - 中间件设计原理
02_中间件四大分类.py    - 监控/修改/控制/强制类

中间件核心概念：
- 拦截、修改、控制和增强Agent执行流程
- 六大Hook点：before_agent → before_model → wrap_model_call → wrap_tool_call → after_model → after_agent
- SOLID五大设计原则

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 3. LangChain1.0 Agent智能体中间件应用实战/第二节课/01_中间件架构原理.py"
"""

print("=" * 60)
print("第二阶段：LangChain中间件(Middleware)入门")
print("=" * 60)
print("""
中间件核心概念：

1. 六大Hook点
   before_agent → before_model → wrap_model_call
   → wrap_tool_call → after_model → after_agent

2. 四大分类
   - Monitor（监控类）：观察执行状态
   - Modify（修改类）：修改输入/输出
   - Control（控制类）：流程阻断、人工介入
   - Enforce（强制类）：安全过滤、限流

代码案例：
01_中间件架构原理.py  - 中间件设计原理
02_中间件四大分类.py  - 四大分类详解
""")