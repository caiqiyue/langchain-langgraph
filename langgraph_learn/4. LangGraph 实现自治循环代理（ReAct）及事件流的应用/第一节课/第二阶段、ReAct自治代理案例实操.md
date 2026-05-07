## <center>第二阶段、ReAct自治代理案例实操</center>

### 1. 案例需求分析

&emsp;&emsp;在这个案例中，我们将通过一个多工具场景需求来测试 `LangGraph` 中 `ReAct` 代理的构建方法和效果。

&emsp;&emsp;我们设计了几个工具：
1. **get_weather**：根据城市名称实时获取当前天气信息
2. **insert_weather_to_db**：将查询到的天气数据保存到本地数据库
3. **query_weather_from_db**：基于本地数据库中的天气数据进行提问
4. **fetch_real_time_info**：实时联网检索

### 2. LangSmith配置（可选）

&emsp;&emsp;首先设置`LangSmith`的配置，用于追踪和可视化`ReAct`的中间过程：

```python
import os

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "langGraph_ReAct"
```

### 3. 天气查询工具定义

&emsp;&emsp;接入实时天气数据查询的在线API：

```python
import requests
import json

def get_weather(loc):
    """
    Function to query current weather.
    :param loc: Required parameter, of type string, representing the specific city name
    :return: The result of the OpenWeather API query for current weather
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": loc,
        "appid": "your-api-key",
        "units": "metric",
        "lang": "zh_cn"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return json.dumps(data)
```

### 4. 数据库操作工具定义

&emsp;&emsp;使用`LangChain`的`tool` 装饰器将普通的函数注册为`LangGraph`中支持的工具服务：

```python
from langchain_core.tools import tool
from typing import Union, Optional
from pydantic import BaseModel, Field

# 天气信息Schema
class WeatherInfo(BaseModel):
    city_id: int = Field(..., description="The unique identifier for the city")
    city_name: str = Field(..., description="The name of the city")
    main_weather: str = Field(..., description="The main weather condition")
    description: str = Field(..., description="A detailed description of the weather")
    temperature: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(..., description="Feels-like temperature in Celsius")
    temp_min: float = Field(..., description="Minimum temperature in Celsius")
    temp_max: float = Field(..., description="Maximum temperature in Celsius")

class QueryWeatherSchema(BaseModel):
    city_name: str = Field(..., description="The name of the city to query weather information")

@tool(args_schema=WeatherInfo)
def insert_weather_to_db(city_id, city_name, main_weather, description, temperature, feels_like, temp_min, temp_max):
    """Insert weather information into the database."""
    # 实现代码...

@tool(args_schema=QueryWeatherSchema)
def query_weather_from_db(city_name: str):
    """Query weather information from the database by city name."""
    # 实现代码...
```

### 5. 创建ReAct代理

&emsp;&emsp;准备好工具后，通过`create_react_agent`创建自治循环代理：

```python
from langgraph.prebuilt import create_react_agent
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# 工具列表
tools = [fetch_real_time_info, get_weather, insert_weather_to_db, query_weather_from_db]

# 创建ReAct代理
graph = create_react_agent(llm, tools=tools)
```

### 6. 测试结果

&emsp;&emsp;完成图的编译后，便可以开始进行功能测试：

```python
# 测试1: 普通对话
finan_response = graph.invoke({"messages": ["你好，请你介绍一下你自己"]})
print(finan_response["messages"][-1].content)

# 测试2: 单工具调用
finan_response = graph.invoke({"messages": ["北京今天的天气怎么样？"]})
print(finan_response["messages"][-1].content)

# 测试3: 多工具顺序调用
finan_response = graph.invoke({"messages": [
    "帮我查一下北京、上海，哈尔滨三个城市的天气，告诉我哪个城市最适合出游。同时，把查询到的数据存储到数据库中"
]})
print(finan_response["messages"][-1].content)

# 测试4: 数据库查询
finan_response = graph.invoke({"messages": [
    "帮我分析一下数据库中北京和哈尔滨城市天气的信息，做一个详细的对比，并生成出行建议"
]})
print(finan_response["messages"][-1].content)
```

### 7. 拓展思考

#### 7.1 ReAct代理的自主循环机制

&emsp;&emsp;通过对不同复杂程度输入问题的测试，我们发现ReAct代理能够非常准确且快速地完成任务目标。在涉及多个任务的顺序执行时，`ReAct` 代理能够自主决策并执行，真正实现了完全的自治循环代理。

&emsp;&emsp;其循环机制的核心在于：大模型在每次工具调用后，都会重新"思考"是否还需要继续调用工具。如果用户的最终目标尚未达成，代理会自动选择下一个合适的工具继续执行。

#### 7.2 可扩展性设计

&emsp;&emsp;对于不同的业务需求：
- **模型可替换**：可使用其他开源或在线模型作为 `ReAct` 的基础模型
- **工具易添加**：只需明确定义每个工具的输入和输出，然后通过工具列表的形式直接注册

&emsp;&emsp;这种设计使得ReAct代理在快速构建智能代理方面非常值得尝试。