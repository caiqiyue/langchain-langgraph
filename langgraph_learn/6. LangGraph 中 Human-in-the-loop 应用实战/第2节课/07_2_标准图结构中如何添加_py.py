# 运行图，直至到断点的节点
async for chunk in graph.astream({"user_input": "我将在数据库中删除 id 为 muyu2222 的所有信息"}, config,  stream_mode="values"):
    print(chunk)