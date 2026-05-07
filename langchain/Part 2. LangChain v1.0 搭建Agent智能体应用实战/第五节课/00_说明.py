# -*- coding: utf-8 -*-
"""
第五阶段：工具（Tools）的工具使用 - 代码案例索引
==================================================

本文件夹包含工具定义和使用的代码案例

文件列表：
00_说明.py                    - 本索引文件
01_tool装饰器.py              - @tool 装饰器定义工具
02_StructuredTool.py          - StructuredTool.from_function
03_多工具使用.py              - 多工具组合使用
04_动态工具加载.py            - 避免上下文过长
05_SystemPrompt最佳实践.py    - 系统提示词设计

工具定义三种方式：
1. @tool 装饰器       - 最简单，适合快速原型
2. StructuredTool    - 更强控制，适合生产环境
3. 继承 StructuredTool - 完全自定义，适合复杂逻辑

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第五节课/01_tool装饰器.py"
"""

print("=" * 60)
print("第五阶段：工具（Tools）的工具使用")
print("=" * 60)
print("""
工具定义三种方式对比：

1. @tool 装饰器
   • 优点：代码简洁，一行装饰器
   • 缺点：参数控制较弱
   • 适用：快速原型、简单工具

2. StructuredTool.from_function()
   • 优点：支持 Pydantic 验证
   • 缺点：代码较多
   • 适用：生产环境、需要参数校验

3. 继承 StructuredTool
   • 优点：完全自定义
   • 缺点：代码复杂
   • 适用：复杂业务逻辑、状态管理

代码案例：
01_tool装饰器.py        - @tool 装饰器基础
02_StructuredTool.py    - 强类型参数验证
03_多工具使用.py        - 工具组合
04_动态工具加载.py      - 避免上下文过长
05_SystemPrompt最佳实践.py - 提示词设计
""")