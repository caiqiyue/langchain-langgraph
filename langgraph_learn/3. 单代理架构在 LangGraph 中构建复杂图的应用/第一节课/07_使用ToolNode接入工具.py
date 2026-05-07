# -*- coding: utf-8 -*-
"""
【案例7】使用ToolNode接入工具
============================================

本案例展示如何使用ToolNode接入外部工具

要点：
1. @tool装饰器的使用
2. ToolNode的创建
3. 工具调用的三种状态要求
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import requests
import json
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage

# ============================================================
# 2. 定义外部工具函数
# ============================================================
@tool
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": query,
      "num": 1,
    })
    headers = {
      'X-API-KEY': 'your-api-key',
      'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)
    if 'organic' in data:
        return json.dumps(data['organic'], ensure_ascii=False)
    else:
        return json.dumps({"error": "No organic results found"}, ensure_ascii=False)

# ============================================================
# 3. 查看工具信息
# ============================================================
print("=" * 50)
print("工具信息")
print("=" * 50)
print(f"name: {fetch_real_time_info.name}")
print(f"description: {fetch_real_time_info.description}")
print(f"arguments: {fetch_real_time_info.args}")

# ============================================================
# 4. 创建ToolNode
# ============================================================
tools = [fetch_real_time_info]
tool_node = ToolNode(tools)

print(f"\nToolNode创建成功: {tool_node}")

# ============================================================
# 5. 手动调用ToolNode
# ============================================================
print("\n" + "=" * 50)
print("手动调用ToolNode")
print("=" * 50)

# 创建带有tool_calls的AIMessage
message_with_single_tool_call = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "fetch_real_time_info",
            "args": {"query": "Cloud3.5的最新新闻"},
            "id": "tool_call_id",
            "type": "tool_call",
        }
    ],
)

# 调用ToolNode
result = tool_node.invoke({"messages": [message_with_single_tool_call]})
print(f"\n工具调用结果:")
print(result)