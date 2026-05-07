config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream({"messages": ["你还知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()