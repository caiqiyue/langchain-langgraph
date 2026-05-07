# -*- coding: utf-8 -*-
"""
【案例3】数据库操作工具定义
============================================

本案例展示如何定义数据库操作工具

要点：
1. SQLAlchemy模型定义
2. @tool装饰器与Pydantic Schema
3. 工具的参数校验
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
from langchain_core.tools import tool
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# 2. 数据库设置
# ============================================================
Base = declarative_base()

class Weather(Base):
    __tablename__ = 'weather'
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(50))
    main_weather = Column(String(50))
    description = Column(String(100))
    temperature = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)

# 数据库连接配置
DATABASE_URI = 'mysql+pymysql://root:password@localhost/langgraph_agent?charset=utf8mb4'
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ============================================================
# 3. 定义工具参数Schema
# ============================================================
class WeatherInfo(BaseModel):
    """Extracted weather information for a specific city."""
    city_id: int = Field(..., description="The unique identifier for the city")
    city_name: str = Field(..., description="The name of the city")
    main_weather: str = Field(..., description="The main weather condition")
    description: str = Field(..., description="A detailed description of the weather")
    temperature: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(..., description="Feels-like temperature in Celsius")
    temp_min: float = Field(..., description="Minimum temperature in Celsius")
    temp_max: float = Field(..., description="Maximum temperature in Celsius")

class QueryWeatherSchema(BaseModel):
    """Schema for querying weather information by city name."""
    city_name: str = Field(..., description="The name of the city to query weather information")

# ============================================================
# 4. 定义数据库操作工具
# ============================================================
@tool(args_schema=WeatherInfo)
def insert_weather_to_db(city_id, city_name, main_weather, description, temperature, feels_like, temp_min, temp_max):
    """Insert weather information into the database."""
    session = Session()
    try:
        weather = Weather(
            city_id=city_id,
            city_name=city_name,
            main_weather=main_weather,
            description=description,
            temperature=temperature,
            feels_like=feels_like,
            temp_min=temp_min,
            temp_max=temp_max
        )
        session.merge(weather)
        session.commit()
        return {"messages": [f"天气数据已成功存储至Mysql数据库。"]}
    except Exception as e:
        session.rollback()
        return {"messages": [f"数据存储失败，错误原因：{e}"]}
    finally:
        session.close()

@tool(args_schema=QueryWeatherSchema)
def query_weather_from_db(city_name: str):
    """Query weather information from the database by city name."""
    session = Session()
    try:
        weather_data = session.query(Weather).filter(Weather.city_name == city_name).first()
        if weather_data:
            return {
                "city_id": weather_data.city_id,
                "city_name": weather_data.city_name,
                "main_weather": weather_data.main_weather,
                "description": weather_data.description,
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "temp_min": weather_data.temp_min,
                "temp_max": weather_data.temp_max
            }
        else:
            return {"messages": [f"未找到城市 '{city_name}' 的天气信息。"]}
    except Exception as e:
        return {"messages": [f"查询失败，错误原因：{e}"]}
    finally:
        session.close()

# ============================================================
# 5. 测试工具
# ============================================================
print("=" * 50)
print("数据库操作工具定义")
print("=" * 50)

print(f"\ninsert_weather_to_db工具名称: {insert_weather_to_db.name}")
print(f"query_weather_from_db工具名称: {query_weather_from_db.name}")