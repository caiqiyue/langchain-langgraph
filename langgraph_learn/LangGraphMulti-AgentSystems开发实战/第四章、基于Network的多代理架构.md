# 4. 基于 Network （网络）的多代理架构

&emsp;&emsp;`Single-Agent`可以在单个图结构运行工具，但即使使用像 `gpt-4` 这样的强大模型，当工具特别多的时候也会经常出现问题。处理复杂任务的一种方法是通过 “分而治之” 的方法：为每个任务或领域创建一个专门的代理，并将任务路由到正确的 “专家”。这是多代理网络架构的一个核心思想。那对于`NetWork`（网络）代理来说，它的架构是：**每个代理都可以与其他代理通信，且任何代理都可以决定接下来要呼叫哪个其他代理。** 正如下图所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411111121494.png" width=100%></div>

```python
# pip install -U langchain langchain_openai langsmith pandas langchain_experimental matplotlib langgraph langchain_core```

&emsp;&emsp;接下来，我们尝试用上图中的网络架构去构建多代理系统。我们选择一个`商业智能（BI）`用于数据分析的落地场景的案例。商业智能（BI）应用于各种行业的数据分析过程，它主要是通过将数据转换为有价值的洞察力，帮助企业做出更好的决策，比如销售和市场分析、客户关系管理（CRM）、库存管理、财务分析等等。这些场景在不同行业的具体应用可能有所差异，但核心都是通过数据分析来提高效率、降低成本、增强客户满意度和优化决策过程。

&emsp;&emsp;这里我们就尝试来实现一个`销售和市场分析`场景的简化案例。完整设计思路及构建流程如下：

- **Stage 1. 定义大模型实例**

&emsp;&emsp;我们使用 `gpt-4o-mini` 作为数据库管理员`db_agent`, 根据用户的需求操作数据库，提取出核心的数据信息。 使用最新开源的`Qwen 2.5-Coder:32b`模型作为数据分析师`code_agent`，根据`db_agent`传递过来的数据生成对应的代码，并在本地的`Python`解释器进行自动化的数据分析，并生成可视化图表。

&emsp;&emsp;首先来接入 `gpt-4o-mini` 模型，代码如下：

```python
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

db_llm = ChatOpenAI(model="gpt-4o-mini")```

&emsp;&emsp;测试一下 `gpt-4o-mini` 模型的连通性，如下：

```python
print(db_llm.invoke("你好,测试连通性。").content)```

&emsp;&emsp;如果能够成功收到回复，则说明`gpt-4o-mini`模型服务正常。接下来，我们使用`Ollama`启动刚刚开源的`Qwen-2.5-Coder：32`模型，用来生成代码。

> 关于如何使用`Ollama`启动大模型的详细教程，请查看开源大模型模块。

&emsp;&emsp;这里我们使用`LangChain`来进行接入。

```python
# ! pip install  langchain-ollama```

```python
from langchain_ollama import ChatOllama

coder_llm = ChatOllama(
    base_url = "http://192.168.110.131:11434",  # 注意：这里需要替换成自己本地启动的endpoint
    model="qwen2.5-coder:32b",
)```

&emsp;&emsp;测试一下 `qwen2.5-coder:0.5b` 模型的连通性，代码如下：

```python
from langchain_core.messages import AIMessage


print(coder_llm.invoke("帮我写一个使用Python实现的贪吃蛇的游戏代码").content)```

- **Stage 2：定义工具**

&emsp;&emsp;这里我们为`db_agent`配置的能力是操作数据库权限，以下是我们即将构建的数据模型（`SalesData`, `CustomerInformation`, `ProductInformation`, `CompetitorAnalysis`）表的描述，用来构成销售和市场分析核心数据的存储。如下所示：

&emsp;&emsp;SalesData 表：

| 字段名       | 类型      | 描述                             |
|------------|---------|----------------------------------|
| sales_id   | Integer | 销售记录的唯一标识符（主键）            |
| product_id | Integer | 产品ID，与产品信息表关联（外键）          |
| employee_id| Integer | 员工ID，假设已有员工表（此例未创建员工表） |
| customer_id| Integer | 客户ID，与客户信息表关联（外键）          |
| sale_date  | String  | 销售日期                           |
| quantity   | Integer | 销售数量                           |
| amount     | Float   | 销售额（总金额）                     |
| discount   | Float   | 折扣率                             |

&emsp;&emsp;CustomerInformation 表：

| 字段名         | 类型      | 描述           |
|--------------|---------|----------------|
| customer_id  | Integer | 客户的唯一标识符（主键） |
| customer_name| String  | 客户姓名         |
| contact_info | String  | 客户联系方式     |
| region       | String  | 客户所在地区     |
| customer_type| String  | 客户类别         |

&emsp;&emsp;ProductInformation 表：

| 字段名      | 类型      | 描述               |
|-----------|---------|--------------------|
| product_id| Integer | 产品的唯一标识符（主键） |
| product_name| String | 产品名称           |
| category  | String  | 产品类别           |
| unit_price| Float   | 单位价格           |
| stock_level| Integer| 库存水平           |

&emsp;&emsp;CompetitorAnalysis 表：

| 字段名         | 类型      | 描述           |
|--------------|---------|----------------|
| competitor_id| Integer | 竞争对手的唯一标识符（主键） |
| competitor_name| String | 竞争对手名称   |
| region       | String  | 竞争对手所在地区 |
| market_share | Float   | 市场份额       |

&emsp;&emsp;使用如下代码进行表结构的创建：

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from faker import Faker
import random

# 创建基类
Base = declarative_base()

# 定义模型
class SalesData(Base):
    __tablename__ = 'sales_data'
    sales_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product_information.product_id'))
    employee_id = Column(Integer)  # 示例简化，未创建员工表
    customer_id = Column(Integer, ForeignKey('customer_information.customer_id'))
    sale_date = Column(String(50))
    quantity = Column(Integer)
    amount = Column(Float)
    discount = Column(Float)

class CustomerInformation(Base):
    __tablename__ = 'customer_information'
    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(50))
    contact_info = Column(String(50))
    region = Column(String(50))
    customer_type = Column(String(50))

class ProductInformation(Base):
    __tablename__ = 'product_information'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(50))
    category = Column(String(50))
    unit_price = Column(Float)
    stock_level = Column(Integer)

class CompetitorAnalysis(Base):
    __tablename__ = 'competitor_analysis'
    competitor_id = Column(Integer, primary_key=True)
    competitor_name = Column(String(50))
    region = Column(String(50))
    market_share = Column(Float)

# 数据库连接和表创建
DATABASE_URI = 'mysql+pymysql://root:snowball950123@192.168.110.131/langgraph_agent?charset=utf8mb4'     # 这里要替换成自己的数据库连接串
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)```

&emsp;&emsp;创建完成后，可以使用可视化工具进行验证，我这里使用`Navicat`：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411151517135.png" width=100%></div>

&emsp;&emsp;接下来，创建模拟数据。我们使用 `Python` 的 `faker` 库来生成模拟数据，并构建插入数据的代码。（faker 是一个 Python 库，用于创建假数据，非常适合在开发和测试阶段填充数据库。）

```python
# ! pip install faker```

```python
# 插入模拟数据
Session = sessionmaker(bind=engine)
session = Session()

fake = Faker()

# 生成客户信息
for _ in range(50):  # 生成50个客户
    customer = CustomerInformation(
        customer_name=fake.name(),
        contact_info=fake.phone_number(),
        region=fake.state(),  # 地区
        customer_type=random.choice(['Retail', 'Wholesale'])  # 零售、批发
    )
    session.add(customer)

# 生成产品信息
for _ in range(20):  # 生成20种产品
    product = ProductInformation(
        product_name=fake.word(),
        category=random.choice(['Electronics', 'Clothing', 'Furniture', 'Food', 'Toys']),  # 电子设备，衣服，家具，食品，玩具
        unit_price=random.uniform(10.0, 1000.0),
        stock_level=random.randint(10, 100)  # 库存
    )
    session.add(product)

# 生成竞争对手信息
for _ in range(10):  # 生成10个竞争对手
    competitor = CompetitorAnalysis(
        competitor_name=fake.company(),
        region=fake.state(),
        market_share=random.uniform(0.01, 0.2)  # 市场占有率
    )
    session.add(competitor)

# 提交事务
session.commit()

# 生成销售数据，假设有100条销售记录
for _ in range(100):
    sale = SalesData(
        product_id=random.randint(1, 20),
        employee_id=random.randint(1, 10),  # 员工ID范围
        customer_id=random.randint(1, 50),
        sale_date=fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
        quantity=random.randint(1, 10),
        amount=random.uniform(50.0, 5000.0),
        discount=random.uniform(0.0, 0.15)
    )
    session.add(sale)

session.commit()

# 关闭会话
session.close()```

&emsp;&emsp;执行结束后，可以进行数据验证，如下所示：

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411151542873.png" width=100%></div>

&emsp;&emsp;准备好数据以后，接下来给`db_agent`配置工具用来执行数据的增删改查操作，具体如下：

```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Union, Optional

class AddSaleSchema(BaseModel):
    product_id: int
    employee_id: int
    customer_id: int
    sale_date: str
    quantity: int
    amount: float
    discount: float

class DeleteSaleSchema(BaseModel):
    sales_id: int

class UpdateSaleSchema(BaseModel):
    sales_id: int
    quantity: int
    amount: float

class QuerySalesSchema(BaseModel):
    sales_id: int

# 1. 添加销售数据：
@tool(args_schema=AddSaleSchema)
def add_sale(product_id, employee_id, customer_id, sale_date, quantity, amount, discount):
    """Add sale record to the database."""
    session = Session()
    try:
        new_sale = SalesData(
            product_id=product_id,
            employee_id=employee_id,
            customer_id=customer_id,
            sale_date=sale_date,
            quantity=quantity,
            amount=amount,
            discount=discount
        )
        session.add(new_sale)
        session.commit()
        return {"messages": ["销售记录添加成功。"]}
    except Exception as e:
        return {"messages": [f"添加失败，错误原因：{e}"]}
    finally:
        session.close()

# 2. 删除销售数据
@tool(args_schema=DeleteSaleSchema)
def delete_sale(sales_id):
    """Delete sale record from the database."""
    session = Session()
    try:
        sale_to_delete = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if sale_to_delete:
            session.delete(sale_to_delete)
            session.commit()
            return {"messages": ["销售记录删除成功。"]}
        else:
            return {"messages": [f"未找到销售记录ID：{sales_id}"]}
    except Exception as e:
        return {"messages": [f"删除失败，错误原因：{e}"]}
    finally:
        session.close()

# 3. 修改销售数据
@tool(args_schema=UpdateSaleSchema)
def update_sale(sales_id, quantity, amount):
    """Update sale record in the database."""
    session = Session()
    try:
        sale_to_update = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if sale_to_update:
            sale_to_update.quantity = quantity
            sale_to_update.amount = amount
            session.commit()
            return {"messages": ["销售记录更新成功。"]}
        else:
            return {"messages": [f"未找到销售记录ID：{sales_id}"]}
    except Exception as e:
        return {"messages": [f"更新失败，错误原因：{e}"]}
    finally:
        session.close()

# 4. 查询销售数据
@tool(args_schema=QuerySalesSchema)
def query_sales(sales_id):
    """Query sale record from the database."""
    session = Session()
    try:
        sale_data = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if sale_data:
            return {
                "sales_id": sale_data.sales_id,
                "product_id": sale_data.product_id,
                "employee_id": sale_data.employee_id,
                "customer_id": sale_data.customer_id,
                "sale_date": sale_data.sale_date,
                "quantity": sale_data.quantity,
                "amount": sale_data.amount,
                "discount": sale_data.discount
            }
        else:
            return {"messages": [f"未找到销售记录ID：{sales_id}。"]}
    except Exception as e:
        return {"messages": [f"查询失败，错误原因：{e}"]}
    finally:
        session.close()```

&emsp;&emsp;然后，第二个数据分析师（code_agent）在需要的时候，接收`db_agent`的数据，生成可视化的图表，这里我们给他配置一个本地的`Python`代码解释器。这里我们使用`Python REPL` 工具，它是`LangChian`封装的一个工具，作用是先让大模型生成代码，然后再运行该代码来获取答案，且仅返回打印的内容。使用的方式非常简单，代码如下：

```python
from typing import Annotated
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
import json
repl = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n\`\`\`python\n{code}\n\`\`\`\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )```

&emsp;&emsp;定义工具列表，并使用`ToolNode`进行构建。

```python
from langgraph.prebuilt import ToolNode

# 定义工具列表
tools = [add_sale, delete_sale, update_sale, query_sales, python_repl]
tool_executor = ToolNode(tools)```

- **Stage 3. 创建代理**

&emsp;&emsp;**要通过图状态进行通信，需要将单个代理定义为图节点，在图执行的每个步骤中，代理节点接收图的当前状态，执行代理代码，然后将更新的状态传递给下一个节点。代理节点是共享单个状态架构的**。这里我们定义一个辅助函数`create_agent`，用来帮助我们创建多代理系统中的每一个子代理。每个子代理可以通过`llm`参数定义其使用的大模型，`system_message`用于定义其每个代理独有的背景信息，而`tools`则可以给不同的子代理绑定特有的工具。具体函数代码如下：

```python
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)```

&emsp;&emsp;对应的中文Prompt 解释：
```python
prompt = """
你是一个有帮助的人工智能助手，与其他助手合作。使用提供的工具来推进解答问题的过程。
如果你不能完全回答，没关系，另一个拥有不同工具的助手会接着帮忙。
尽你所能执行任务以取得进展。如果你或其他任何助手得到了最终答案或成果，请在你的回答前加上“最终答案”，以便团队知道可以停止。
你可以使用以下工具：{tool_names}。{system_message}。
"""
```

&emsp;&emsp;然后，我们根据`create_agent`辅助函数依次去创建`db_agent`和`code_agent`两个代理，分别赋予它们不同的身份设定、基座模型和所能使用的工具。

```python
# 数据库管理员
db_agent = create_agent(
    db_llm,
    [add_sale, delete_sale, update_sale, query_sales],
    system_message="You should provide accurate data for the code_generator to use.  and source code shouldn't be the final answer",
)


# 程序员
code_agent = create_agent(
    coder_llm,
    [python_repl],
    system_message="Run python code to display diagrams or output execution results",
)```

```python
db_agent```

&emsp;&emsp;接下来，将`Agent`去定义成节点。如下代码所示：

```python
import functools
from langchain_core.messages import AIMessage

def agent_node(state, agent, name):
    result = agent.invoke(state)
    # 将代理输出转换为适合附加到全局状态的格式
    if isinstance(result, ToolMessage):
        pass
    else:
        # 创建一个 AIMessage 类的新实例，其中包含 result 对象的所有数据（除了 type 和 name），并且设置新实例的 name 属性为特定的值 name。
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # 跟踪发件人，这样我们就知道下一个要传给谁。
        "sender": name,
    }

db_node = functools.partial(agent_node, agent=db_agent, name="db_manager")
code_node = functools.partial(agent_node, agent=code_agent, name="code_generator")```

```python
db_node```

- **Stage 4. 定义 路由**

&emsp;&emsp;在多代理系统中，路由器的功能是根据从代理收到的消息确定接下来要执行的流程，用于路由调用工具、结束流程或继续下一步，具体取决于消息的内容和代理做出的决策。如下所示的`router` 函数，将图的当前状态作为输入，从状态中提取消息，重点关注列表中的最后一条消息。如果最后一条消息的附加参数中包含 `tool_calls`，则表示前一个代理调用了工具。在这种情况下，路由器决定继续执行图形中的 `call_tool` 节点。如果最后一条消息的内容包括 `FINAL ANSWER`，则表示所有代理都已决定完成工作。在这种情况下，路由器将工作流定向到终端节点，指示进程的终止。如果上述条件均未满足，则路由器将返回 `continue`，指示工作流应继续执行图中的下一步。

```python
# 任何一个代理都可以决定结束
from typing import Literal

def router(state):
    # 这是一个路由
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # 前一个代理正在调用一个工具
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # 任何Agent都决定工作完成
        return END
    return "continue"```

- **Stage 5. 定义状态和图**

&emsp;&emsp;在初始化 `StateGraph` 对象之前，我们首先定义 `AgentState`。`AgentState`定义在图中的节点之间传递的对象的结构。在这里，它包括消息列表和要执行任务的代理名称(sender)。代码如下：

```python
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str```

- **Stage 5. 构建图结构**

&emsp;&emsp;一切准备就绪后，我们在在下面的代码中构建管理多智能体工作流的流程。通过网络代理的多代理架构，它是每一个代理之间都可以构建互相的连接关系，所以我们就需要在定义图结构的时候，将需要进行通行的代理通过条件边来互相建立联系。

```python
from langgraph.graph import END, StateGraph

# 初始化一个状态图
workflow = StateGraph(AgentState)

# 将Agent作为节点进行添加
workflow.add_node("db_manager", db_node)
workflow.add_node("code_generator", code_node)
workflow.add_node("call_tool", tool_executor)

# 通过条件边 构建 子代理之间的通信
workflow.add_conditional_edges(
    "db_manager",
    router,
    {"continue": "code_generator", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "code_generator",
    router,
    {"continue": "db_manager", "call_tool": "call_tool",END: END},
)

workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {
        "db_manager": "db_manager",
        "code_generator": "code_generator",
    },
)

# 设置 db_manager 为初始节点
workflow.set_entry_point("db_manager")

# 编译图
graph = workflow.compile()```

- **Stage 6. 可视化图结构**

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

- **Stage 6. 调用测试**

&emsp;&emsp;完成图表的编译后，我们就可以进行功能测试了。

```python
for chunk in graph.stream(
    {"messages": [HumanMessage(content="根据sales_id使用折线图显示前5名销售的销售总额")]}, 
    {"recursion_limit": 50}, 
    stream_mode='values'):
    print(chunk)```

```python
for chunk in graph.stream(
    {"messages": [HumanMessage(content="帮我删除销售id 是 20 的这名销售信息")]}, 
    {"recursion_limit": 20}, 
    stream_mode='values'):
    print(chunk)```

```python
for chunk in graph.stream(
    {"messages": [HumanMessage(content="帮我根据前10名的 销售记录id，生成对应的销售额柱状图")]}, 
    {"recursion_limit": 20}, 
    stream_mode='values'):
    chunk["messages"][-1].pretty_print()```

&emsp;&emsp;在基于网络代理构建的多智能体系统中，每个代理都可以与其他每个代理通信（多对多连接），并可以决定接下来要调用哪个代理。虽然非常灵活，但这个体系结构不能随着代理数量的增加而很好地扩展，比如很难强制执行接下来应该调用哪个代理，很难确定应该在代理之间传递多少信息等多种问题。这是`NetWork`通信方式的优劣势所在。

&emsp;&emsp;除此以外，`LangGraph`中可以构建的`Supervisor`与`Hierarchical`多智能体系统，我们在下节课给大家展开详细的介绍。
