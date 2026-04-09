# 2. 案例实操：构建复杂工具应用的ReAct自治代理

&emsp;&emsp;在这个案例中，我们将通过一个多工具场景需求来测试 `LangGraph` 中 `ReAct` 代理的构建方法和效果。我们设计了几个工具，以实现实时数据的查询和管理。首先，用户可以通过一个工具根据城市名称实时获取当前天气信息。接着，如果用户希望将查询到的天气数据保存到本地数据库中，可以使用另一个工具完成数据的插入操作。此外，我们还提供了一个工具，允许用户基于本地数据库中的天气数据进行提问数据进行提问。通过这些工具的组合，我们能够快速验证如何在复杂的应用场景中有效地整合不同功能，并实际的感知`LangGraph`框架下`ReAct`代理模式带来的开发便捷性和可扩展性。

&emsp;&emsp;首先，我们设置一下`LangSmith`的配置，用于追踪和可视化`ReAct`的中间过程。这里新建了一个项目，命名为`langGraph_ReAct`，导入基础配置的代码如下图所示：

> LangSmith：https://www.langchain.com/langsmith

```python
import os

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "REDACTED_TOKEN"  # 需要更改为自己的 langsmith API_KEY
os.environ["LANGCHAIN_PROJECT"]="langGraph_ReAct"          # 需要更改为自己实际创建的项目名称

# 验证环境变量是否设置成功
print(os.getenv("LANGCHAIN_TRACING_V2"))
print(os.getenv("LANGCHAIN_API_KEY"))
print(os.getenv("LANGCHAIN_PROJECT"))```

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241029162049660.png" width=100%></div>

&emsp;&emsp;首先，我们接入实时天气数据查询的在线API，代码定义如下：

> OpenWeather API的注册与使用，请参考赠送课程的大模型技术实战部分 - 《Ch.10 借助Function calling调用外部工具API方法》

```python
import requests

def get_weather(loc):
    """
    Function to query current weather.
    :param loc: Required parameter, of type string, representing the specific city name for the weather query. \
    Note that for cities in China, the corresponding English city name should be used. For example, to query the weather for Beijing, \
    the loc parameter should be input as 'Beijing'.
    :return: The result of the OpenWeather API query for current weather, with the specific URL request address being: https://api.openweathermap.org/data/2.5/weather. \
    The return type is a JSON-formatted object after parsing, represented as a string, containing all important weather information.
    """
    # Step 1.构建请求
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Step 2.设置查询参数
    params = {
        "q": loc,               
        "appid": "7b34ea15a881668d4255910e5899920c",    # 输入API key
        "units": "metric",            # 使用摄氏度而不是华氏度
        "lang":"zh_cn"                # 输出语言为简体中文
    }

    # Step 3.发送GET请求
    response = requests.get(url, params=params)
    
    # Step 4.解析响应
    data = response.json()
    return json.dumps(data)```

&emsp;&emsp;测试一下`get_weather`函数的有效性，正常情况下可以得到输入城市名的实时天气信息。测试代码如下所示：

```python
get_weather('beijing')```

&emsp;&emsp;从返回的结果是`Json`数据类型，包含了非常丰富的实时天气数据，如天气条件、温度、湿度、风速、天气描述等信息，这里我们选择一些重要的数据参数进行存储操作（存储至Mysql数据库中）。提取的参数如下：

| 字段名称      | 描述                       |
|---------------|----------------------------|
| city_id       | 城市的唯一标识符           |
| city_name     | 城市名称                   |
| main_weather  | 主要天气状况               |
| description   | 天气的详细描述             |
| temperature    | 当前温度                   |
| feels_like    | 体感温度                   |
| temp_min      | 最低温度                   |
| temp_max      | 最高温度                  |


&emsp;&emsp;接下来，设计一个用于存储实时天气信息的表。这里我们定义一个新的模型 `Weather`，并包括上述所提取出来的的字段。连接 `Mysql`数据库及创建表的代码如下所示：

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# 创建基类
Base = declarative_base()

# 定义 WeatherInfo 模型
class Weather(Base):
    __tablename__ = 'weather'
    city_id = Column(Integer, primary_key=True)  # 城市ID
    city_name = Column(String(50))                # 城市名称
    main_weather = Column(String(50))             # 主要天气状况
    description = Column(String(100))              # 描述
    temperature = Column(Float)                    # 温度
    feels_like = Column(Float)                    # 体感温度
    temp_min = Column(Float)                      # 最低温度
    temp_max = Column(Float)                      # 最高温度


# 数据库连接 URI，这里要替换成自己的Mysql 连接信息，以下是各个字段的对应解释：
# root：MySQL 数据库的用户名。
# snowball950123：MySQL 数据库的密码。
# 192.168.110.131：MySQL 服务器的 IP 地址。
# langgraph_agent：要连接的数据库的名称。
# charset=utf8mb4：设置数据库的字符集为 utf8mb4，支持更广泛的 Unicode 字符
DATABASE_URI = 'mysql+pymysql://root:snowball950123@192.168.110.131/langgraph_agent?charset=utf8mb4'    
engine = create_engine(DATABASE_URI)

# 如果表不存在，则创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)```

&emsp;&emsp;接下来，使用`LangChain`的`tool` 装饰器将普通的函数注册为`LangGraph`中支持的工具服务，根据需求的设计，我们要依次创建三个外部函数，分别是：
1. `get_weather`工具：用于根据城市名称实时查询该城市的当前天气数据。
2. `insert_weather_to_db`工具：如果用户想要把查询到的天气数据插入到数据库的表中，则使用此函数完成数据库的插入操作。
3. `query_weather_from_db`工具：如果用户想基于本地数据库的天气数据直接进行提问，则使用此函数完成数据库的查询操作。

&emsp;&emsp;如上节课实践的流程一样，我们依然使用`pydantic`来做工具的参数校验和结构化输出。三个工具函数的定义代码依次如下所示：

```python
from langchain_core.tools import tool
from typing import Union, Optional
from pydantic import BaseModel, Field
import requests

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


@tool(args_schema=WeatherInfo)
def insert_weather_to_db(city_id, city_name, main_weather, description, temperature, feels_like, temp_min, temp_max):
    """Insert weather information into the database."""
    session = Session()  # 确保为每次操作创建新的会话
    try:
        # 创建天气实例
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
        # 使用 merge 方法来插入或更新（如果已有记录则更新）
        session.merge(weather)
        # 提交事务
        session.commit()
        return {"messages": [f"天气数据已成功存储至Mysql数据库。"]}
    except Exception as e:
        session.rollback()  # 出错时回滚
        return {"messages": [f"数据存储失败，错误原因：{e}"]}
    finally:
        session.close()  # 关闭会话


@tool(args_schema=QueryWeatherSchema)
def query_weather_from_db(city_name: str):
    """Query weather information from the database by city name."""
    session = Session()
    try:
        # 查询天气数据
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
        session.close()  # 关闭会话```

&emsp;&emsp;然后，定义实时联网检索外部工具，通过该函数获取最新的网络数据信息。

```python
class SearchQuery(BaseModel):
    query: str = Field(description="Questions for networking queries")


@tool(args_schema = SearchQuery)
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": query,
      "num": 1,
    })
    headers = {
      'X-API-KEY': 'cd872fca99047eb9165242365c65b858bc8970c0',
      'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)  # 将返回的JSON字符串转换为字典
    if 'organic' in data:
        return json.dumps(data['organic'],  ensure_ascii=False)  # 返回'organic'部分的JSON字符串
    else:
        return json.dumps({"error": "No organic results found"},  ensure_ascii=False)  # 如果没有'organic'键，返回错误信息```

&emsp;&emsp;然后把所有定义的工具存储在一个列表中，如下代码所示：

```python
tools = [fetch_real_time_info, get_weather, insert_weather_to_db, query_weather_from_db]```

```python
tools```

&emsp;&emsp;准备好工具后，接下来定义用于构建`AI Agent`的大模型实例，这里我们使用`OpenAI`的在线`GPT-4`模型。代码如下：

```python
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


llm = ChatOpenAI(model="gpt-4o")```

&emsp;&emsp;当有了工具列表和模型后，就可以通过`create_react_agent`这个`LangGraph`框架中预构建的方法来创建自治循环代理（ReAct）的工作流，其必要的参数如下：

- model： 支持工具调用的LangChain聊天模型。
- tools： 工具列表、ToolExecutor 或 ToolNode 实例。
- state_schema：图的状态模式。必须有`messages`和`is_last_step`键。默认为定义这两个键的`Agent State`。

&emsp;&emsp;上述三点我们均在前面的课程中详细且作为重点介绍过，大家应该是比较容易理解的。所以，创建`ReAct`代理的代码就如下所示：

```python
from langgraph.prebuilt import create_react_agent

graph = create_react_agent(llm, tools=tools)```

```python
graph```

&emsp;&emsp;我们可以逐步的分析和解释一下这一行代码中涉及的图构建过程：

- **Step 1. 定义图状态模式**

&emsp;&emsp;`LangGraph`中的主要图类型是`StateGraph`。每个节点通过`State`中的参数获取有效信息，执行完节点的内部逻辑后，更新该`State`状态中的值。不同的状态模式，可以通过注释设置状态的特定属性（例如覆盖现有值）或添加到现有属性。伪代码如下：

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
```

- **Step 2. 定义`Router Function`**

&emsp;&emsp;设置边缘条件，有条件的原因是，根据节点的输出，可以采用多个路径之一。在该节点运行之前，所采用的路径是未知的（由大模型决定）。
- 条件边缘：调用代理后，如果代理说要采取行动，那么应该调用调用工具的函数。如果代理说已经完成，那么就应该完成。
- 正常边：调用工具后，它应该始终返回给代理来决定下一步做什么。

&emsp;&emsp;伪代码如下：

```python
# 定义决定是否继续执行任务的路由函数
def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    # 如果不是工具调用，则结束
    if not last_message.tool_calls:
        return END
    # 如果是的话，则进入工具库中选择函数执行
    else:
        return "tools"
```

- **Step 3. 定义大模型的交互函数**

&emsp;&emsp;接下来需要通过一个节点函数加载我想要使用的大模型。它需要满足两个标准：
- 应该与消息一起使用，因为图的状态主要是消息列表（聊天历史记录）。
- 需要与工具调用一起使用，其内部使用的是预构建的ToolNode。

&emsp;&emsp;伪代码如下：

```python
from typing import Literal

from langchain_core.runnables import RunnableConfig

# 定义大模型交互的节点函数
async def call_model(state: State, config: RunnableConfig):
    messages = state["messages"]
    response = await model.ainvoke(messages, config)
    # 将调用大模型后得到的响应，追加到消息列表中
    return {"messages": response}
```

- **Step 4. 构建图结构**

&emsp;&emsp;最后，把上述所有的组件放在一起构建图结构，这与我们手动构建图的方式基本一致，伪代码如下：

```python
from langgraph.graph import END, START, StateGraph

# 定义一个新图
workflow = StateGraph(State)

# 添加两个节点
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# 设置起始节点为 agent
workflow.add_edge(START, "agent")

# 添加条件边 -- > Router Agent
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END],
)

# 添加回调边
workflow.add_edge("tools", "agent")

# 编译图
app = workflow.compile()
```

&emsp;&emsp;理解了上面的`create_react_agent`方法内部的构建原理后，其实就能明白：当通过`create_react_agent(llm, tools=tools)`一行代码的执行，现在得到的已经是一个编译后、可执行的图了。我们可以通过`mermaid`方法来可视化经过`create_react_agent`方法构造出来的图结构，代码如下所示：

```python
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))```

&emsp;&emsp;返回的是编译好的`LangGraph`可运行程序，可直接用于聊天交互。调用方式则和之前使用的方法一样，我们可以依次针对不同复杂程度的需求依次进行提问。首先是测试是否可以不使用工具，直接调用大模型生成响应。

```python
# query="你好，请你介绍一下你自己"
# input_message = {"messages": [HumanMessage(content=query)]}

# 可以自动处理成 HumanMessage 的消息格式
finan_response = graph.invoke({"messages":["你好，请你介绍一下你自己"]})
finan_response```

```python
finan_response["messages"][-1].content```

&emsp;&emsp;加大输入问题的复杂度，接下来我们提问的问题希望它能够自动找到正确的工具函数，基于工具的执行结果作为既定的事实，引导生成最终的回复。

```python
finan_response = graph.invoke({"messages":["北京今天的天气怎么样？"]})

finan_response```

```python
finan_response["messages"][-1].content```

```python
finan_response = graph.invoke({"messages":["北京今天的天气怎么样？"]})

finan_response```

```python
finan_response = graph.invoke({"messages":["你知道 cloud 3.5 发布的 computer use 吗？请用中文回复我"]})

finan_response```

```python
finan_response["messages"][-1].content```

&emsp;&emsp;继续加大问题的难度，我们要在一个问题中涉及多个工具的使用，比如：

```python
finan_response = graph.invoke({"messages":["帮我查一下北京、上海，哈尔滨三个城市的天气，告诉我哪个城市最适合出游。同时，把查询到的数据存储到数据库中"]})

finan_response```

```python
finan_response["messages"][-1].content```

&emsp;&emsp;同时，可以在数据库中查看数据的插入情况：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241029183322973.png" width=100%></div>

```python
finan_response = graph.invoke({"messages":["帮我分析一下数据库中北京和哈尔滨城市天气的信息，做一个详细的对比，并生成出行建议"]})

finan_response```

```python
print(finan_response["messages"][-1].content)```

&emsp;&emsp;通过对不同复杂程度输入问题的测试，我们发现当前架构能够非常准确且快速地完成任务目标。在涉及多个任务的顺序执行时，`ReAct` 代理能够自主决策并执行，真正实现了完全的自治循环代理。此外，其可扩展性也十分出色。**对于不同的业务需求，我们只需调整接入的大模型实例（可使用其他开源或在线模型）作为 `ReAct` 的基础模型。对于工具的配置，也无需特别进行复杂的编排，只需明确定义每个工具的输入和输出，然后通过工具列表的形式直接注册到大模型实例及 `ToolNode` 实例中**。这种方法在快速构建智能代理方面，非常值得大家尝试。
