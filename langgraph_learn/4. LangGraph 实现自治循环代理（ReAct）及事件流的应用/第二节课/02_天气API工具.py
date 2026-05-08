"""
天气查询 API 工具
=================

本文件演示如何封装 OpenWeather API 为可调用的天气查询工具。
"""

import requests


def get_weather(loc):
    """
    Function to query current weather.

    :param loc: Required parameter, of type string, representing the specific city name
                for the weather query. Note that for cities in China, the corresponding
                English city name should be used. For example, to query the weather for
                Beijing, the loc parameter should be input as 'Beijing'.
    :return: The result of the OpenWeather API query for current weather, including:
            - city_id: Unique identifier for the city
            - city_name: Name of the city
            - main_weather: Main weather condition (e.g., Clear, Clouds, Rain)
            - description: Detailed weather description
            - temperature: Current temperature
            - feels_like: Feels like temperature
            - humidity: Humidity percentage
            - wind_speed: Wind speed
            - icon: Weather icon code
    """
    api_key = "your_openweather_api_key"  # 替换为你的 OpenWeather API Key
    base_url = "https://api.openweathermap.org/data/2.5/weather?"

    try:
        # 发送请求
        url = f"{base_url}q={loc}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200:
            result = {
                "city_id": data["id"],
                "city_name": data["name"],
                "main_weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"]
            }
            return result
        else:
            return {"error": f"API request failed with code: {data.get('cod')}"}

    except Exception as e:
        return {"error": str(e)}


# 测试天气查询
if __name__ == "__main__":
    result = get_weather('beijing')
    print(result)