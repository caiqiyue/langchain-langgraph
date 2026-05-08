for chunk in graph.stream(None, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()