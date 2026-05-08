"""
02_绑定工具到LLM
演示如何使用 bind_tools 将工具绑定到大模型
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import json

llm = ChatOpenAI(model="gpt-4o")

# ==================== 定义工具 ====================

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

tools = [fetch_real_time_info, get_weather]

# ==================== 绑定工具到模型 ====================

model_with_tools = llm.bind_tools(tools)

print("模型信息：")
print(model_with_tools)
print(f"\n模型 kwargs: {model_with_tools.kwargs}")

# ==================== 测试工具调用 ====================

# 测试1：查询新闻
print("\n" + "="*50)
print("测试1: 查询 Cloud3.5 最新新闻")
print("="*50)
result = model_with_tools.invoke("Cloud3.5的最新新闻")
print(f"tool_calls: {result.tool_calls}")

# 测试2：查询天气
print("\n" + "="*50)
print("测试2: 查询北京天气")
print("="*50)
result = model_with_tools.invoke("北京现在多少度呀？")
print(f"tool_calls: {result.tool_calls}")

print("\n说明：大模型可以正确填充 tool_calls 信息，传递给 ToolNode 执行")