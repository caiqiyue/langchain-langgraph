async for chunk in simple_short_graph.astream(input={"messages": ["请问，我叫什么？"]}, stream_mode="values"):
    message = chunk["messages"][-1].pretty_print()