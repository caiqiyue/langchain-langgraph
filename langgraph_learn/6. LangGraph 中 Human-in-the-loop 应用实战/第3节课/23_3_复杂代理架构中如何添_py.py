config = {"configurable": {"thread_id": "4"}}

for chunk in graph.stream({"messages": "最近 OpenAI 有哪些大动作？"}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()