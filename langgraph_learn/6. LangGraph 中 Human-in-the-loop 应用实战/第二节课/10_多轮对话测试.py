# 运行图，直至到断点的节点
async for chunk in graph.astream({"user_input": "你好，请你介绍一下你自己"}, config,  stream_mode="values"):
    pass

async for chunk in graph.astream(None, config, stream_mode="values"):
    print(chunk)