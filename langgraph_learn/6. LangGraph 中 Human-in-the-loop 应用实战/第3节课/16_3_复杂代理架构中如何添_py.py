def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # 如果没有 工具调用，则输出至最终节点
    if not last_message.tool_calls:
        return "end"
    # 如果还有子任务需要继续执行工具调用的话，则继续等待执行
    else:
        return "continue"