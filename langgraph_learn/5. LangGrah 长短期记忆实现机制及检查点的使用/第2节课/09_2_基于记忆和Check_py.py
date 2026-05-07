for chunk in graph_with_memory.stream({"messages": ["我刚才都问了你什么问题？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()