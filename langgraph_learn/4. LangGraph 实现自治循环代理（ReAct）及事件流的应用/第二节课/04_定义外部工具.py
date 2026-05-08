"""
定义外部工具
============

本文件演示如何使用 LangChain 的 @tool 装饰器将函数封装为 LangGraph 支持的工具格式。

使用 @tool 装饰器的优势：
1. 自动生成工具描述
2. 支持 Pydantic 模型进行参数验证
3. 与 LangGraph 无缝集成
"""

from langchain_core.tools import tool
from typing import Union, Optional
from pydantic import BaseModel, Field
import requests
import json

# -----------------------------------------------------------------------------
# 1. 使用 Pydantic 模型定义工具参数
# -----------------------------------------------------------------------------
class WeatherLoc(BaseModel):
    """天气查询参数模型"""
    location: str = Field(description="The location name of the city")


class WeatherInfo(BaseModel):
    """提取的天气信息模型"""
    city_id: int = Field(..., description="The unique identifier for the city")
    city_name: str = Field(..., description="The name of the city")
    main_weather: str = Field(..., description="Main weather condition")
    description: str = Field(..., description="Detailed weather description")
    temperature: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in m/s")


class SearchQuery(BaseModel):
    """网络搜索查询参数模型"""
    query: str = Field(description="Questions for networking queries")


# -----------------------------------------------------------------------------
# 2. 定义网络搜索工具
# -----------------------------------------------------------------------------
@tool(args_schema=SearchQuery)
def fetch_real_time_info(query):
    """
    Get real-time Internet information.

    This tool allows you to search the web for current information,
    news, and answers to questions.

    Args:
        query: The search query string

    Returns:
        Search results with titles, snippets, and links
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": 1,
    })
    headers = {
        'X-API-KEY': 'your_serper_api_key',  # 替换为你的 Serper API Key
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        data = response.json()

        if response.status_code == 200 and 'organic' in data:
            results = []
            for item in data['organic'][:3]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
            return json.dumps(results, ensure_ascii=False)
        else:
            return json.dumps({"error": "Search failed"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# -----------------------------------------------------------------------------
# 3. 定义天气查询工具
# -----------------------------------------------------------------------------
@tool(args_schema=WeatherLoc)
def get_weather(location: str) -> dict:
    """
    Query current weather information for a specific city.

    This function queries the OpenWeather API to get real-time weather data
    including temperature, humidity, weather conditions, and more.

    Args:
        location: City name (use English name for Chinese cities, e.g., 'Beijing')

    Returns:
        A dictionary containing weather information including:
        - city_id, city_name, main_weather, description
        - temperature, feels_like, humidity, wind_speed, icon
    """
    api_key = "your_openweather_api_key"  # 替换为你的 OpenWeather API Key
    base_url = "https://api.openweathermap.org/data/2.5/weather?"

    try:
        url = f"{base_url}q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200:
            return {
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
        else:
            return {"error": f"API request failed with code: {data.get('cod')}"}
    except Exception as e:
        return {"error": str(e)}


# -----------------------------------------------------------------------------
# 4. 数据库操作工具（复用 03_数据库模型.py 中的函数）
# -----------------------------------------------------------------------------
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/weather_db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Weather(Base):
    __tablename__ = 'weather'
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(50))
    main_weather = Column(String(50))
    description = Column(String(100))
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    icon = Column(String(10))
    record_time = Column(String(50))


Base.metadata.create_all(engine)


@tool
def insert_weather_to_db(weather_data: dict) -> dict:
    """
    Insert or update weather data in the database.

    This tool stores weather information into MySQL database for later retrieval.

    Args:
        weather_data: Dictionary containing weather information

    Returns:
        Status message indicating success or failure
    """
    session = SessionLocal()
    try:
        weather = Weather(
            city_id=weather_data.get("city_id"),
            city_name=weather_data.get("city_name"),
            main_weather=weather_data.get("main_weather"),
            description=weather_data.get("description"),
            temperature=weather_data.get("temperature"),
            feels_like=weather_data.get("feels_like"),
            humidity=weather_data.get("humidity"),
            wind_speed=weather_data.get("wind_speed"),
            icon=weather_data.get("icon"),
            record_time=weather_data.get("dt", "")
        )
        session.merge(weather)
        session.commit()
        return {"status": "success", "message": "Weather data inserted successfully"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        session.close()


@tool
def query_weather_from_db(city_name: str) -> dict:
    """
    Query weather data from database for a specific city.

    This tool retrieves stored weather information from MySQL database.

    Args:
        city_name: Name of the city to query

    Returns:
        Weather data if found, or error message if not found
    """
    session = SessionLocal()
    try:
        weather = session.query(Weather).filter(Weather.city_name == city_name).first()
        if weather:
            return {
                "city_id": weather.city_id,
                "city_name": weather.city_name,
                "main_weather": weather.main_weather,
                "description": weather.description,
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "icon": weather.icon,
                "record_time": weather.record_time
            }
        return {"error": f"No weather data found for {city_name}"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()


# -----------------------------------------------------------------------------
# 5. 工具列表
# -----------------------------------------------------------------------------
tools = [fetch_real_time_info, get_weather, insert_weather_to_db, query_weather_from_db]

if __name__ == "__main__":
    print("Available tools:")
    for t in tools:
        print(f"  - {t.name}: {t.description[:50]}...")