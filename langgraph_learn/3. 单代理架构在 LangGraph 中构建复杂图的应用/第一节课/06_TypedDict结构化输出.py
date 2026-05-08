"""
06_TypedDict结构化输出
演示使用 TypedDict 类定义结构化输出模式
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from typing import Optional
from typing_extensions import Annotated, TypedDict

llm = ChatOpenAI(model="gpt-4o-mini")

# 定义 TypedDict 模型
class UserInfo(TypedDict):
    """Extracted user information from text"""
    name: Annotated[str, ..., "The user's name"]
    age: Annotated[Optional[int], None, "The user's age"]
    email: Annotated[str, ..., "The user's email address"]
    phone: Annotated[Optional[str], None, "The user's phone number"]

# 创建结构化输出模型
structured_llm = llm.with_structured_output(UserInfo)

# 测试：提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

print("TypedDict 结构化输出结果：")
print(f"类型: {type(extracted_user_info)}")
print(f"内容: {extracted_user_info}")

print("\n说明: TypedDict 创建的是字典对象，没有 Pydantic 模型的方法和属性")