"""
创建 ReAct Agent
=================

本文件演示如何使用 LangGraph 的 create_react_agent 方法创建 ReAct Agent。

create_react_agent 是 LangGraph 预置的方法，它封装了完整的 ReAct 循环逻辑：
1. 模型调用
2. 工具选择
3. 工具执行
4. 结果处理
5. 循环判断
"""

import getpass
import os
from langchain_openai import ChatOpenAI

# -----------------------------------------------------------------------------
# 1. 初始化 OpenAI 模型
# -----------------------------------------------------------------------------
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# -----------------------------------------------------------------------------
# 2. 创建 ReAct Agent
# -----------------------------------------------------------------------------
# 注意：tools 变量需要从 04_定义外部工具.py 导入
# 这里假设 tools 已经定义
# from 04_定义外部工具 import tools

# from langgraph.prebuilt import create_react_agent
# graph = create_react_agent(llm, tools=tools)

# -----------------------------------------------------------------------------
# 3. Agent 图结构可视化
# -----------------------------------------------------------------------------
# 使用 get_graph().draw_mermaid_png() 可以导出 Agent 的 Mermaid 图表
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

"""
Agent 执行流程说明：

1. START -> agent (调用模型)
2. agent -> {
       "continue": tools (如果有工具调用),
       "end": END (如果没有工具调用)
   }
3. tools -> agent (工具执行完后继续调用模型)
4. 循环直到没有工具调用或达到最大迭代次数
"""


# =============================================================================
# 完整示例
# =============================================================================
if __name__ == "__main__":
    # 导入工具列表
    from 04_定义外部工具 import tools

    # 创建 Agent
    from langgraph.prebuilt import create_react_agent
    graph = create_react_agent(llm, tools=tools)

    print("ReAct Agent created successfully!")
    print(f"Number of tools: {len(tools)}")
    print(f"Tools: {[t.name for t in tools]}")