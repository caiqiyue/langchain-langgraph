config = {"configurable": {"thread_id": "10"}}

for chunk in graph.stream({"messages": "帮我删除数据库中上海的天气数据"}, config, stream_mode="values"):
    state = graph.get_state(config)

    # print(state.next)
    # print(state.tasks)

    # 检查是否有任务，如果没有则结束循环
    if not state.tasks:
        # print("所有任务都已完成。")
        chunk["messages"][-1].pretty_print()
        break
    
    if state.tasks[0].name == 'run_tool':
        while True:
            user_input = input("是否允许执行删除操作？请输入'是'或'否'：")
            if user_input in ["是", "否"]:
                break
            else:
                print("输入错误，请输入'是'或'否'。")
            
        if user_input == "是":
            graph.update_state(config=config, values=chunk)
            for event in graph.stream(None, config, stream_mode="values"):
                event["messages"][-1].pretty_print()
        elif user_input == "否":
            state = graph.get_state(config)
            tool_call_id = state.values["messages"][-1].tool_calls[0]["id"]
            print(tool_call_id)

            #我们现在需要构造一个替换工具调用。把参数改为“xxsd”，请注意，我们可以更改任意数量的参数或工具名称-它必须是一个有效的
            new_message = {
                "role": "tool",
                # 这是得到的用户不允许操作的反馈
                "content": "管理员不允许执行该操作！",
                "name": "delete_weather_from_db",
                "tool_call_id": tool_call_id,
            }
            graph.update_state(config, {"messages": [new_message]}, as_node="run_tool",)
            for event in graph.stream(None, config, stream_mode="values"):
                event["messages"][-1].pretty_print()