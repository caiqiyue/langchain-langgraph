# -*- coding: utf-8 -*-
"""
【案例10】手动构建Tool Calling Agent
============================================

本案例展示如何手动构建Tool Calling Agent（不依赖ToolNode自动处理）

要点：
1. 手动处理tool_calls
2. 工具执行逻辑
3. 循环调用机制
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
import operator

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")

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
llm_with_tools = llm.bind_tools(tools)

# ============================================================
# 4. 定义节点函数
# ============================================================
def chat_with_model(state):
    """generate structured output"""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def execute_function(state: AgentState):
    """手动执行工具调用"""
    tool_calls = state['messages'][-1].tool_calls
    results = []
    tools_dict = {t.name: t for t in tools}

    for t in tool_calls:
        if not t['name'] in tools_dict:
            result = "bad tool name, retry"
        else:
            result = tools_dict[t['name']].invoke(t['args'])
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    return {'messages': results}

def final_answer(state):
    """generate natural language responses"""
    messages = state['messages'][-1]
    return {"messages": [messages]}

def exists_function_calling(state: AgentState):
    """判断是否存在工具调用"""
    result = state['messages'][-1]
    return len(result.tool_calls) > 0

# ============================================================
# 5. 定义状态和构建图
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("chat_with_model", chat_with_model)
graph.add_node("execute_function", execute_function)
graph.add_node("final_answer", final_answer)

# 设置图的启动节点
graph.set_entry_point("chat_with_model")

# 设置条件边
graph.add_conditional_edges(
    "chat_with_model",
    exists_function_calling,
    {True: "execute_function", False: "final_answer"}
)

# 执行完工具后回到chat_with_model继续循环
graph.add_edge("execute_function", "chat_with_model")
graph.add_edge("final_answer", END)

# 编译图
graph = graph.compile()

print("=" * 50)
print("手动构建 Tool Calling Agent 构建完成")
print("=" * 50)

# ============================================================
# 6. 测试
# ============================================================
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# 测试1: 普通对话
print("\n--- 测试1: 普通对话 ---")
messages = [HumanMessage(content="你好，请你介绍一下你自己")]
result = graph.invoke({"messages": messages})
print(f"结果: {result['messages'][-1]}")

# 测试2: 天气查询
print("\n--- 测试2: 天气查询 ---")
messages = [HumanMessage(content="北京的天气怎么样？")]
result = graph.invoke({"messages": messages})
print(f"结果: {result['messages'][-1]}")