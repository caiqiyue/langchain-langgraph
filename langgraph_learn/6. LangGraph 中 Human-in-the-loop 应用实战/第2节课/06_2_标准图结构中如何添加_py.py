async for chunk in graph.astream(None, config, stream_mode="values"):
    print(chunk)