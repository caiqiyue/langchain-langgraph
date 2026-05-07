config = {"configurable": {"thread_id": "9"}}

for chunk in graph.stream({"messages": "北京的天气怎么样？"}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()