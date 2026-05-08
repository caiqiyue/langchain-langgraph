"""
第2阶段、工具调用代理Tool Calling Agent

本节课程内容：
1. 使用ToolNode接入工具
   - @tool 装饰器
   - ToolNode 实例化
   - 串行和并行工具调用

2. Tool Calling Agent的完整实现案例
   - 多个工具的定义
   - 结构化输出路由
   - 完整的图构建

3. 手动构建Tool Calling Agent的方法
   - 手动实现 execute_function 节点
   - exists_function_calling 路由判断
   - 完整的工具调用链路

环境依赖：
- langgraph
- langchain-openai
- langchain-core
- requests (用于实时联网检索)

安装命令：
pip install langgraph langchain-openai langchain-core requests
"""