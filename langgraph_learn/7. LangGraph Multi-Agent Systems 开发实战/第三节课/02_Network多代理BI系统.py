# -*- coding: utf-8 -*-
"""
【案例】基于 Network 的多代理架构实现 BI 数据分析系统
============================================

本案例展示如何使用 LangGraph 实现基于 Network 架构的多代理系统

要点：
1. 使用 Network 架构，每个代理都可以与其他代理通信
2. 数据库管理员(db_agent)负责数据库操作
3. 数据分析师(code_agent)负责生成和执行Python代码
4. 通过条件边实现代理间的动态路由

案例说明：
构建一个销售和市场分析场景的多代理系统：
- db_agent: 接收用户需求，操作数据库提取数据
- code_agent: 接收数据，生成可视化图表
"""

# ============================================================
# Stage 1: 环境配置
# ============================================================
import getpass
import os

# GPT 模型配置
# if not os.environ.get("OPENAI_API_KEY"):
#     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

db_llm = ChatOpenAI(model="gpt-4o-mini")

# Ollama 模型配置（用于代码生成）
# from langchain_ollama import ChatOllama
# coder_llm = ChatOllama(
#     base_url="http://192.168.110.131:11434",
#     model="qwen2.5-coder:32b",
# )

# ============================================================
# Stage 2: 数据库模型定义
# ============================================================
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

# 数据库连接
DATABASE_URI = 'mysql+pymysql://root:snowball950123@192.168.110.131/langgraph_agent?charset=utf8mb4'
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)

# ============================================================
# Stage 3: 工具定义
# ============================================================
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

Session = sessionmaker(bind=engine)

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

# Python REPL 工具
from typing import Annotated
from langchain_experimental.utilities import PythonREPL

repl = PythonREPL()

@tool
def python_repl(code: Annotated[str, "The python code to execute to generate your chart."]):
    """Use this to execute python code."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."

# ============================================================
# Stage 4: 创建代理
# ============================================================
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools
from langchain_core.messages import AIMessage

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
    return prompt | llm.bind_tools(tools)

# 创建数据库管理员代理
db_agent = create_agent(
    db_llm,
    [add_sale, delete_sale, update_sale, query_sales],
    system_message="You should provide accurate data for the code_generator to use."
)

# 创建代码生成代理（使用同一个模型简化示例）
code_agent = create_agent(
    db_llm,  # 实际应该使用 coder_llm
    [python_repl],
    system_message="Run python code to display diagrams or output execution results"
)

# 定义代理节点
def agent_node(state, agent, name):
    result = agent.invoke(state)
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        "sender": name,
    }

db_node = functools.partial(agent_node, agent=db_agent, name="db_manager")
code_node = functools.partial(agent_node, agent=code_agent, name="code_generator")

# ============================================================
# Stage 5: 定义路由
# ============================================================
from typing import Literal

def router(state):
    """路由器：根据消息内容决定下一步"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        return END
    return "continue"

# ============================================================
# Stage 6: 定义状态和图
# ============================================================
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

# 定义工具列表
tools = [add_sale, delete_sale, update_sale, query_sales, python_repl]
tool_executor = ToolNode(tools)

# 初始化状态图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("db_manager", db_node)
workflow.add_node("code_generator", code_node)
workflow.add_node("call_tool", tool_executor)

# 通过条件边构建子代理之间的通信
workflow.add_conditional_edges(
    "db_manager",
    router,
    {"continue": "code_generator", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "code_generator",
    router,
    {"continue": "db_manager", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {"db_manager": "db_manager", "code_generator": "code_generator"},
)

# 设置入口点
workflow.set_entry_point("db_manager")

# 编译图
graph = workflow.compile()

# ============================================================
# Stage 7: 测试运行
# ============================================================
print("=" * 50)
print("案例：基于 Network 的多代理 BI 数据分析系统")
print("=" * 50)

# 测试查询和数据可视化
print("\n--- 测试1：查询并可视化数据 ---")
for chunk in graph.stream(
    {"messages": [HumanMessage(content="根据sales_id使用折线图显示前5名销售的销售总额")]},
    {"recursion_limit": 50},
    stream_mode='values'):
    pass  # 简化输出

print("测试完成！")

print("\n" + "=" * 50)
print("案例说明：")
print("=" * 50)
print("""
本案例实现了基于 Network 架构的多代理系统。

架构特点：
1. 每个代理都可以与其他代理通信（多对多连接）
2. db_manager 负责数据库操作
3. code_generator 负责生成和执行Python代码
4. 通过条件边实现动态路由

工作流程：
用户输入 -> db_manager(查询数据) -> code_generator(生成图表) -> ... -> FINAL ANSWER
""")