"""
04_手动构建Tool_Calling_Agent
手动实现工具调用链路的完整示例
不使用 ToolNode，手动实现 execute_function 节点
"""
import getpass
import os
from typing import Union, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
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

# ==================== 2. 初始化模型 ====================

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini")

# 绑定工具到模型
tools = [insert_db, fetch_real_time_info, get_weather]
llm_with_tools = llm.bind_tools(tools)

# ==================== 3. 定义节点函数 ====================

def chat_with_model(state):
    """调用模型生成响应（可能包含工具调用）"""
    print("=== chat_with_model 节点 ===")
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def execute_function(state: AgentState):
    """手动执行工具调用"""
    print("=== execute_function 节点 ===")
    tool_calls = state['messages'][-1].tool_calls
    results = []

    # 创建工具名称到工具的映射
    tools_map = {t.name: t for t in tools}

    for t in tool_calls:
        if t['name'] not in tools_map:
            result = "Unknown tool, please retry"
        else:
            result = tools_map[t['name']].invoke(t['args'])
        # 创建 ToolMessage
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    return {'messages': results}

def final_answer(state):
    """生成自然语言响应"""
    print("=== final_answer 节点 ===")
    messages = state['messages'][-1]
    return {"messages": [messages]}

# 系统提示词，用于生成最终响应
SYSTEM_PROMPT = """
请根据目前获得的信息，进行总结，生成专业的回复。注意，请用中文回复。
"""

def natural_response(state):
    """生成最终的自然语言响应"""
    print("=== natural_response 节点 ===")
    messages = state['messages'][-1]
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"messages": [response]}

def exists_function_calling(state: AgentState):
    """判断是否存在函数调用"""
    result = state['messages'][-1]
    return len(result.tool_calls) > 0

# ==================== 4. 定义状态 ====================

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# ==================== 5. 构建图 ====================

graph = StateGraph(AgentState)

graph.add_node("chat_with_model", chat_with_model)
graph.add_node("execute_function", execute_function)
graph.add_node("final_answer", final_answer)
graph.add_node("natural_response", natural_response)

# 设置入口点
graph.set_entry_point("chat_with_model")

# 添加条件边 - 根据是否有工具调用决定路由
graph.add_conditional_edges(
    "chat_with_model",
    exists_function_calling,
    {True: "execute_function", False: "final_answer"}
)

# 执行完工具后进入 natural_response
graph.add_edge("execute_function", "natural_response")
# 普通响应也进入 natural_response
graph.add_edge("final_answer", "natural_response")

# 设置结束点
graph.set_finish_point("natural_response")

# 编译图
graph = graph.compile()

# 可视化
print("图结构：")
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ==================== 6. 测试 ====================

print("\n" + "="*50)
print("测试1: 简单问候（无需工具调用）")
print("="*50)
messages = [HumanMessage(content="你好，请你介绍一下你自己")]
result = graph.invoke({"messages": messages})
print(f"最终输出: {result['messages'][-1].content}")

print("\n" + "="*50)
print("测试2: 实时搜索（需要工具调用）")
print("="*50)
messages = [HumanMessage(content="Cloud3.5的最新新闻")]
result = graph.invoke({"messages": messages})
print(f"最终输出: {result['messages'][-1].content}")

print("\n" + "="*50)
print("测试3: 插入数据（需要工具调用）")
print("="*50)
messages = [HumanMessage(content="我是木羽，28岁，电话是133232，有问题随时联系")]
result = graph.invoke({"messages": messages})
print(f"最终输出: {result['messages'][-1].content}")