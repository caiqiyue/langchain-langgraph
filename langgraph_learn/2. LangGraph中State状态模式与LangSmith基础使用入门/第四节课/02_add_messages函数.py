"""
02_add_messages函数
演示add_messages函数的行为
这个函数是LangGraph预构建的Reducer，用于合并消息列表
"""
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

# 场景1：合并不同ID的消息
print("=== 场景1：合并不同ID的消息 ===")
msgs1 = [HumanMessage(content="你好。", id="1")]
msgs2 = [AIMessage(content="你好，很高兴认识你。", id="2")]

result = add_messages(msgs1, msgs2)
print("合并结果:", result)
print("说明: 不同ID的消息会被追加到列表中")

# 场景2：合并相同ID的消息
print("\n=== 场景2：合并相同ID的消息 ===")
msgs1 = [HumanMessage(content="你好。", id="1")]
msgs2 = [HumanMessage(content="你好呀。", id="1")]

result = add_messages(msgs1, msgs2)
print("合并结果:", result)
print("说明: 相同ID的消息会被覆盖")

"""
add_messages函数核心逻辑：
1. 如果right的消息与left的消息具有相同的ID，则right的消息将替换left的消息
2. 否则作为一条新的消息进行追加
3. 默认情况下，状态为"仅附加"，除非新消息与现有消息具有相同的ID

这就是为什么在开发人机交互程序时，通常首先创建一个StateGraph，
然后在State中定义一个使用add_messages作为Reducer的messages键
"""