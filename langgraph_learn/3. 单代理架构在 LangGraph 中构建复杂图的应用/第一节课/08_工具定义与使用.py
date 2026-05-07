# -*- coding: utf-8 -*-
"""
【案例8】工具定义与bind_tools使用
============================================

本案例展示如何定义多个工具并使用bind_tools绑定到模型

要点：
1. 多个工具的定义
2. bind_tools方法使用
3. 模型自动生成tool_calls
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# ============================================================
# 3. 定义工具参数schema
# ============================================================
class SearchQuery(BaseModel):
    query: str = Field(description="Questions for networking queries")

class WeatherLoc(BaseModel):
    location: str = Field(description="The location name of the city")

# ============================================================
# 4. 定义工具
# ============================================================
@tool
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    # 实现代码...
    return f"搜索结果: {query}"

@tool
def get_weather(location):
    """Call to get the current weather."""
    if location.lower() in ["beijing"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai"]:
        return "上海的温度是20度，部分多云。"
    else:
        return "不好意思，并未查询到具体的天气信息。"

# ============================================================
# 5. 绑定工具到模型
# ============================================================
tools = [fetch_real_time_info, get_weather]
model_with_tools = llm.bind_tools(tools)

print("=" * 50)
print("工具绑定到模型")
print("=" * 50)
print(f"\n模型类型: {type(model_with_tools).__name__}")
print(f"绑定工具数量: {len(tools)}")

# ============================================================
# 6. 测试模型工具调用
# ============================================================
print("\n" + "=" * 50)
print("测试模型工具调用")
print("=" * 50)

# 测试网络搜索
result1 = model_with_tools.invoke("Cloud3.5的最新新闻")
print(f"\n查询1: Cloud3.5的最新新闻")
print(f"tool_calls: {result1.tool_calls}")

# 测试天气查询
result2 = model_with_tools.invoke("北京现在多少度呀？")
print(f"\n查询2: 北京现在多少度呀？")
print(f"tool_calls: {result2.tool_calls}")

# ============================================================
# 7. 使用ToolNode执行工具
# ============================================================
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)

print("\n" + "=" * 50)
print("使用ToolNode执行工具")
print("=" * 50)

# 执行第一个工具调用
tool_result1 = tool_node.invoke({"messages": [result1]})
print(f"\n工具1执行结果: {tool_result1}")

# 执行第二个工具调用
tool_result2 = tool_node.invoke({"messages": [result2]})
print(f"\n工具2执行结果: {tool_result2}")