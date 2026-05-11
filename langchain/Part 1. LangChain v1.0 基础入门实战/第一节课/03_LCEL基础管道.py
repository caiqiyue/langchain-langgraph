# -*- coding: utf-8 -*-
"""
【案例 3】LCEL 管道组合基础
==========================================

本案例展示 LCEL（LangChain Expression Language）的核心用法
LCEL 通过 | 运算符将多个 Runnable 组合成链

要点：
1. 什么是 LCEL
2. | 管道运算符的原理
3. 三大组件：PromptTemplate + ChatModel + OutputParser
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
print("案例 3: LCEL 管道组合基础")
print("=" * 50)

# ============================================================
# 1. LCEL 三大组件
# ============================================================
"""
【LCEL 核心组件】

1. PromptTemplate: 定义提示词模板
   - 输入：dict（包含变量）
   - 输出：消息列表

2. ChatModel: 大语言模型
   - 输入：消息列表
   - 输出：AIMessage

3. OutputParser: 输出解析器
   - 输入：AIMessage
   - 输出：str / dict / Pydantic Model
"""

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建三大组件
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的翻译专家。"),
    ("human", "把以下中文翻译成英文：{text}")
])

model = ChatTongyi(model="qwen3-max", temperature=0.3)

parser = StrOutputParser()

# ============================================================
# 2. 使用 | 运算符组合成链
# ============================================================
"""
【| 运算符原理】

chain = prompt | model | parser

等价于：
result = parser.invoke(model.invoke(prompt.invoke(input)))

数据流向：
input (dict) → prompt.invoke() → messages → model.invoke() → AIMessage → parser.invoke() → output (str)
"""

chain = prompt | model | parser

print(f"\n链结构: prompt | model | parser")
print(f"链类型: {type(chain)}")

# 调用链
input_data = {"text": "今天天气真好"}
result = chain.invoke(input_data)

print(f"\n输入: {input_data}")
print(f"输出: {result}")

# ============================================================
# 3. LCEL 的等价手动实现
# ============================================================
"""
【拓展：LCEL 内部执行流程】

当调用 chain.invoke(input) 时，LangChain 内部执行：

Step 1: prompt.invoke({"text": "今天天气真好"})
        ↓
        [SystemMessage(...), HumanMessage("翻译：今天天气真好")]

Step 2: model.invoke([SystemMessage, HumanMessage])
        ↓
        AIMessage(content="The weather is nice today")

Step 3: parser.invoke(AIMessage)
        ↓
        "The weather is nice today"
"""

print("\n" + "-" * 30)
print("LCEL 内部执行流程（等价手动实现）")
print("-" * 30)

# Step 1
step1 = prompt.invoke({"text": "你好世界"})
print(f"Step 1 - prompt.invoke():")
print(f"  类型: {type(step1)}")
print(f"  内容: {step1}")

# Step 2
step2 = model.invoke(step1)
print(f"\nStep 2 - model.invoke():")
print(f"  类型: {type(step2)}")
print(f"  内容: {step2}")

# Step 3
step3 = parser.invoke(step2)
print(f"\nStep 3 - parser.invoke():")
print(f"  类型: {type(step3)}")
print(f"  内容: {step3}")

# 验证结果一致
assert result == step3, "结果不一致！"
print("\n✅ LCEL 链执行结果与手动执行完全一致")
