# <center>第一阶段：Agent 开发的可观测性基石

&emsp;&emsp;在对LangChain 1.0有了一定的基础了解之后，对于开发者来说，还需要进一步了解和掌握LangChain Agent必备的开发者套件。分别是LangChain Agent运行监控框架LangSmith、底层LangGraph图结构可视化与调试框架LangGraph Studio和LangGraph服务部署工具LangGraph Cli。可以说这些开发工具套件，是真正推动LangGraph的企业级应用开发效率大幅提升的关键。同时监控、调试和部署工具，也是全新一代企业级Agent开发框架的必备工具，也是开发者必须要掌握的基础工具。

## 1. LangGraph图结构可视化与调试框架：LangGraph Studio

&emsp;&emsp;**LangGraph Studio** 它是一个本地 Graph 可视化引擎，是一个用于可视化构建、测试、分享和部署智能体流程图的图形化 IDE + 运行平台。专注于实时的状态展示和交互式调试。对于正在开发复杂 Agent 逻辑的工程师来说，能够实时观察每个节点的执行状态、输入输出数据和中间计算结果，这种可视化的调试体验是无价的。langGraph Studio`对于`LangChian Agent`来说，则是比`LangSmith`更加方便和高效的可视化调试工具平台。

`LangGraph Studio` 在本地可视化运行时会自动把调用过程上传到 `LangSmith`；而在 `LangSmith` 网页端查看任何 `Trace` 时，又能一键`Run in Studio`回放整条执行链，所以它是通过统一 `Trace SDK` 与 `LangSmith` 紧密集成。而LangGraph CLI则是构建这个项目的关键

<center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251202190426330.png
" alt="image-20250626130624364" style="zoom: 70%;" />


## 2. LangGraph服务部署工具：LangGraph Cli

&emsp;&emsp;LangGraph CLI 是用于本地启动、调试、测试和托管 LangGraph 智能体图的开发者命令行工具。

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250626131252066.png" alt="image-20250626131252066" style="zoom:50%;" />

| 功能类别               | 命令示例                                                  | 说明                                      |
| ------------------ | ----------------------------------------------------- | --------------------------------------- |
| ✅ 启动 Graph 服务      | `langgraph dev`                                       | 启动 Graph 的开发服务器，供前端（如 Agent Chat UI）调用  |
| 🧪 测试 Graph 输入     | `langgraph run graph:graph --input '{"input": "你好"}'` | 本地 CLI 输入测试，输出结果                        |
| 🧭 管理项目结构          | `langgraph init`                                      | 初始化一个标准 Graph 项目目录结构                    |
| 📦 部署 Graph（未来）    | `langgraph deploy`（预留）                                | 发布 graph 至 LangGraph 云端（已对接 Studio）     |
| 🧱 显示 Assistant 列表 | `langgraph list`                                      | 显示当前 graph 中有哪些 assistant（即 entrypoint） |
| 🔄 重载运行时           | 自动热重载                                                 | 修改 `graph.py` 时，`dev` 模式自动重启生效          |

而一旦应用成功部署上线，LangGraph Cli还会非常贴心的提供后端接口说明文档：

<center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251202191424859.png" alt="image-20250626132044152" style="zoom:70%;" />

而对于LangGraph构建的智能体，除了能够本地部署外，官方也提供了云托管服务，借助LangGraph Platform，开发者可以将构建的智能体 Graph部署到云端，并允许公开访问，同时支持支持长时间运行、文件上传、外部 API 调用、Studio 集成等功能。

### 2.1 创建完整LangGraph智能体项目流程

- **Step 1. 创建一个`LangChain Agent`项目主文件夹**

&emsp;&emsp;我们这里创建一个`LangChain Agent`文件夹，如下图所示：

<center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251202193605261.png" alt="image-20251028174723860" style="zoom:50%;" />

- **Step 2. 创建`requirements.txt`文件**

&emsp;&emsp;在`LangChain Chatbot`文件夹中，新建一个`requirements.txt`文件，里面需要填写在运行该项目时需要安装的依赖项(**注意**：这里的依赖可以根据自己需要的进行增加)，如下所示：

```bash
langchain
langchain-deepseek
langchain-openai
langchain-tavily
python-dotenv
langsmith
pydantic
matplotlib
seaborn
pandas
IPython

```

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20251028174939509.png" alt="image-20251028174939509" style="zoom:50%;" />

- **Step 3. 注册LangSmith（可选）**

&emsp;&emsp;对于企业级的Agent项目，为了更好的监控智能体实时运行情况，我们可以考虑借助LangSmith进行追踪（会将智能体运行情况实时上传到LangGraph官网并进行展示）。

&emsp;&emsp;要开始使用 `LangSmith`，我们需要创建一个帐户。可以在这里注册一个免费帐户进入`LangSmith`登录页面： https://smith.langchain.com/ ， 支持使用 Google、GitHub、Discord 和电子邮件登录。

<center><div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202506151835039.png" width=33%></div>

&emsp;&emsp;注册并等登录后，可以直接查看到仪表板：

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624190009348.png" alt="image-20250624190009348" style="zoom:33%;" />

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624190049558.png" alt="image-20250624190049558" style="zoom:33%;" />

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624190123279.png" alt="image-20250624190123279" style="zoom:33%;" />

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624190228537.png" alt="image-20250624190228537" style="zoom:33%;" />

&emsp;&emsp;在构建程序跟踪前，首先需要创建一个 `API` 密钥，该密钥将允许我们的项目开始向 `Langsmith` 发送跟踪数据。创建完密钥后，在后续配置环境变量环节设置开启追踪、并输入密钥即可接入LangSmith。

- **Step 4. 创建`.env`配置文件**

&emsp;&emsp;在`LangChain Chatbot`文件夹中，新建一个`.env`文件，将敏感信息（如`API`密钥）放在环境变量中而不是硬编码。如下所示：

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20251028175031725.png" alt="image-20251028175031725" style="zoom:40%;" />

这里需要注意的是，如果不设置LangSmith，则无需设置中间三个环境变量，而具体工具也可以根据实际需求进行设置。

- **Step 5. 创建`graph.py`核心文件**

&emsp;&emsp;在`LangChain Agent`文件夹中，新建一个`graph.py`文件，在该文件中编写构建图的具体运行逻辑，如状态、节点、变、图的编译等。此外，在使用LangGraph CLI创建智能体项目时，会自动设置记忆相关内容，并进行持久化记忆存储，无需手动设置。因此此时智能体代码如下所示：

```python
import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from typing_extensions import TypedDict
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests,json

# 加载环境变量
load_dotenv(override=True)

# 内置搜索工具
search_tool = TavilySearch(max_results=5, topic="general")

class WeatherQuery(BaseModel):
    loc: str = Field(description="The location name of the city")

@tool(args_schema = WeatherQuery)
def get_weather(loc):
    """
    查询即时天气函数
    :param loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称，\
    注意，中国的城市需要用对应城市的英文名称代替，例如如果需要查询北京市天气，则loc参数需要输入'Beijing'；
    :return：OpenWeather API查询即时天气的结果，具体URL请求地址为：https://api.openweathermap.org/data/2.5/weather\
    返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """
    # Step 1.构建请求
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Step 2.设置查询参数
    params = {
        "q": loc,
        "appid": os.getenv("OPENWEATHER_API_KEY"),    # 输入API key
        "units": "metric",            # 使用摄氏度而不是华氏度
        "lang":"zh_cn"                # 输出语言为简体中文
    }

    # Step 3.发送GET请求
    response = requests.get(url, params=params)

    # Step 4.解析响应
    data = response.json()
    return json.dumps(data)

tools = [search_tool, get_weather]

# 创建模型
model = ChatDeepSeek(model="deepseek-chat")

prompt = """
你是一名乐于助人的智能助手，擅长根据用户的问题选择合适的工具来查询信息并回答。

当用户的问题涉及**天气信息**时，你应优先调用`get_weather`工具，查询用户指定城市的实时天气，并在回答中总结查询结果。

当用户的问题涉及**新闻、事件、实时动态**时，你应优先调用`search_tool`工具，检索相关的最新信息，并在回答中简要概述。

如果问题既包含天气又包含新闻，请先使用`get_weather`查询天气，再使用`search_tool`查询新闻，最后将结果合并后回复用户。

所有回答应使用**简体中文**，条理清晰、简洁友好。
"""

# 创建图
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt=prompt)
```

这里的代码编写时需要注意，如果需要使用langgraph studio进行可视化调试，则需要注意下面两点：

* 1、使用create_agent创建的对象名称必须是graph，与langgraph.json中后缀定义的名称要一致（graph.py:graph）

* 2、create_agent创建时不可以加checkpointer记忆参数，否则langgraph studio会报错

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624191412113.png" alt="image-20250624191412113" style="zoom:33%;" />

- **Step 6. 创建`langgraph.json`文件**

&emsp;&emsp;在`LangChain Agent`文件夹中，新建一个`langgraph.json`文件，在该`json`文件中配置项目信息，遵循规范如下所示：

- 必须包含 `dependencies` 和 `graphs` 字段
- `graphs` 字段格式："图名": "文件路径:变量名"
- 配置文件必须放在与Python文件同级或更高级的目录

&emsp;&emsp;注意: 项目文件的名称必须为`langgraph.json`。如下所示：

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624191532218.png" alt="image-20250624191532218" style="zoom:33%;" />

```josn
{
  "dependencies": ["./"],
  "graphs": {
    "chatbot": "./graph.py:graph"
  },
  "env": ".env"
}

```

&emsp;&emsp;其中：
- `dependencies`: ["./"] - 告诉`LangGraph`在当前目录查找依赖项（会自动读取`requirements.txt`）
- `chatbot`: "./graph.py:graph" - 定义图名为`chatbot`，来自`graph.py`文件中的`graph`变量
- `env`: ".env" - 指定环境变量文件位置

&emsp;&emsp;最终完整项目结构如下所示：

```json
    ./langraph_chatbot/
    ├── graph.py              # 对应官方的 agent.py
    ├── requirements.txt      # ✅ 依赖管理
    ├── langgraph.json       # ✅ 配置文件
    └── .env                 # ✅ 环境变量
```

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20250624191613003.png" alt="image-20250624191613003" style="zoom:50%;" />

- **Step 7. 安装`langgraph-cli`以及其他依赖**

```python
!pip install -U "langgraph-cli[inmem]"```

&emsp;&emsp;然后，安装`langgraph-cli`依赖，执行如下代码：

```bash
    pip install -U "langgraph-cli[inmem]"
```

```bash
    pip install -r requirements.txt
```

执行`LangGraph dev`即可启动项目

```bash
    langgraph dev
```

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20251028175822701.png" alt="image-20251028175822701" style="zoom:50%;" />


&emsp;&emsp;启动成功后能看到三个连接，其中第一个连接是当前部署完成后的服务端口，第二个是LangGraph Studio的可视化页面，第三个端口是端口说明。这里点击第二个链接进入Langgraph Studio的页面：

<center>

<img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20251028175752261.png" alt="image-20251028175752261" style="zoom:40%;" />

