def run_multi_round_dialogue(graph, config):
  
    while True:  # 开始多轮循环
        # 询问用户输入操作，允许退出
        user_input = input("请输入您的问题（例如：'帮我查询上海的天气数据'），输入'退出'结束对话：")
        
        # 检查是否退出对话
        if user_input.lower() == '退出':
            print("对话已结束。")
            break

        # 启动对话，根据用户的输入进行处理
        for chunk in graph.stream({"messages": user_input}, config, stream_mode="values"):
            state = graph.get_state(config)

            # 如果没有任务则结束这一轮循环
            if not state.tasks:
                if "messages" in chunk and len(chunk["messages"]) > 0:
                    print("人工智能助理：", chunk["messages"][-1].content)
                break
            
            # 处理动态断点的任务
            if state.tasks[0].name == 'run_tool':
                user_approval = None
                while True:
                    user_approval = input("是否允许执行删除操作？请输入'是'或'否'：")
                    if user_approval in ["是", "否"]:
                        break
                    else:
                        print("输入错误，请输入'是'或'否'。")
                    
                if user_approval == "是":
                    graph.update_state(config=config, values=chunk)
                    for event in graph.stream(None, config, stream_mode="values"):
                        if "messages" in event and len(event["messages"]) > 0:
                            print("人工智能助理：",  event["messages"][-1].content)
                            # event["messages"][-1].pretty_print()
                elif user_approval == "否":
                    state = graph.get_state(config)
                    tool_call_id = state.values["messages"][-1].tool_calls[0]["id"]

                    # 构造一个反馈消息来停止操作
                    new_message = {
                        "role": "tool",
                        "content": "管理员不允许执行该操作！",
                        "name": "delete_weather_from_db",
                        "tool_call_id": tool_call_id,
                    }
                    graph.update_state(config, {"messages": [new_message]}, as_node="run_tool")
                    for event in graph.stream(None, config, stream_mode="values"):
                        if "messages" in event and len(event["messages"]) > 0:
                            print("人工智能助理：",  event["messages"][-1].content)
                            #event["messages"][-1].pretty_print()