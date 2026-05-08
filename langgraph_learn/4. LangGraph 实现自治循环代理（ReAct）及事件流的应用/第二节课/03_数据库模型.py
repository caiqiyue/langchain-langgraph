"""
MySQL 数据库模型
=================

本文件演示如何使用 SQLAlchemy ORM 定义天气数据存储模型。
"""

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------------------------------------------------------
# 1. 数据库配置
# -----------------------------------------------------------------------------
# 请根据实际情况修改数据库连接参数
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/weather_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------------------------------------------------------
# 2. Weather 模型定义
# -----------------------------------------------------------------------------
class Weather(Base):
    """存储实时天气信息的数据库模型"""
    __tablename__ = 'weather'

    city_id = Column(Integer, primary_key=True)      # 城市ID
    city_name = Column(String(50))                    # 城市名称
    main_weather = Column(String(50))               # 主要天气状况
    description = Column(String(100))                 # 详细描述
    temperature = Column(Float)                       # 温度
    feels_like = Column(Float)                       # 体感温度
    humidity = Column(Float)                          # 湿度
    wind_speed = Column(Float)                       # 风速
    icon = Column(String(10))                        # 天气图标码
    record_time = Column(String(50))                 # 记录时间

    def __repr__(self):
        return f"<Weather(city_name='{self.city_name}', temperature={self.temperature})>"


# -----------------------------------------------------------------------------
# 3. 数据库操作函数
# -----------------------------------------------------------------------------
def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(engine)


def get_db_session():
    """获取数据库会话"""
    return SessionLocal()


def insert_weather_to_db(weather_data: dict):
    """
    将天气数据插入数据库

    :param weather_data: 天气数据字典
    """
    session = get_db_session()
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
            record_time=weather_data.get("dt")
        )
        session.merge(weather)  # 使用 merge 替代 insert，如果是更新则更新已有记录
        session.commit()
        return {"status": "success", "message": "Weather data inserted successfully"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        session.close()


def query_weather_from_db(city_name: str):
    """
    从数据库查询天气信息

    :param city_name: 城市名称
    """
    session = get_db_session()
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
# 4. 初始化数据库
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")