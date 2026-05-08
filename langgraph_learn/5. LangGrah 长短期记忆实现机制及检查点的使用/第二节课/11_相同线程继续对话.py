config = {"configurable": {"thread_id": "2"}}

for chunk in graph_with_memory.stream({"messages": ["请问我刚才都问了你什么问题？"]}, config, stream_mode="debug"):
    if chunk["type"] == "checkpoint":
        # print(chunk)
        print(f"Thread id:{chunk['payload']['config']['configurable']['thread_id']}")
        print(f"CheckPoint id :{chunk['payload']['config']['configurable']['checkpoint_id']}")

        for message in chunk['payload']['values']['messages']:
            print(f"Message id:{message.id}，Message content:{message.content}")
      
    # print(f"Task id : {chunk['payload']['id']}")
    # if chunk["type"] == "task":
    #     for message in chunk["payload"]["input"]["messages"]:
    #         print(f"Message id:{message.id}, Message content:{message.content}")

    # if chunk["type"] == "task_result":
    #      print(f"Message id:{chunk['payload']['result'][0][1].id}, Message content:{chunk['payload']['result'][0][1].content}")  # tuple 类型

    print("------------------------------------------------")
    print("------------------------------------------------")