# -*- coding: utf-8 -*-
"""
【案例 6】结构化输出 Pydantic + with_structured_output
==========================================

本案例展示如何使用 Pydantic 实现结构化输出
让 LLM 返回程序友好的数据

要点：
1. Pydantic 模型定义
2. with_structured_output 的用法
3. 结构化输出的应用场景
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / ".env"
load_dotenv(env_path, override=True)

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")
os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 6: 结构化输出")
print("=" * 50)

from pydantic import BaseModel, Field
from typing import List
from langchain_community.chat_models.tongyi import ChatTongyi

# ============================================================
# 1. 定义 Pydantic 模型
# ============================================================
print("\n1. 定义 Pydantic 模型")
print("-" * 30)

class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="人的姓名")
    age: int = Field(description="人的年龄")
    hobbies: List[str] = Field(description="爱好列表")
    email: str = Field(description="邮箱地址", default="")

print(f"Person 模型字段:")
for field_name, field in Person.model_fields.items():
    print(f"  {field_name}: {field.annotation} - {field.description}")

# ============================================================
# 2. 使用 with_structured_output
# ============================================================
print("\n2. with_structured_output")
print("-" * 30)

model = ChatTongyi(model="qwen3-max", temperature=0)
structured_model = model.with_structured_output(Person)

prompt = "张三，35岁，喜欢阅读、游泳和旅行。邮箱是 zhangsan@example.com"
result = structured_model.invoke(prompt)

print(f"提示词: {prompt}")
print(f"\n解析结果:")
print(f"  姓名: {result.name}")
print(f"  年龄: {result.age}")
print(f"  爱好: {result.hobbies}")
print(f"  邮箱: {result.email}")
print(f"  类型: {type(result)}")

# ============================================================
# 3. 实际应用场景
# ============================================================
print("\n3. 实际应用场景")
print("-" * 30)

print("""
结构化输出的典型应用：

1. 表单提取
   从自然语言中提取表单数据

2. 数据抽取
   从文本中抽取结构化信息

3. API 响应格式化
   生成符合规范的 API 响应

4. 代码生成
   生成符合 Schema 的代码
""")

# ============================================================
# 【补充】Function Calling 原理
# ============================================================
print("\n" + "=" * 50)
print("with_structured_output 底层原理")
print("=" * 50)
print("""
底层使用 Function Calling：

1. Pydantic 模型 → JSON Schema
2. 将 schema 发送给模型，告知输出格式
3. 模型输出符合格式的 JSON
4. LangChain 解析 JSON → Pydantic 对象

优势：
- 比纯 prompt 更可靠
- 类型安全
- 自动验证

注意：
- 需要模型支持 Function Calling
- 通义千问 qwen3-max 支持
""")
