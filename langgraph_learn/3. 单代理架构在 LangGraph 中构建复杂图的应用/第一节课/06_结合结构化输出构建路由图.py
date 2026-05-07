# -*- coding: utf-8 -*-
"""
【案例6】结合结构化输出构建完整路由图
============================================

本案例展示如何结合Pydantic结构化输出构建Router Agent

要点：
1. 使用Union类型支持多种输出
2. Router Function的定义
3. 条件边的设置
4. 数据库连接与操作
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import Union, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from langchain_core.messages import AnyMessage, HumanMessage
import operator

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")

# ============================================================
# 3. 定义Pydantic模型
# ============================================================
# 用户信息模型
class UserInfo(BaseModel):
    """Extracted user information"""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

# 对话响应模型
class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner."""
    response: str = Field(description="A conversational response to the user's query")

# 最终响应模型（支持多种类型）
class FinalResponse(BaseModel):
    final_output: Union[UserInfo, ConversationalResponse]

# ============================================================
# 4. 数据库设置
# ============================================================
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    email = Column(String(100))
    phone = Column(String(15))

# 数据库连接配置
DATABASE_URI = 'mysql+pymysql://root:password@localhost/langgraph_agent?charset=utf8mb4'
engine = create_engine(DATABASE_URI, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ============================================================
# 5. 定义节点函数
# ============================================================
def chat_with_model(state):
    """generate structured output"""
    messages = state['messages']
    structured_llm = llm.with_structured_output(FinalResponse)
    response = structured_llm.invoke(messages)
    return {"messages": [response]}

def final_answer(state):
    """generate natural language responses"""
    messages = state['messages'][-1]
    response = messages.final_output.response
    return {"messages": [response]}

def insert_db(state):
    """Insert user information into the database"""
    session = Session()
    try:
        result = state['messages'][-1]
        output = result.final_output
        user = User(name=output.name, age=output.age, email=output.email, phone=output.phone)
        session.add(user)
        session.commit()
        return {"messages": [f"数据已成功存储至Mysql数据库。"]}
    except Exception as e:
        session.rollback()
        return {"messages": [f"数据存储失败，错误原因：{e}"]}
    finally:
        session.close()

# ============================================================
# 6. 定义Router Function
# ============================================================
def generate_branch(state: AgentState):
    result = state['messages'][-1]
    output = result.final_output

    if isinstance(output, UserInfo):
        return True
    elif isinstance(output, ConversationalResponse):
        return False

# ============================================================
# 7. 定义状态和构建图
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("chat_with_model", chat_with_model)
graph.add_node("final_answer", final_answer)
graph.add_node("insert_db", insert_db)

# 设置图的启动节点
graph.set_entry_point("chat_with_model")

# 设置条件边
graph.add_conditional_edges(
    "chat_with_model",
    generate_branch,
    {True: "insert_db", False: "final_answer"}
)

# 设置终止节点
graph.set_finish_point("final_answer")
graph.set_finish_point("insert_db")

# 编译图
graph = graph.compile()

print("=" * 50)
print("Router Agent图结构构建完成")
print("=" * 50)

# ============================================================
# 8. 测试
# ============================================================
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 测试插入数据库
query = "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1323521313"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"\n查询: {query}")
print(f"结果: {result['messages'][-1]}")

# 测试直接回复
query = "你好，请你介绍一下你自己"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"\n查询: {query}")
print(f"结果: {result['messages'][-1]}")