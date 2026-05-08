config = {"configurable": {"thread_id": "9"}}

for chunk in graph.stream({"messages": "帮我同时查一下上海、杭州的天气，比较哪个城市更适合现在出游。"}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()