from langgraph.checkpoint.sqlite import SqliteSaver

# 创建一个内存中的检查点
memory = SqliteSaver.from_conn_string(":memory:")