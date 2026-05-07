# -*- coding: utf-8 -*-
"""
【案例8】异步流输出astream
============================================

本案例展示LangGraph异步流输出

要点：
1. astream方法的使用
2. 异步迭代器的处理
3. values模式的异步使用
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

# ============================================================
# 2. 设置API密钥并创建代理
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    if location.lower() in ["beijing", "北京"]:
        return "北京的温度是16度，天气晴朗。"
    else:
        return f"未找到{location}的天气信息。"

tools = [get_weather]
graph = create_react_agent(llm, tools=tools)

# ============================================================
# 3. 异步流输出示例
# ============================================================
print("=" * 50)
print("异步流输出 astream")
print("=" * 50)
print("""
异步流输出说明：
- 在异步开发环境中使用astream方法
- 使用async for遍历结果
- 专为非阻塞工作流程而设计
- 可使用的模式和stream一致
""")

# ============================================================
# 4. 执行异步流输出
# ============================================================
import asyncio

async def run_stream():
    """执行异步流输出"""
    print("\n--- 执行异步流输出 ---")

    # 使用values模式
    async for chunk in graph.astream(input={"messages": ["你好，四川的天气怎么样？"]}, stream_mode="values"):
        message = chunk["messages"][-1]
        message.pretty_print()

# 运行异步函数
asyncio.run(run_stream())

# ============================================================
# 5. 获取最终结果
# ============================================================
async def get_final_result():
    """获取最终结果"""
    print("\n--- 获取最终结果 ---")

    final_result = None
    async for chunk in graph.astream(input={"messages": ["你好，乌鲁木齐的天气怎么样？"]}, stream_mode="values"):
        final_result = chunk

    print(f"最终结果:")
    final_result["messages"][-1].pretty_print()

asyncio.run(get_final_result())