config = {"configurable": {"thread_id": "11"}, "user_id": "6"}

async for chunk in graph.astream({"messages": ["你知道我叫什么吗？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()