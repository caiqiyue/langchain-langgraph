config = {"configurable": {"thread_id": "10"}, "user_id": "6"}

async for chunk in graph.astream({"messages": ["你好，我是木羽"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()