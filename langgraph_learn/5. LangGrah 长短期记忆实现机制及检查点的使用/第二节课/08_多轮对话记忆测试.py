# 这个 thread_id 可以取任意数值
config = {"configurable": {"thread_id": "1"}}

for chunk in graph_with_memory.stream({"messages": ["你好，我叫木羽"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()


for chunk in graph_with_memory.stream({"messages": ["请问我叫什么？"]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()