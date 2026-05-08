with SqliteSaver.from_conn_string(":memory:") as memory:
    # 保存检查点，包括时间戳
    saved_config = memory.put(
        config={"configurable": {"thread_id": checkpoint_data["thread_id"], "thread_ts": checkpoint_data["thread_ts"], "checkpoint_ns": ""}},
        checkpoint=checkpoint_data["checkpoint"],
        metadata=checkpoint_data["metadata"],
        new_versions= {"writes": {"key": "value"}}
    )

    # 检索检查点的数据
    config = {"configurable": {"thread_id": checkpoint_data["thread_id"]}}
    
    # 获取给定 thread_id 的所有检查点
    checkpoints = list(memory.list(config))  
    for checkpoint in checkpoints:
        print(checkpoint)