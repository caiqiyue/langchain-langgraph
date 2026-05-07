# -*- coding: utf-8 -*-
"""
【案例3】使用Pydantic做结构化输出
============================================

本案例展示如何使用Pydantic定义输出格式，
并使用with_structured_output方法让模型返回结构化数据

要点：
1. Pydantic模型定义
2. with_structured_output方法使用
3. 结构化输出在Router中的应用
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import Optional
from pydantic import BaseModel, Field

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# ============================================================
# 3. 定义Pydantic模型
# ============================================================
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

# ============================================================
# 4. 创建结构化输出模型
# ============================================================
structured_llm = llm.with_structured_output(UserInfo)

print("=" * 50)
print("使用Pydantic进行结构化输出")
print("=" * 50)
print(f"\n模型类型: {type(structured_llm).__name__}")

# ============================================================
# 5. 测试结构化输出
# ============================================================
# 测试从文本中提取用户信息
query1 = "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052"
extracted_user_info1 = structured_llm.invoke(query1)

print(f"\n查询: {query1}")
print(f"提取结果: {extracted_user_info1}")
print(f"提取结果类型: {type(extracted_user_info1)}")

# 测试另一个文本
query2 = "我是哈哈，3岁，邮箱为snow@gmial.com，电话是1234233052"
extracted_user_info2 = structured_llm.invoke(query2)

print(f"\n查询: {query2}")
print(f"提取结果: {extracted_user_info2}")

# ============================================================
# 6. 使用isinstance进行类型判断
# ============================================================
print("\n" + "=" * 50)
print("使用isinstance进行类型判断")
print("=" * 50)

extracted_user_info = extracted_user_info1
if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑（需要存储到数据库）")
else:
    print("执行节点B的逻辑（直接回复用户）")

# 测试非用户信息输入
extracted_user_info = "你好"
if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑")
else:
    print("执行节点B的逻辑（直接回复用户）")