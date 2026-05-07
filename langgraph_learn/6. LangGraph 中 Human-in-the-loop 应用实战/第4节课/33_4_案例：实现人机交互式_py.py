memory = MemorySaver()

graph = workflow.compile(checkpointer=memory, interrupt_before=["run_tool"])