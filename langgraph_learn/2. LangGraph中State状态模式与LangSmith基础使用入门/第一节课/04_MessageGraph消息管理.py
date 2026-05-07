# -*- coding: utf-8 -*-
"""
【案例 4】MessageGraph 消息管理
============================================

本案例展示 LangGraph 中的 MessageGraph 组件用于消息管理

要点：
1. MessageGraph 的作用
2. 消息类型的处理
3. 自动消息历史管理
"""

# ============================================================
# 1. 导入消息类型
# ============================================================
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

# ============================================================
# 2. 定义消息节点
# ============================================================
def chat_node(state: MessagesState):
    """
    聊天节点：处理消息列表
    """
    from langchain_openai import ChatOpenAI
    import os
    import getpass

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(state["messages"])

    # 返回的消息会自动追加到 messages 列表
    return {"messages": [response]}

# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(MessagesState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()

# ============================================================
# 4. 测试
# ============================================================
print("=" * 50)
print("案例 4: MessageGraph 消息管理")
print("=" * 50)

from langchain_core.messages import HumanMessage

result = graph.invoke({
    "messages": [HumanMessage(content="你好，请介绍一下你自己")]
})

print(f"消息数量: {len(result['messages'])}")
print(f"最后一条消息: {result['messages'][-1].content[:50]}...")