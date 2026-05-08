"""
05_Pydantic结构化输出
演示使用 Pydantic 模型进行结构化输出
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional

llm = ChatOpenAI(model="gpt-4o-mini")

# 定义 Pydantic 模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")

# 创建结构化输出模型
structured_llm = llm.with_structured_output(UserInfo)

# 测试1：提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

print("测试1 - 提取用户信息：")
print(f"姓名: {extracted_user_info.name}")
print(f"年龄: {extracted_user_info.age}")
print(f"邮箱: {extracted_user_info.email}")
print(f"电话: {extracted_user_info.phone}")

# 测试2：另一用户的不同信息
extracted_user_info2 = structured_llm.invoke("我是哈哈，3岁，邮箱为snow@gmial.com，电话是1234233052")

print("\n测试2 - 另一用户信息：")
print(f"姓名: {extracted_user_info2.name}")
print(f"年龄: {extracted_user_info2.age}")
print(f"邮箱: {extracted_user_info2.email}")
print(f"电话: {extracted_user_info2.phone}")

# 演示 isinstance 在路由中的应用
print("\n演示 isinstance 在路由判断中的应用：")
if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑 - 处理用户信息")
else:
    print("执行节点B的逻辑 - 其他处理")