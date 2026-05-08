# 第3阶段说明
# 本节课程：图状态中处理消息的思路

## 学习目标
1. 理解在LangGraph中处理消息的模式
2. 掌握如何接入大模型并处理对话
3. 理解消息列表在State中的管理和传递

## 核心概念
- messages键：存储消息列表的State键
- HumanMessage：用户输入消息
- AIMessage：大模型响应消息
- operator.add：消息追加Reducer

## 课程文件
- 01_大模型接入与消息处理.py：演示大模型接入和消息处理流程

## 注意事项
- 需要设置OpenAI API Key
- 消息处理是构建对话机器人的基础