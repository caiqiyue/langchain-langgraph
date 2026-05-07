# -*- coding: utf-8 -*-
"""
Script to generate course files for LangGraph courses 4 and 5
"""

import os

base4 = "E:/langchain_learning/langgraph_learn/4. LangGraph 实现自治循环代理（ReAct）及事件流的应用/第一节课"
os.makedirs(base4, exist_ok=True)
os.makedirs(base4 + "/assets", exist_ok=True)

# ===== Course 4 Python File 1 =====
py1 = '''# -*- coding: utf-8 -*-
"""
【案例 1】LangGraph 实战 ReAct 自治循环代理
============================================

本案例展示如何使用 LangGraph 的 create_react_agent 预构建方法，
构建一个具备多工具调用能力的 ReAct 自治循环代理，实现：
- 实时天气数据查询（OpenWeather API）
- 天气数据持久化存储（Mysql 数据库）
- 联网实时检索

要点：
1. create_react_agent 预构建方法的使用
2. 多工具的注册与 ToolNode 自动调度
3. ReAct 循环代理的自主决策机制
4. 多轮对话中的状态管理与图执行流程
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os

# LangSmith 追踪配置
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "your-langsmith-api-key")
os.environ["LANGCHAIN_PROJECT"] = "langGraph_ReAct"

# ============================================================
# 2. 工具定义
# ============================================================
import json
import requests
from langchain_core.tools import tool
from typing import Union, Optional
from pydantic import BaseModel, Field

# --- 2.1 Pydantic 模型：天气信息结构化输出 ---
class WeatherLoc(BaseModel):
    location: str = Field(description="The location name of the city")

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


# --- 2.2 天气查询工具 ---
@tool(args_schema=WeatherLoc)
def get_weather(location: str) -> str:
    """
    Function to query current weather.
    :param location: Required parameter, of type string, representing the specific city name for the weather query.
    For cities in China, the corresponding English city name should be used.
    :return: The result of the OpenWeather API query for current weather.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": os.getenv("OPENWEATHER_API_KEY", "your-api-key"),
        "units": "metric",
        "lang": "zh_cn"
    }
    response = requests.get(url, params=params)
    return json.dumps(response.json())


# --- 2.3 联网检索工具 ---
class SearchQuery(BaseModel):
    query: str = Field(description="Questions for networking queries")

@tool(args_schema=SearchQuery)
def fetch_real_time_info(query: str) -> str:
    """Get real-time Internet information via Serper API."""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 1})
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY", "your-serper-api-key"),
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)
    if "organic" in data:
        return json.dumps(data["organic"], ensure_ascii=False)
    else:
        return json.dumps({"error": "No organic results found"}, ensure_ascii=False)


# --- 2.4 数据库模型与工具 ---
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Weather(Base):
    __tablename__ = "weather"
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(50))
    main_weather = Column(String(50))
    description = Column(String(100))
    temperature = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)

# 数据库连接（替换为实际连接信息）
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "mysql+pymysql://user:password@host:port/langgraph_agent?charset=utf8mb4"
)
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@tool(args_schema=WeatherInfo)
def insert_weather_to_db(
    city_id: int, city_name: str, main_weather: str,
    description: str, temperature: float, feels_like: float,
    temp_min: float, temp_max: float
):
    """Insert weather information into the MySQL database."""
    session = Session()
    try:
        weather = Weather(
            city_id=city_id, city_name=city_name, main_weather=main_weather,
            description=description, temperature=temperature, feels_like=feels_like,
            temp_min=temp_min, temp_max=temp_max
        )
        session.merge(weather)
        session.commit()
        return {"messages": ["天气数据已成功存储至Mysql数据库。"]}
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
            return {"messages": [f"未找到城市 \\'{city_name}\\' 的天气信息。"]}
    except Exception as e:
        return {"messages": [f"查询失败，错误原因：{e}"]}
    finally:
        session.close()


# --- 2.5 工具列表 ---
tools = [fetch_real_time_info, get_weather, insert_weather_to_db, query_weather_from_db]


# ============================================================
# 3. 大模型实例与 ReAct 代理构建
# ============================================================
import getpass
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# create_react_agent 参数：
# - model: 支持工具调用的 LangChain 聊天模型
# - tools: 工具列表（ToolExecutor 或 ToolNode 实例）
# - state_schema: 图的状态模式，默认为 AgentState（包含 messages 和 is_last_step）
graph = create_react_agent(llm, tools=tools)


# ============================================================
# 4. 图执行与调用示例
# ============================================================
from IPython.display import Image, display

# 可视化 ReAct 代理图结构
display(Image(graph.get_graph().draw_mermaid_png()))


# --- 4.1 无工具调用：直接生成响应 ---
response1 = graph.invoke({"messages": ["你好，请你介绍一下你自己"]})
print(response1["messages"][-1].content)


# --- 4.2 单工具调用：天气查询 ---
response2 = graph.invoke({"messages": ["北京今天的天气怎么样？"]})
print(response2["messages"][-1].content)


# --- 4.3 多工具调用：查询+存储 ---
response3 = graph.invoke({
    "messages": [
        "帮我查一下北京、上海，哈尔滨三个城市的天气，"
        "告诉我哪个城市最适合出游。同时，把查询到的数据存储到数据库中"
    ]
})
print(response3["messages"][-1].content)


# --- 4.4 跨线程数据查询 ---
response4 = graph.invoke({
    "messages": [
        "帮我分析一下数据库中北京和哈尔滨城市天气的信息，"
        "做一个详细的对比，并生成出行建议"
    ]
})
print(response4["messages"][-1].content)
'''

with open(base4 + "/01_ReAct代理基础构建.py", "w", encoding="utf-8") as f:
    f.write(py1)
print("Written: 01_ReAct代理基础构建.py")


# ===== Course 4 Python File 2 =====
py2 = '''# -*- coding: utf-8 -*-
"""
【案例 2】LangGraph 事件流与异步处理
============================================

本案例展示 LangGraph 中的流式输出与事件流机制，包括：
- stream / astream 多种模式（values/updates/debug/messages）
- astream_events 获取中间步骤与自定义事件
- Token 级别的流式处理

要点：
1. LangGraph 流式输出四种模式详解
2. astream_events 事件过滤与数据提取
3. AIMessageChunk 的拼接与 ToolMessage 处理
4. 异步环境下的人机交互与中间进度展示
"""

# ============================================================
# 1. 环境配置
# ============================================================
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")


# ============================================================
# 2. 流式输出基础：AIMessageChunk
# ============================================================

# 每个 chunk 都是一个 AIMessageChunk，代表 AIMessage 的一部分
# 消息块在设计上是可加的，可以拼接
chunks = []
async for chunk in llm.astream("你好，请你详细的介绍一下你自己。"):
    chunks.append(chunk)
    print(chunk.content, end="|", flush=True)

# 拼接所有 chunk
if len(chunks) >= 5:
    gathered = chunks[0] + chunks[1] + chunks[2] + chunks[3] + chunks[4]
    print("\\n拼 接 结 果：", gathered.content)


# ============================================================
# 3. LangGraph 流式输出模式
# ============================================================
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessageChunk, HumanMessage

# graph = create_react_agent(llm, tools=tools)

# --- 3.1 stream_mode="values"：流式传输状态的完整值 ---
def print_stream_values(stream):
    for sub_stream in stream:
        message = sub_stream["messages"][-1]
        message.pretty_print()

input_message = {"messages": ["你好，南京现在的天气怎么样？"]}
print_stream_values(graph.stream(input_message, stream_mode="values"))


# --- 3.2 stream_mode="updates"：流式传输每个步骤后的状态更新 ---
def print_stream_updates(stream):
    for sub_stream in stream:
        print(sub_stream)

input_message2 = {"messages": ["你好，天津、内蒙现在的天气怎么样？"]}
print_stream_updates(graph.stream(input_message2, stream_mode="updates"))


# --- 3.3 stream_mode="debug"：流式传输尽可能多的调试信息 ---
def print_stream_debug(stream):
    for sub_stream in stream:
        print(sub_stream)

input_message3 = {"messages": ["你好，乌鲁木齐的天气怎么样？"]}
print_stream_debug(graph.stream(input_message3, stream_mode="debug"))


# ============================================================
# 4. 异步流式输出（astream）
# ============================================================

# --- 4.1 获取最终结果（仅保留最后值） ---
async for chunk in graph.astream(
    input={"messages": ["你好，四川的天气怎么样？"]},
    stream_mode="values"
):
    final_result = chunk

final_result["messages"][-1].pretty_print()


# --- 4.2 查看每个节点的更新 ---
inputs = {"messages": [("human", "你好，乌鲁木齐的天气怎么样？")]}
async for chunk in graph.astream(inputs, stream_mode="updates"):
    for node, values in chunk.items():
        print(f"接收到的更新节点: \\'{node}\\'")
        print(values)
        print()


# --- 4.3 stream_mode="messages"：Token 级别的流式输出 ---
first = True
async for msg, metadata in graph.astream(
    {"messages": ["你好，帮我查询一下数据库中都有哪些城市的天气数据"]},
    stream_mode="messages"
):
    if msg.content and not isinstance(msg, HumanMessage):
        print(msg.content, end="|", flush=True)

    if isinstance(msg, AIMessageChunk):
        if first:
            gathered = msg
            first = False
        else:
            gathered = gathered + msg

        if msg.tool_call_chunks:
            print(gathered.tool_calls)


# ============================================================
# 5. 事件流（astream_events）
# ============================================================

# --- 5.1 打印所有事件的 event 和 name ---
async for event in graph.astream_events(
    {"messages": ["你好，请你介绍一下你自己"]},
    version="v2"
):
    kind = event["event"]
    print(f"{kind}: {event['name']}")


# --- 5.2 捕获所有事件到列表 ---
events = []
async for event in graph.astream_events(
    {"messages": ["你好，请你介绍一下你自己"]},
    version="v2"
):
    events.append(event)

print("事件总数:", len(events))
print("事件[0]:", events[0])


# --- 5.3 按 event 类型过滤：仅保留聊天模型的流式输出 ---
async for event in graph.astream_events(
    {"messages": ["你好，请你介绍一下你自己"]},
    version="v2"
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event, end="|")


# --- 5.4 提取 AIMessageChunk 的 content（Token 级别） ---
async for event in graph.astream_events(
    {"messages": ["你好，请你介绍一下你自己"]},
    version="v2"
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="|")


# ============================================================
# 6. 事件流处理流程说明
# ============================================================
"""
LangGraph astream_events 完整流程：
1. on_chain_start: LangGraph 写入 __start__ 节点
2. on_chain_start: call_model 节点启动
3. on_chat_model_start: ChatOpenAI 开始调用
4. on_chat_model_stream: 按 Token 增量流式返回
5. on_chat_model_end: ChatOpenAI 输出完全部内容后停止
6. ChannelWrite<call_model,messages>: 将结果写回通道
7. 回到 call_model 节点做决策
8. 最终完成整个图的运行流程

事件结构：
- event: 正在发出的事件类型
- name: 事件的名称
- data: 与事件关联的数据（on_chat_model_stream 中为 AIMessageChunk）
"""
'''

with open(base4 + "/02_LangGraph事件流处理.py", "w", encoding="utf-8") as f:
    f.write(py2)
print("Written: 02_LangGraph事件流处理.py")

print("Course 4 Python files done")
