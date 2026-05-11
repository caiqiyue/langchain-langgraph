# -*- coding: utf-8 -*-
"""
【案例 5】工具定义 @tool 装饰器
==========================================

本案例展示如何使用 @tool 装饰器定义自定义工具
工具是 Agent 系统的核心组成部分

要点：
1. @tool 装饰器的基本用法
2. 工具的描述和参数
3. 工具的调用方式
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / ".env"
load_dotenv(env_path, override=True)

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")
os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 5: 工具定义 @tool 装饰器")
print("=" * 50)

from langchain_core.tools import tool

# ============================================================
# 1. 定义工具
# ============================================================
"""
【@tool 装饰器原理】

@tool 装饰器会自动：
1. 将普通函数转换为 BaseTool 对象
2. 从 docstring 提取工具描述
3. 从函数签名提取参数信息
4. 生成 JSON Schema 用于 Function Calling
"""

@tool
def get_weather(city: str) -> str:
    """
    查询城市天气

    Args:
        city: 城市名称，如"北京"、"上海"、"深圳"

    Returns:
        天气信息字符串，包含温度和天气状况
    """
    weather_data = {
        "北京": "多云转晴，25°C",
        "上海": "小雨，22°C",
        "深圳": "晴天，28°C",
        "杭州": "阴天，23°C",
        "广州": "雷阵雨，26°C"
    }
    return weather_data.get(city, "暂无该城市数据")


@tool
def calculate(expression: str) -> str:
    """
    执行数学计算

    Args:
        expression: 数学表达式，如 "2 + 3 * 4"、"10 ** 2"、"sqrt(16)"

    Returns:
        计算结果字符串
    """
    try:
        # 注意：实际生产中应该使用更安全的求值方式
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"


@tool
def get_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前时间

    Args:
        format: 时间格式，默认为"%Y-%m-%d %H:%M:%S"

    Returns:
        格式化的时间字符串
    """
    from datetime import datetime
    return datetime.now().strftime(format)


# ============================================================
# 2. 工具属性
# ============================================================
print("\n工具属性:")
print("-" * 30)

print(f"\nget_weather:")
print(f"  名称: {get_weather.name}")
print(f"  描述: {get_weather.description}")
print(f"  参数: {get_weather.args}")

print(f"\ncalculate:")
print(f"  名称: {calculate.name}")
print(f"  描述: {calculate.description}")

print(f"\nget_time:")
print(f"  名称: {get_time.name}")
print(f"  描述: {get_time.description}")

# ============================================================
# 3. 调用工具
# ============================================================
print("\n" + "-" * 30)
print("工具调用示例:")
print("-" * 30)

# 单个调用
result1 = get_weather.invoke({"city": "北京"})
print(f"\nget_weather(city='北京'): {result1}")

result2 = calculate.invoke({"expression": "123 * 456"})
print(f"\ncalculate(expression='123 * 456'): {result2}")

result3 = get_time.invoke({})
print(f"\nget_time(): {result3}")

# ============================================================
# 4. 批量调用工具
# ============================================================
print("\n" + "-" * 30)
print("批量调用工具:")
print("-" * 30)

# 批量调用 - 在单个工具上使用 batch
print("get_weather 批量查询多个城市:")
weather_results = get_weather.batch([
    {"city": "上海"},
    {"city": "北京"},
    {"city": "深圳"}
])
for i, result in enumerate(weather_results):
    print(f"  结果 {i+1}: {result}")

print("\ncalculate 批量计算多个表达式:")
calc_results = calculate.batch([
    {"expression": "2 ** 10"},
    {"expression": "123 * 456"},
    {"expression": "1000 - 1"}
])
for i, result in enumerate(calc_results):
    print(f"  结果 {i+1}: {result}")

print("\nget_time 批量获取时间:")
time_results = get_time.batch([{}, {}, {}])
for i, result in enumerate(time_results):
    print(f"  结果 {i+1}: {result}")

# ============================================================
# 【补充】@tool 装饰器的底层原理
# ============================================================
print("\n" + "=" * 50)
print("@tool 装饰器原理")
print("=" * 50)
print("""
@tool 装饰器内部做了以下事情：

1. 函数签名分析
   - 提取参数名和类型注解
   - 生成 JSON Schema

2. Docstring 解析
   - 提取工具描述
   - 提取参数描述（Args 部分）

3. BaseTool 对象创建
   - 设置 name = 函数名
   - 设置 description = docstring 第一行
   - 设置 args_schema = JSON Schema

4. invoke() 方法绑定
   - 将调用请求转发给原函数
   - 处理参数验证和异常
""")
