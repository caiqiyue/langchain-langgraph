"""
04_输出解析器结构化输出
演示通过输出解析器从大模型响应中提取结构化数据
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
import json
import re
from typing import List

llm = ChatOpenAI(model="gpt-4o-mini")

# 定义JSON提取函数
def extract_json(message: AIMessage) -> List[dict]:
    """从消息内容中提取JSON数据"""
    text = message.content
    # 定义正则表达式模式匹配JSON块
    pattern = r"\`\`\`json(.*?)\`\`\`"

    # 在字符串中查找模式并返回所有匹配
    matches = re.findall(pattern, text, re.DOTALL)

    # 从匹配到的JSON字符串列表中解析JSON对象
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")

# 创建提示模板
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json`",
        ),
        ("human", "{query}"),
    ]
)

# 创建链：提示 -> LLM -> JSON解析器
chain = prompt | llm | extract_json

# 测试：提取用户信息
ans = chain.invoke({"query": "我叫木羽，今年18岁，邮箱地址是snow@gmial.com，电话是1234567052"})

print("输出解析器结果：")
print(ans)