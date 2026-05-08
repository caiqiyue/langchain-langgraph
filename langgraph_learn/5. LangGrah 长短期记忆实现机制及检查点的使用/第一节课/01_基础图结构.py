"""
第1阶段、AI Agent的记忆机制认知
本节代码演示：
- 基础 StateGraph 构建
- Checkpointer 概念引入
- 多轮对话测试

学习完本节后，你将理解：
1. 什么是短期记忆和长期记忆
2. LangGraph 中 Checkpointer 的作用
3. 如何在图中添加和配置 checkpointer
"""

# ============================================================
# 示例1：基础图结构（不含 Checkpointer）
# ============================================================
# 本示例展示一个最基础的状态图，用于演示 LangGraph 的基本用法。
# 该图没有添加 checkpointer，因此不具备记忆功能，每次对话都是独立的。

import getpass
import os
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages

# 初始化 LLM
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: State):
    """处理用户输入，调用大模型生成回复"""
    response = llm.invoke(state["messages"])
    return {"messages": response}


def translate_message(state: State):
    """将上一步的回复翻译成英文"""
    system_prompt = """
    Please translate the received text in any language into English as output
    """
    messages = state['messages']
    if isinstance(messages[-1], HumanMessage):
        # 如果最后一条是用户消息，需要先构建对话历史
        translated = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    else:
        # 翻译 AI 的回复
        translated = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"][:-1] + [state["messages"][-1]])
    return {"messages": translated}


# 构建简单图
builder = StateGraph(State)
builder.add_node("call_model", call_model)
builder.add_node("translate_message", translate_message)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "translate_message")
builder.add_edge("translate_message", END)

# 编译图（不使用 checkpointer，无记忆功能）
simple_graph = builder.compile()

# 可视化
display(Image(simple_graph.get_graph().draw_mermaid_png()))


# ============================================================
# 测试：无记忆的两轮对话
# ============================================================
# 由于没有 checkpointer，每轮对话都是独立的，模型不知道之前的对话内容

async def test_no_memory():
    """测试没有记忆功能的两轮对话"""
    print("=" * 50)
    print("第一轮对话：")
    async for chunk in simple_graph.astream(input={"messages": ["你好，请介绍你自己"]}, stream_mode="values"):
        message = chunk["messages"][-1]
        if hasattr(message, 'pretty_print'):
            message.pretty_print()
        else:
            print(message)

    print("\n" + "=" * 50)
    print("第二轮对话：")
    async for chunk in simple_graph.astream(input={"messages": ["你知道我刚才问了你什么吗？"]}, stream_mode="values"):
        message = chunk["messages"][-1]
        if hasattr(message, 'pretty_print'):
            message.pretty_print()
        else:
            print(message)


# 注意：在 Jupyter 环境中可以直接运行 test_no_memory()
# 在普通 Python 环境中需要使用 asyncio.run(test_no_memory())


print("=" * 50)
print("基础图结构演示 - 无记忆功能")
print("=" * 50)
print("""
在这个示例中，我们创建了一个简单的状态图：
1. START -> call_model -> translate_message -> END
2. 该图没有使用 checkpointer，因此没有记忆功能
3. 每次对话都是独立的，模型不会记住之前的内容

接下来请查看 02_异步流式输出测试.py 学习如何使用 checkpointer
""")