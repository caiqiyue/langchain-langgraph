# <center>第五阶段、LangSmith监控工具

## 一、 LangSmith核心概念详解

&emsp;&emsp;大模型的行为往往存在不确定性，尤其在开发复杂的`AI Agent`应用程序时，过程中常包含众多子步骤。若希望掌握每一步的执行状态与结果，一方面可采用`Debug`方式实现实时控制，另一方面也可借助特定工具来观察和调试中间的交互流程。`Langsmith` 就是为应对这一挑战而设计的工具平台，由 `LangChain` 和 `LangGraph` 的团队创建。其核心目标是赋予LLM应用全面的可观测性，具体通过两大功能支柱实现：**一是提供覆盖全链路的跟踪、日志与实时分析能力；二是构建集成的监控与调试环境，让每一个中间步骤都清晰可见。**

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022164041124.png" width=80%></div>

- **Project** (项目)：蓝色方块代表整个项目，可能是一个单独的应用程序或服务。

- **Traces** (轨迹)：绿色方块代表项目在不同条件或配置下的执行路径。每个轨迹可以是一个特定的用户会话、一个功能的执行，或者应用在特定输入下的行为。

- **Runs** (运行)：每个轨迹下的黄色方块表示特定轨迹的单次执行。这些是执行的实例，每个实例都是轨迹在特定条件下的实际运行。

- **Feedback, Tags, Metadata** (反馈、标签、元数据)：这部分显示了系统如何利用用户或自动化工具生成的反馈、标签和元数据来增强轨迹的管理和过滤。反馈可以用于改进未来的运行，标签和元数据可用于分类和筛选特定的轨迹或运行，以便在LangSmith的用户界面中更容易地管理和审查

### 1. Trace（追踪）

一次完整应用执行的全链路记录，从用户输入到最终输出的整个调用树。它可视化LLM应用的执行路径，帮助开发者快速定位问题。

   * 作用：提供端到端的可见性，捕获所有输入、输出和中间步骤，是调试和性能分析的基础。

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210111225733.png" width=80%></div>

LangSmith可以追踪从用户输入到最终输出的完整流程，只要执行了invoke或者stream方法，就会自动记录一条Trace。包括：

- Agent决策过程

- 工具调用详情

- LLM调用参数和响应

- 检索结果质量

- 执行耗时分析

### 2. Run（运行单元）、Feedback（反馈）、Metadata（元数据）

* Run：Trace中的单个执行节点，每个LLM调用、工具调用或函数执行都会生成一个Run，形成父子关系的树状结构。

  - 作用：记录具体操作细节（如token消耗、延迟、参数）， granular 级别的监控和成本分析。

* Feedback：对单个Run的质量评估，包含标签（如"answer_correctness"）和分数（0-1或分类），可人工标注或自动计算。

  - 作用：构建评估数据集，驱动持续优化。支持在线（实时用户反馈）和离线（批量评估）两种模式。

  - **注意**：LangSmith不会自动生成Feedback，必须由开发者主动在代码中调用API显式创建反馈记录。

* Metadata：附加在Run上的键值对信息（如{"version": "v1.2", "env": "production"}），用于标记运行环境、模型版本等。

  - 作用：支持跨维度筛选、分组分析（如对比不同版本的性能差异）。

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210112202512.png" width=80%></div>


## 二、 LangSmith配置步骤

- **Step 1. 创建一个 LangSmith 帐户**

&emsp;&emsp;要开始使用 `LangSmith`，我们需要创建一个帐户。可以在这里注册一个免费帐户进入`LangSmith`登录页面： https://smith.langchain.com/， 支持使用 Google、GitHub、Discord 和电子邮件登录。


<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241022165215709.png" width=40%></div>

&emsp;&emsp;注册并等登录后，可以直接查看到仪表板：

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210114756767.png" width=85%></div>


&emsp;&emsp;在构建程序跟踪前，首先需要创建一个 `API` 密钥，该密钥将允许我们的项目开始向 `Langsmith` 发送跟踪数据，务必保存好api_key!

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210115234152.png" width=80%></div>


<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210115403568.png" width=80%></div>


&emsp;&emsp;`LangSmith` 支持两种类型的 API 密钥：服务密钥和个人访问令牌。两种类型的令牌都可用于验证对 `LangSmith API` 的请求，但它们有不同的用例。这里选择“密钥类型令牌的个人访问” ，因为我们将使用此密钥作为用户进行个人访问。

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210115758508.png" width=80%></div>


&emsp;&emsp;单击“创建 API 密钥” ，复制并确认已保存。这和`OpenAI`的`API`密钥一样，一旦创建完成，则不允许再次复制。

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210120021074.png" width=60%></div>


<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210120256273.png" width=100%></div>


&emsp;&emsp;现在，就可以将其集成到我们的项目中了。


- **Step 3. 创建环境变量**


&emsp;&emsp;将`LANGCHAIN_API_KEY`替换为我们刚刚创建的 `API` 密钥，或者直接放到.env文件中保存（**推荐**）。


```python
import os

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# 设置LangSmith的API密钥
os.environ["LANGSMITH_API_KEY"] = "REDACTED_TOKEN"

# 设置LangSmith的项目名称
os.environ["LANGSMITH_PROJECT"] = "My_project"


# 验证环境变量是否设置成功
print(os.getenv("LANGCHAIN_TRACING_V2"))
print(os.getenv("LANGSMITH_API_KEY"))
print(os.getenv("LANGSMITH_PROJECT"))```

```python
# 1.导入相关库
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
load_dotenv(override=True)

# 2.导入模型和工具
web_search = TavilySearch(max_results=2)

# 3.创建模型
model = ChatDeepSeek(model="deepseek-chat")

# 4.创建Agent
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="你是一名多才多艺的智能助手，可以调用工具帮助用户解决问题。"
)

# 5.运行Agent获得结果
result = agent.invoke(
    {"messages": [{"role": "user", "content": "请帮我查询2024年诺贝尔物理学奖得主是谁？"}]}
)

print(result['messages'][-1].content)```

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210125640902.png" width=100%></div>


## 5.2 免费Developer Plan容量限制

对于免费的**Developer Plan**，具体的容量限制如下：

- **Trace 额度**：每月 **5,000 条 (5k)** 免费 Base Traces

  - 注：如果绑定了信用卡，超过5000条后不会停止服务，而是自动按 $0.50/1k 条收费；未绑定信用卡则会停止接收新数据

- **数据保留期 (Retention)**：默认为 **14天**

  - 14天前的运行日志会被自动清除，除非手动将其添加到Dataset（数据集）中

- **并发/速率限制**：

  - 每小时最多接收 **500MB** 的数据包或 **50,000** 个事件，防止滥用

- **席位限制**：仅限 **1** 个用户（不能邀请团队成员）

具体费用查看，还是先进入到**settings**设置中，然后点击**Billing and usage**来进行查看

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251210102407004.png" width=80%></div>


```python
```
