from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display
from langchain_core.tools import tool
from langgraph.graph import MessagesState, START
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph
import json
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

# 定义状态模式
class State(TypedDict):
    user_input: str
    model_response: str
    user_approval: str

# 定义用于大模型交互的节点
def call_model(state):
    messages = state["user_input"]
    if '删除' in state["user_input"]:
        state["user_approval"] = f"用户输入的指令是:{state['user_input']}, 请人工确认是否执行！"
    else:
        response = llm.invoke(messages)
        state["user_approval"] = "直接运行！"
        state["model_response"] = response
    return state

# 定义人工介入的breakpoint内部的执行逻辑
def execute_users(state):
    if state["user_approval"] == "是":
        response = "您的删除请求已经获得管理员的批准并成功执行。如果您有其他问题或需要进一步的帮助，请随时联系我们。"
        return {"model_response":AIMessage(response)}
    elif state["user_approval"] == "否":
        response = "对不起，您当前的请求是高风险操作，管理员不允许执行！"
        return {"model_response":AIMessage(response)}    
    else:
        return state

# 定义翻译节点
def translate_message(state: State):
    system_prompt = """
    Please translate the received text in any language into English as output
    """
    messages = state['model_response']
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=messages.content)]
    response = llm.invoke(messages)
    return {"model_response": response}

# 构建状态图
builder = StateGraph(State)

# 向图中添加节点
builder.add_node("call_model", call_model)
builder.add_node("execute_users", execute_users)
builder.add_node("translate_message", translate_message)

# 构建边
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "execute_users")
builder.add_edge("execute_users", "translate_message")
builder.add_edge("translate_message", END)

# 设置 checkpointer，使用内存存储
memory = MemorySaver()

# 在编译图的时候，添加短期记忆，并使用interrupt_before参数 设置 在 execute_users 节点之前中止图的运行，等待人工审核
graph = builder.compile(checkpointer=memory, interrupt_before=["execute_users"])

# 生成可视化图像结构
display(Image(graph.get_graph().draw_mermaid_png()))