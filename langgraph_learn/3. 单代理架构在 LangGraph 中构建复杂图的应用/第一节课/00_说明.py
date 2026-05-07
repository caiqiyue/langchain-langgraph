# -*- coding: utf-8 -*-
"""
第三课：单代理架构在 LangGraph 中构建复杂图的应用 - 代码案例索引
==========================================

本文件夹包含单代理架构在 LangGraph 中构建复杂图的应用的所有代码案例

文件列表：
01_基础图结构与add_edge.py      - 基础图结构与add_edge方法
02_条件边与add_conditional_edges.py - 条件边与add_conditional_edges方法
03_使用Pydantic做结构化输出.py  - 使用Pydantic进行结构化输出
04_使用TypedDict做结构化输出.py - 使用TypedDict进行结构化输出
05_Json_Schema结构化输出.py     - 使用Json Schema进行结构化输出
06_结合结构化输出构建路由图.py  - 结合结构化输出构建完整路由图
07_使用ToolNode接入工具.py      - 使用ToolNode接入外部工具
08_工具定义与使用.py            - 工具定义与bind_tools使用
09_Tool_Calling_Agent完整实现.py - Tool Calling Agent完整实现案例
10_手动构建Tool_Calling_Agent.py - 手动构建Tool Calling Agent

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "3. 单代理架构在 LangGraph 中构建复杂图的应用/第一节课/01_基础图结构与add_edge.py"

配置：
    API_KEY = 从环境变量 OPENAI_API_KEY 读取
    模型 = gpt-4o-mini 或 gpt-4o
"""

print("=" * 50)
print("第三课：单代理架构在 LangGraph 中构建复杂图的应用")
print("=" * 50)
print("""
本课程序件列表：

01_基础图结构与add_edge.py      - 基础图结构与add_edge方法
02_条件边与add_conditional_edges.py - 条件边与add_conditional_edges方法
03_使用Pydantic做结构化输出.py  - 使用Pydantic进行结构化输出
04_使用TypedDict做结构化输出.py - 使用TypedDict进行结构化输出
05_Json_Schema结构化输出.py     - 使用Json Schema进行结构化输出
06_结合结构化输出构建路由图.py  - 结合结构化输出构建完整路由图
07_使用ToolNode接入工具.py      - 使用ToolNode接入外部工具
08_工具定义与使用.py            - 工具定义与bind_tools使用
09_Tool_Calling_Agent完整实现.py - Tool Calling Agent完整实现案例
10_手动构建Tool_Calling_Agent.py - 手动构建Tool Calling Agent

运行示例：
    python "3. 单代理架构在 LangGraph 中构建复杂图的应用/第一节课/01_基础图结构与add_edge.py"
""")