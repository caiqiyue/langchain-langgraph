"""
08_完整Router_Agent案例
结合结构化输出构建完整的路由图，实现用户信息提取并存入数据库
这是一个完整的 Router Agent 应用案例
"""
import getpass
import os
from typing import Union, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from IPython.display import Image, display

# ==================== 1. 定义 Pydantic 模型 ====================

# 定义数据库插入的用户信息模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

# 定义正常对话的响应模型
class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner. Be kind and helpful."""
    response: str = Field(description="A conversational response to the user's query")

# 定义最终响应模型 - 使用 Union 支持多种输出类型
class FinalResponse(BaseModel):
    final_output: Union[UserInfo, ConversationalResponse]

# ==================== 2. 初始化模型和数据库 ====================

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# 初始化模型
llm = ChatOpenAI(model="gpt-4o-mini")

# ==================== 3. 数据库设置 ====================
# 注意：需要替换为实际的 MySQL 连接信息
# pip install sqlalchemy pymysql

Base = declarative_base()

# 定义 User 表
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    email = Column(String(100))
    phone = Column(String(15))

# 数据库连接 URI - 请替换为实际的 MySQL 连接信息
# 格式: mysql+pymysql://用户名:密码@主机地址:端口/数据库名?charset=utf8mb4
DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/langgraph_agent?charset=utf8mb4'

try:
    engine = create_engine(DATABASE_URI, echo=True)
    # 创建表
    Base.metadata.create_all(engine)
    # 创建会话
    Session = sessionmaker(bind=engine)
    print("数据库连接成功！")
except Exception as e:
    print(f"数据库连接失败: {e}")
    print("将跳过数据库操作，仅演示路由逻辑")

# ==================== 4. 定义节点函数 ====================

def chat_with_model(state):
    """生成结构化输出"""
    print("=== chat_with_model 节点 ===")
    messages = state['messages']
    structured_llm = llm.with_structured_output(FinalResponse)
    response = structured_llm.invoke(messages)
    return {"messages": [response]}

def final_answer(state):
    """生成自然语言响应"""
    print("=== final_answer 节点 ===")
    messages = state['messages'][-1]
    response = messages.final_output.response
    return {"messages": [response]}

def insert_db(state):
    """将用户信息插入数据库"""
    print("=== insert_db 节点 ===")
    session = Session()
    try:
        result = state['messages'][-1]
        output = result.final_output
        # 创建用户实例
        user = User(name=output.name, age=output.age, email=output.email, phone=output.phone)
        # 添加到会话
        session.add(user)
        # 提交事务
        session.commit()
        return {"messages": [f"用户信息已成功存储到数据库。"]}
    except Exception as e:
        session.rollback()  # 出错时回滚
        return {"messages": [f"数据存储失败，原因：{e}"]}
    finally:
        session.close()  # 关闭会话

# ==================== 5. 定义状态和路由函数 ====================

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def generate_branch(state: AgentState):
    """路由函数 - 根据输出类型选择分支"""
    result = state['messages'][-1]
    output = result.final_output

    if isinstance(output, UserInfo):
        return True  # 路由到 insert_db
    elif isinstance(output, ConversationalResponse):
        return False  # 路由到 final_answer

# ==================== 6. 构建图 ====================

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("chat_with_model", chat_with_model)
graph.add_node("final_answer", final_answer)
graph.add_node("insert_db", insert_db)

# 设置入口点
graph.set_entry_point("chat_with_model")

# 添加条件边
graph.add_conditional_edges(
    "chat_with_model",
    generate_branch,
    {True: "insert_db", False: "final_answer"}
)

# 设置结束点
graph.set_finish_point("final_answer")
graph.set_finish_point("insert_db")

# 编译图
graph = graph.compile()

# 可视化
print("\n图结构：")
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ==================== 7. 测试 ====================

print("\n" + "="*50)
print("测试1: 提取用户信息（应路由到 insert_db）")
print("="*50)
query = "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1323521313"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"最终输出: {result['messages'][-1]}")

print("\n" + "="*50)
print("测试2: 简单问候（应路由到 final_answer）")
print("="*50)
query = "你好，请你介绍一下你自己"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"最终输出: {result['messages'][-1]}")

print("\n" + "="*50)
print("测试3: 知识问答（应路由到 final_answer）")
print("="*50)
query = "请问什么是机器学习"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"最终输出: {result['messages'][-1]}")