# -*- coding: utf-8 -*-
"""
【案例 2】Reducer 函数基础
============================================

本案例展示 LangGraph 中 Reducer 函数的概念和用法

要点：
1. Reducer 的作用：如何合并多个状态更新
2. 自定义 Reducer 函数
3. 默认 Reducer 行为
"""

# ============================================================
# 1. Reducer 概念
# ============================================================
from typing import TypedDict
from operator import add

# 定义带列表的状态
class ChatState(TypedDict):
    messages: list

# ============================================================
# 2. 自定义 Reducer 函数
# ============================================================
def message_adder(existing: list, new: list) -> list:
    """
    自定义 Reducer：追加新消息到现有消息列表
    """
    return existing + new

# ============================================================
# 3. 测试 Reducer
# ============================================================
print("=" * 50)
print("案例 2: Reducer 函数基础")
print("=" * 50)

existing_messages = ["你好", "有什么可以帮助你的吗？"]
new_messages = ["我想了解天气"]

result = message_adder(existing_messages, new_messages)
print(f"原有消息: {existing_messages}")
print(f"新消息: {new_messages}")
print(f"合并结果: {result}")

print("\nReducer 说明:")
print("- Reducer 定义如何合并多个状态更新")
print("- 默认情况下，新值会覆盖旧值")
print("- 使用自定义 Reducer 可以实现追加、累加等操作")