# -*- coding: utf-8 -*-
"""
【案例2】天气查询工具定义
============================================

本案例展示如何定义天气查询工具

要点：
1. 使用requests调用外部API
2. @tool装饰器的使用
3. 工具的参数定义与验证
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import requests
import json
from langchain_core.tools import tool
from typing import Optional
from pydantic import BaseModel, Field

# ============================================================
# 2. 定义天气查询工具
# ============================================================
class WeatherLoc(BaseModel):
    location: str = Field(description="The location name of the city")

@tool
def get_weather(loc: str) -> str:
    """
    Function to query current weather.
    :param loc: Required parameter, of type string, representing the specific city name
    :return: The result of the OpenWeather API query for current weather
    """
    # 构建请求
    url = "https://api.openweathermap.org/data/2.5/weather"

    # 设置查询参数
    params = {
        "q": loc,
        "appid": "your-api-key",  # 需要替换为实际API Key
        "units": "metric",
        "lang": "zh_cn"
    }

    # 发送GET请求
    response = requests.get(url, params=params)

    # 解析响应
    data = response.json()
    return json.dumps(data)

# ============================================================
# 3. 测试工具
# ============================================================
print("=" * 50)
print("天气查询工具定义")
print("=" * 50)

print(f"\n工具名称: {get_weather.name}")
print(f"工具描述: {get_weather.description}")
print(f"参数Schema: {get_weather.args}")

# 测试调用
print("\n--- 测试调用 ---")
result = get_weather.invoke({"loc": "beijing"})
print(f"输入: beijing")
print(f"结果: {result[:200]}...")