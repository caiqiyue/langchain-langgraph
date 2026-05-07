# -*- coding: utf-8 -*-
"""
【案例9】Tool Calling Agent完整实现
============================================

本案例展示Tool Calling Agent的完整实现

要点：
1. 完整工具库定义
2. 路由与执行逻辑
3. 图构建与编译
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import Union, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")

# ============================================================
# 3. 定义工具
# ============================================================
from langchain_core.tools import tool

class SearchQuery(BaseModel):
    query: str = Field(description="Questions for networking queries")

class WeatherLoc(BaseModel):
    location: str = Field(description="The location name of the city")

class UserInfo(BaseModel):
    """Extracted user information"""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

@tool(args_schema=SearchQuery)
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    return f"搜索结果: {query}"

@tool(args_schema=WeatherLoc)
def get_weather(location):
    """Call to get the current weather."""
    if location.lower() in ["beijing"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai"]:
        return "上海的温度是20度，部分多云。"
    else:
        return "不好意思，并未查询到具体的天气信息。"

@tool(args_schema=UserInfo)
def insert_db(name, age, email, phone):
    """Insert user information into the database"""
    return f"数据已成功存储至数据库: name={name}, age={age}, email={email}, phone={phone}"

# 工具列表
tools = [fetch_real_time_info, get_weather, insert_db]
tool_node = ToolNode(tools)

# 绑定工具到模型
model_with_tools = llm.bind_tools(tools)

# ============================================================
# 4. 定义响应模型
# ============================================================
class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner."""
    response: str = Field(description="A conversational response to the user's query")

class FinalResponse(BaseModel):
    final_output: Union[ConversationalResponse, SearchQuery, WeatherLoc, UserInfo]

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

def execute_function(state):
    """execute the selected tool"""
    messages = state['messages'][-1].final_output
    response = tool_node.invoke({"messages": [model_with_tools.invoke(str(messages))]})
    return {"messages": [response]}

# ============================================================
# 6. 定义Router Function
# ============================================================
def generate_branch(state: AgentState):
    result = state['messages'][-1]
    output = result.final_output

    if isinstance(output, ConversationalResponse):
        return False
    else:
        return True

# ============================================================
# 7. 定义状态和构建图
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("chat_with_model", chat_with_model)
graph.add_node("final_answer", final_answer)
graph.add_node("execute_function", execute_function)

# 设置图的启动节点
graph.set_entry_point("chat_with_model")

# 设置条件边
graph.add_conditional_edges(
    "chat_with_model",
    generate_branch,
    {True: "execute_function", False: "final_answer"}
)

# 设置终止节点
graph.set_finish_point("final_answer")
graph.set_finish_point("execute_function")

# 编译图
graph = graph.compile()

print("=" * 50)
print("Tool Calling Agent 构建完成")
print("=" * 50)

# ============================================================
# 8. 测试
# ============================================================
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 测试1: 普通对话
print("\n--- 测试1: 普通对话 ---")
query = "你好，请你介绍一下你自己"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"查询: {query}")
print(f"结果: {result['messages'][-1]}")

# 测试2: 天气查询
print("\n--- 测试2: 天气查询 ---")
query = "北京的天气怎么样？"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"查询: {query}")
print(f"结果: {result['messages'][-1]}")

# 测试3: 网络搜索
print("\n--- 测试3: 网络搜索 ---")
query = "帮我查一下Cloud3.5的最新新闻"
input_message = {"messages": [HumanMessage(content=query)]}
result = graph.invoke(input_message)
print(f"查询: {query}")
print(f"结果: {result['messages'][-1]}")