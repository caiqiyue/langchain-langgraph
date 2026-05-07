# -*- coding: utf-8 -*-
"""
【案例 1】State 状态定义与 TypedDict
============================================

本案例展示如何使用 TypedDict 定义 LangGraph 中的状态模式

要点：
1. TypedDict 基础用法
2. 状态模式的定义
3. 输入、输出状态的合并
"""

# ============================================================
# 1. TypedDict 基础用法
# ============================================================
from typing import TypedDict

class Contact(TypedDict):
    """联系人类型定义"""
    name: str
    email: str
    phone: str

def send_email(contact: Contact) -> None:
    print(f"Sending email to {contact['name']}")

# 使用定义好的 TypedDict 创建字典
contact_info: Contact = {
    'name': 'Alice',
    'email': 'alice@example.com',
    'phone': '123-456-7890'
}

send_email(contact_info)

# ============================================================
# 2. LangGraph 状态定义
# ============================================================
from typing_extensions import TypedDict

# 定义输入的模式
class InputState(TypedDict):
    question: str

# 定义输出的模式
class OutputState(TypedDict):
    answer: str

# 将 InputState 和 OutputState 合并成一个更全面的字典类型
class OverallState(InputState, OutputState):
    pass

print("=" * 50)
print("案例 1: TypedDict 状态定义")
print("=" * 50)
print(f"InputState 字段: {list(InputState.__annotations__.keys())}")
print(f"OutputState 字段: {list(OutputState.__annotations__.keys())}")
print(f"OverallState 字段: {list(OverallState.__annotations__.keys())}")