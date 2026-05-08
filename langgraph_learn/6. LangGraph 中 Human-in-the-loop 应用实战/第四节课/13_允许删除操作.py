config = {"configurable": {"thread_id": "9"}}

for chunk in graph.stream({"messages": "帮我删除数据库中北京的天气数据"}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()