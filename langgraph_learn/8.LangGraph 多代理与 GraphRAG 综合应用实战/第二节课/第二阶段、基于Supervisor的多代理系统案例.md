## <center>第二阶段、基于Supervisor的多代理系统案例</center>

&emsp;&emsp;这里我们使用上节课程中构建的两个子代理数据库管理员`db_agent`和数据分析师`code_agent`，前者根据用户的需求操作数据库，提取出核心的数据信息，后者根据`db_agent`传递过来的数据生成对应的代码，并在本地的`Python`解释器进行自动化的数据分析，并生成可视化图表。同时保留大模型交互的`Chat`节点。添加`supervisor`进行统一管理。

- **Step 1. 定义工具**

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
    employee_id = Column(Integer)
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
DATABASE_URI = 'mysql+pymysql://root:snowball950123@192.168.110.131/langgraph_agent?charset=utf8mb4'
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
```

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
        session.close()
```

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
    return result_str
```

&emsp;&emsp;使用 `create_react_agent` 构建成两个`ReAct`代理。

```python
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
```

```python
db_agent = create_react_agent(
    llm,
    tools=[add_sale, delete_sale, update_sale, query_sales],
    state_modifier="You use to perform database operations while should provide accurate data for the code_generator to use"
)
```

```python
code_agent = create_react_agent(
    llm,
    tools=[python_repl],
    state_modifier="Run python code to display diagrams or output execution results"
)
```

&emsp;&emsp;然后分别将两个`ReAct Agent` 构造成节点，并添加代理名称标识。

```python
def db_node(state: AgentState):
    result = db_agent.invoke(state)
    return {
        "messages": [
            HumanMessage(content=result["messages"][-1].content, name="sqler")
        ]
    }


def code_node(state: AgentState):
    result = code_agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, name="coder")]
    }
```

&emsp;&emsp;定义父图的状态。

```python
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str
```

&emsp;&emsp;然后去设置代理主管可以管理的子代理， 添加`FINISH`是为了用来标识 任务是否已经全部完成，可以返回最终的结果了。

```python
members = ["chat", "coder", "sqler"]
options = members + ["FINISH"]
```

```python
from typing import Literal
from typing_extensions import TypedDict
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""

    next: Literal[*options]
```

```python
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

def supervisor(state: AgentState):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- chat: Responds directly to user inputs using natural language.\n"
        "Given the following user request, respond with the worker to act next."
        " Each worker will perform a task and respond with their results and status."
        " When finished, respond with FINISH."
    )

    messages = [{"role": "system", "content": system_prompt},] + state["messages"]

    response = llm.with_structured_output(Router).invoke(messages)
    next_ = response["next"]
    if next_ == "FINISH":
        next_ = END
    return {"next": next_}
```

&emsp;&emsp;接下来正常构建`Chat`子代理，通过`Node`的形式来定义。

```python
def chat(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chatbot")]
    return {"messages": final_response}


builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("coder", code_node)
builder.add_node("sqler", db_node)

for member in members:
    # 每个子代理在完成工作后总是向主管"汇报"
    builder.add_edge(member, "supervisor")

builder.add_conditional_edges("supervisor", lambda state: state["next"])

builder.add_edge(START, "supervisor")

graph = builder.compile()
```

&emsp;&emsp;可视化完整的图结构：

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

&emsp;&emsp;接下来进行问答测试：

```python
for chunk in graph.stream({"messages": "帮我查询前3个销售记录的具体信息"}, stream_mode="values"):
    print(chunk)
```

```python
for chunk in graph.stream({"messages": "帮我根据前10名的销售记录id，生成对应的销售额柱状图"}, stream_mode="values"):
    print(chunk)
```

```python
for chunk in graph.stream({"messages": "你好，请你介绍一下你自己"}, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

```python
for chunk in graph.stream({"messages": "帮我删除 第 33条销售数据"}, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

&emsp;&emsp;`LangGraph`中构建`supervisor`很高效，代理监督和 `StateGraph`的构架方式可以极大简化工作流程、优化任务分配并增强多代理系统内的协作。但也存在一些问题。比如大家在后续尝试的过程中会发现经常可以看到主管不断地一次又一次地将一个代理的输出发送给自己，开始自言自语，这就会导致更高的运行时间和更高的`Token`消耗，同时，在决策方向选择其他代理人而不是首选代理人，从而导致幻觉。这些都是我们在自己应用的时候，结合具体的业务逻辑，以及所使用的大模型的原生能力进行针对性的调整。

&emsp;&emsp;而至于`supervisor`的变体 `Supervisor (tool-calling)` 和 `Hierarchical`，不过是以不同的方式对`supervisor`进行嵌套应用，可以更模块化、规范化代理的处理构建更庞大的`Agent`集群，但带来的问题同时也是更高的`Token`和更缓慢的处理速度，就目前` AI Agent`的发展阶段来说，所应用的范畴还是较少。如果感兴趣可以在如下官网进一步了解，课程中不做重复的说明。[LangGraph Hierarchical Agent](https://langchain-ai.github.io/langgraph/concepts/multi_agent/#hierarchical)

## 拓展思考

### 1. 深度概念

&emsp;&emsp;**Supervisor架构在实际应用中的常见问题及解决方案？**

&emsp;&emsp;在实际应用中，Supervisor架构可能会遇到以下问题：
- **自言自语问题**：Supervisor反复将代理输出发送给自己，导致高延迟和高Token消耗
- **路由选择错误**：Supervisor可能选择错误的代理
- **幻觉问题**：Supervisor产生错误的决策

&emsp;&emsp;解决方案：
- 添加适当的提示工程，优化Supervisor的决策质量
- 设置最大迭代次数，防止无限循环
- 使用更强大的模型作为Supervisor

&emsp;&emsp;**如何优化Supervisor的决策质量？**

&emsp;&emsp;优化Supervisor决策的方法：
1. 清晰的系统提示明确定义每个代理的角色
2. 提供具体的决策示例
3. 使用结构化输出确保响应格式正确
4. 添加决策历史上下文帮助Supervisor理解任务进展
