config = {"configurable": {"thread_id": "4"}}

for chunk in graph.stream({"messages": "请帮我查一下北京的天气"}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()