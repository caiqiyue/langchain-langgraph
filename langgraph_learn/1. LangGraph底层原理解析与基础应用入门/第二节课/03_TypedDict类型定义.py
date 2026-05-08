# -*- coding: utf-8 -*-
"""
【案例3】TypedDict类型定义
============================================

本案例展示如何使用TypedDict定义状态模式。

要点：
1. TypedDict允许为字典中的键指定期望的具体类型
2. 用于定义图的输入/输出模式
3. 确保节点间传递的数据结构符合预期
"""

# ============================================================
# 1. TypedDict基本用法
# ============================================================
from typing import TypedDict

class Contact(TypedDict):
    name: str
    email: str
    phone: str

def send_email(contact: Contact) -> None:
    print(f"Sending email to {contact['name']} at {contact['email']}")

# 使用定义好的 TypedDict 创建字典
contact_info: Contact = {
    'name': 'Alice',
    'email': 'alice@example.com',
    'phone': '123-456-7890'
}

send_email(contact_info)

# ============================================================
# 2. LangGraph中的TypedDict使用
# ============================================================
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 这两个 TypedDict 类型合并成一个字典类型
class OverallState(InputState, OutputState):
    pass

print("TypedDict用于LangGraph状态定义：")
print(f"- InputState: {InputState}")
print(f"- OutputState: {OutputState}")
print(f"- OverallState: {OverallState}")
