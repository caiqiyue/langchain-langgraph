# -*- coding: utf-8 -*-
"""
【案例 1】@tool 装饰器 - 最简单的工具定义方式
===============================================

本案例展示如何使用 @tool 装饰器快速定义工具。

@tool 装饰器是 LangChain 中最简单、最直观的工具创建方式：
- 一行装饰器，将普通 Python 函数转换为 Agent 可调用的工具
- 自动从函数签名生成工具的参数 schema
- 适合快速原型开发和简单工具实现

要点：
1. 理解 @tool 装饰器的工作原理
2. 掌握如何定义一个简单的工具
3. 理解自动生成的参数 schema
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# 2. 导入核心组件
# ============================================================
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

print("=" * 60)
print("案例 1: @tool 装饰器 - 最简单的工具定义")
print("=" * 60)

# ============================================================
# 3. 使用 @tool 装饰器定义工具
# ============================================================

# --- 简单工具：乘法计算 ---
@tool
def multiply(a: int, b: int) -> int:
    """
    计算两个整数的乘积。

    参数:
        a (int): 第一个整数
        b (int): 第二个整数

    返回:
        int: 两个数的乘积
    """
    return a * b

# --- 简单工具：获取天气 ---
@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    参数:
        city (str): 城市名称，如"北京"、"上海"

    返回:
        str: 天气信息描述
    """
    weather_data = {
        "北京": "晴朗，气温25°C，适合外出",
        "上海": "多云，气温28°C，稍有闷热",
        "广州": "小雨，气温30°C，记得带伞"
    }
    return weather_data.get(city, f"抱歉，暂不支持{city}的天气查询")

# --- 简单工具：搜索新闻 ---
@tool
def search_news(keyword: str) -> str:
    """
    搜索相关新闻。

    参数:
        keyword (str): 搜索关键词

    返回:
        str: 新闻摘要
    """
    news_data = {
        "AI": "最新AI资讯：GPT-5即将发布，多模态能力大幅提升",
        "Python": "Python 3.13正式发布，性能提升显著",
        "LangChain": "LangChain 1.0正式发布，Agent开发更简单"
    }
    return news_data.get(keyword, f"关于'{keyword}'暂无最新消息")

# ============================================================
# 4. 查看自动生成的工具信息
# ============================================================
print("\n" + "=" * 60)
print("工具元信息（自动生成）")
print("=" * 60)

print(f"\n工具名称: {multiply.name}")
print(f"工具描述: {multiply.description}")
print(f"参数 Schema: {multiply.args_schema}")

# ============================================================
# 5. 初始化模型并创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# 将工具添加到列表
tools = [multiply, get_weather, search_news]

# 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""你是一个多功能的智能助手，可以：
1. 进行数学计算（使用 multiply 工具）
2. 查询天气（使用 get_weather 工具）
3. 搜索新闻（使用 search_news 工具）

请根据用户问题选择合适的工具。"""
)

# ============================================================
# 6. 测试不同类型的工具调用
# ============================================================
print("\n" + "=" * 60)
print("测试工具调用")
print("=" * 60)

# 测试1：计算
问题1 = "帮我计算一下 12 乘以 8"
print(f"\n问题1: {问题1}")
result1 = agent.invoke({"messages": [{"role": "user", "content": 问题1}]})
print(f"回答: {result1['messages'][-1].content}")

# 测试2：天气
问题2 = "北京今天的天气怎么样？"
print(f"\n问题2: {问题2}")
result2 = agent.invoke({"messages": [{"role": "user", "content": 问题2}]})
print(f"回答: {result2['messages'][-1].content}")

# 测试3：新闻
问题3 = "有什么关于AI的最新消息吗？"
print(f"\n问题3: {问题3}")
result3 = agent.invoke({"messages": [{"role": "user", "content": 问题3}]})
print(f"回答: {result3['messages'][-1].content}")

# ============================================================
# 7. 单独测试工具（不通过 Agent）
# ============================================================
print("\n" + "=" * 60)
print("单独测试工具")
print("=" * 60)

# 直接调用工具
print("\n直接调用 multiply.invoke:")
结果 = multiply.invoke({"a": 15, "b": 6})
print(f"  15 × 6 = {结果}")

print("\n直接调用 get_weather.invoke:")
结果 = get_weather.invoke({"city": "上海"})
print(f"  {结果}")

# ============================================================
# 8. @tool 装饰器总结
# ============================================================
print("\n" + "=" * 60)
print("✅ @tool 装饰器总结")
print("=" * 60)
print("""
@tool 装饰器特点：

1. 【极简语法】
   @tool
   def my_tool(param: str) -> str:
       """工具描述"""
       return result

2. 【自动生成】
   • 工具名称：函数名
   • 工具描述：docstring 第一行
   • 参数 schema：从类型注解自动推断

3. 【适用场景】
   ✅ 快速原型验证
   ✅ 简单工具实现
   ✅ 开发测试阶段

4. 【局限性】
   ❌ 参数控制较弱
   ❌ 不支持复杂参数验证
   ❌ 不支持异步

5. 【最佳实践】
   • 写清晰的 docstring（LLM 靠它理解工具）
   • 使用类型注解（让 schema 更准确）
   • 描述要包含：功能、参数、示例
""")