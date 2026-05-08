workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node("run_tool", run_tool)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "run_tool":"run_tool",
        "end": END,
    },
)


workflow.add_edge("action", "agent")
workflow.add_edge("run_tool", "agent")