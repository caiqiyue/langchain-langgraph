"""
01_ToolNode基础使用
演示如何使用 @tool 装饰器和 ToolNode 进行工具调用
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage
import json

llm = ChatOpenAI(model="gpt-4o")

# ==================== 1. 定义工具函数 ====================

@tool
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": query,
      "num": 1,
    })
    headers = {
      'X-API-KEY': 'YOUR_API_KEY',  # 请替换为实际的 API Key
      'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)
    if 'organic' in data:
        return json.dumps(data['organic'], ensure_ascii=False)
    else:
        return json.dumps({"error": "No organic results found"}, ensure_ascii=False)

@tool
def get_weather(location):
    """Call to get the current weather."""
    if location.lower() in ["beijing"]:
        return "北京的温度是16度，天气晴朗。"
    elif location.lower() in ["shanghai"]:
        return "上海的温度是20度，多云。"
    else:
        return "抱歉，暂未查询到该地区的天气信息。"

# 打印工具信息
print(f'''
工具名称: {fetch_real_time_info.name}
工具描述: {fetch_real_time_info.description}
工具参数: {fetch_real_time_info.args}
''')

# ==================== 2. 创建 ToolNode ====================

tools = [fetch_real_time_info, get_weather]
tool_node = ToolNode(tools)

print(f"ToolNode 创建成功，包含 {len(tools)} 个工具")

# ==================== 3. 单个工具调用 ====================

# 创建带有单个工具调用的 AI 消息
message_with_single_tool_call = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "fetch_real_time_info",
            "args": {"query": "Cloud3.5最新新闻"},
            "id": "tool_call_id",
            "type": "tool_call",
        }
    ],
)

print("\n单个工具调用结果：")
result = tool_node.invoke({"messages": [message_with_single_tool_call]})
print(result)

# ==================== 4. 并行工具调用 ====================

# 创建带有多个工具调用的 AI 消息
message_with_multiple_tool_calls = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "fetch_real_time_info",
            "args": {"query": "Cloud3.5最新新闻"},
            "id": "tool_call_id",
            "type": "tool_call",
        },
        {
            "name": "get_weather",
            "args": {"location": "beijing"},
            "id": "tool_call_id_2",
            "type": "tool_call",
        },
    ],
)

print("\n并行工具调用结果：")
result = tool_node.invoke({"messages": [message_with_multiple_tool_calls]})
print(result)