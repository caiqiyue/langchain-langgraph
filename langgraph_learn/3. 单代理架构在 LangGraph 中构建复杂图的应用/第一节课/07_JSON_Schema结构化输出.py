"""
07_JSON_Schema结构化输出
演示使用 JSON Schema 格式进行结构化输出
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# 定义 JSON Schema
json_schema = {
    "title": "user_info",
    "description": "Extracted user information",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The user's name",
        },
        "age": {
            "type": "integer",
            "description": "The user's age",
            "default": None,
        },
        "email": {
            "type": "string",
            "description": "The user's email address",
        },
        "phone": {
            "type": "string",
            "description": "The user's phone number",
            "default": None,
        },
    },
    "required": ["name", "email"],
}

# 创建结构化输出模型
structured_llm = llm.with_structured_output(json_schema)

# 测试：提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

print("JSON Schema 结构化输出结果：")
print(f"类型: {type(extracted_user_info)}")
print(f"内容: {extracted_user_info}")

print("\n说明: JSON Schema 方式无需导入类，直接通过字典形式定义，但代码更冗长")