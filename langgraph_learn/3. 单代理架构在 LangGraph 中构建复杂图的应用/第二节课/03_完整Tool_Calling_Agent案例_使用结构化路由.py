"""
03_完整Tool_Calling_Agent案例_使用结构化路由
使用结构化输出进行路由的完整 Tool Calling Agent 实现
"""
import getpass
import os
from typing import Union, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, HumanMessage
from IPython.display import Image, display

# ==================== 1. 定义工具 ====================

class SearchQuery(BaseModel):
    query: str = Field(description="Questions for networking queries")

class WeatherLoc(BaseModel):
    location: str = Field(description="The location name of the city")

class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

@tool(args_schema=SearchQuery)
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    return f"关于 {query} 的搜索结果..."

@tool(args_schema=WeatherLoc)
def get_weather(location):
    """Call to get the current weather."""
    if location.lower() in ["beijing"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai"]:
        return "上海的温度是20度，多云。"
    else:
        return "抱歉，暂未查询到该地区的天气信息。"

@tool(args_schema=UserInfo)
def insert_db(name, age, email, phone):
    """Insert user information into the database"""
    return f"用户 {name} (年龄: {age}, 邮箱: {email}, 电话: {phone}) 已存入数据库"

tools = [insert_db, fetch_real_time_info, get_weather]
tool_node = ToolNode(tools)

# ==================== 2. 初始化模型 ====================

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")
model_with_tools = llm.bind_tools(tools)

# ==================== 3. 定义响应模型 ====================

class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner."""
    response: str = Field(description="A conversational response to the user's query")

class FinalResponse(BaseModel):
    final_output: Union[ConversationalResponse, SearchQuery, WeatherLoc, UserInfo]

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

def execute_function(state):
    """执行工具调用"""
    print("=== execute_function 节点 ===")
    messages = state['messages'][-1].final_output
    response = tool_node.invoke({"messages": [model_with_tools.invoke(str(messages))]})
    print(f"工具响应: {response}")
    response = response["messages"][0].content
    return {"messages": [response]}

# ==================== 5. 定义状态和路由函数 ====================

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def generate_branch(state: AgentState):
    """路由函数 - 根据输出类型选择分支"""
    result = state['messages'][-1]
    output = result.final_output

    if isinstance(output, ConversationalResponse):
        return False  # 路由到 final_answer
    else:
        return True   # 路由到 execute_function

# ==================== 6. 构建图 ====================

graph = StateGraph(AgentState)

graph.add_node("chat_with_model", chat_with_model)
graph.add_node("final_answer", final_answer)
graph.add_node("execute_function", execute_function)

graph.set_entry_point("chat_with_model")

graph.add_conditional_edges(
    "chat_with_model",
    generate_branch,
    {True: "execute_function", False: "final_answer"}
)

graph.set_finish_point("final_answer")
graph.set_finish_point("execute_function")

graph = graph.compile()

# 可视化
print("图结构：")
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ==================== 7. 测试 ====================

print("\n" + "="*50)
print("测试1: 简单问候（路由到 final_answer）")
print("="*50)
query = "你好，请你介绍一下你自己"
result = graph.invoke({"messages": [HumanMessage(content=query)]})
print(f"最终输出: {result['messages'][-1]}")

print("\n" + "="*50)
print("测试2: 实时搜索（路由到 execute_function -> fetch_real_time_info）")
print("="*50)
query = "帮我查一下Cloud3.5的最新新闻"
result = graph.invoke({"messages": [HumanMessage(content=query)]})
print(f"最终输出: {result['messages'][-1]}")

print("\n" + "="*50)
print("测试3: 查询天气（路由到 execute_function -> get_weather）")
print("="*50)
query = "北京的天气怎么样？"
result = graph.invoke({"messages": [HumanMessage(content=query)]})
print(f"最终输出: {result['messages'][-1]}")