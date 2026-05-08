# 创建一个函数来封装对话逻辑
def run_dialogue(graph, config, all_chunks=[]):
    while True:
        # 接收用户输入
        user_input = input("请输入您的消息（输入'退出'结束对话）：")
        if user_input.lower() == '退出':
            break
        
        # 运行图，直至到断点的节点
        for chunk in graph.stream({"user_input": user_input}, config, stream_mode="values"):
            all_chunks.append(chunk)
        
        # 处理可能的审批请求
        last_chunk = all_chunks[-1]
        if last_chunk["user_approval"] ==  f"用户输入的指令是:{last_chunk['user_input']}, 请人工确认是否执行！":
            user_approval = input(f"当前用户的输入是：{last_chunk['user_input']}, 请人工确认是否执行！请回复 是/否。")
            graph.update_state(config, {"user_approval": user_approval})

        # 继续执行图
        for chunk in graph.stream(None, config, stream_mode="values"):
            all_chunks.append(chunk)
        
        # 显示最终模型的响应
        print("人工智能助理：", all_chunks[-1]["model_response"].content)