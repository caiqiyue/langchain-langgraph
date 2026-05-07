# -*- coding: utf-8 -*-
"""
【案例4】使用TypedDict做结构化输出
============================================

本案例展示如何使用TypedDict定义输出格式

要点：
1. TypedDict模型定义
2. Annotated语法使用
3. TypedDict与Pydantic的区别
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os
from typing import Optional
from typing_extensions import Annotated, TypedDict

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# ============================================================
# 3. 定义TypedDict模型
# ============================================================
class UserInfo(TypedDict):
    """Extracted user information from text"""
    name: Annotated[str, ..., "The user's name"]
    age: Annotated[Optional[int], None, "The user's age"]
    email: Annotated[str, ..., "The user's email address"]
    phone: Annotated[Optional[str], None, "The user's phone number"]

# ============================================================
# 4. 创建结构化输出模型
# ============================================================
structured_llm = llm.with_structured_output(UserInfo)

print("=" * 50)
print("使用TypedDict进行结构化输出")
print("=" * 50)

# ============================================================
# 5. 测试结构化输出
# ============================================================
query = "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052"
extracted_user_info = structured_llm.invoke(query)

print(f"\n查询: {query}")
print(f"提取结果: {extracted_user_info}")
print(f"提取结果类型: {type(extracted_user_info)}")

# ============================================================
# 6. TypedDict与Pydantic的区别说明
# ============================================================
print("\n" + "=" * 50)
print("TypedDict与Pydantic的区别")
print("=" * 50)
print("""
1. TypedDict创建的"对象"实际上是一个字典
2. 没有Pydantic模型那样的方法和属性
3. 主要用于静态类型检查，不会进行运行时类型验证
4. 搭配LangGraph的基本验证机制使用
""")