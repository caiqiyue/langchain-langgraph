async for chunk in graph_with_memory.astream(input={"messages": ["你好，我叫木羽"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()