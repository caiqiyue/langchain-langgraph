# -*- coding: utf-8 -*-
"""
【案例5】Json Schema结构化输出
============================================

本案例展示如何使用JSON Schema进行结构化输出

要点：
1. JSON Schema定义方式
2. 直接通过字典形式定义结构
3. 三种结构化输出方式的对比
"""

# ============================================================
# 1. 导入必要的模块
# ============================================================
import getpass
import os

# ============================================================
# 2. 设置API密钥
# ============================================================
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# ============================================================
# 3. 定义JSON Schema
# ============================================================
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

# ============================================================
# 4. 创建结构化输出模型
# ============================================================
structured_llm = llm.with_structured_output(json_schema)

print("=" * 50)
print("使用JSON Schema进行结构化输出")
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
# 6. 三种方式对比
# ============================================================
print("\n" + "=" * 50)
print("三种结构化输出方式对比")
print("=" * 50)
print("""
1. Pydantic:
   - 需要导入BaseModel, Field
   - 支持运行时验证
   - 代码最清晰
   - 推荐使用

2. TypedDict:
   - 使用Annotated语法
   - 仅静态类型检查
   - 无运行时验证
   - 适合类型提示

3. JSON Schema:
   - 直接用字典定义
   - 代码较冗长
   - 无验证功能
   - 适合简单场景
""")