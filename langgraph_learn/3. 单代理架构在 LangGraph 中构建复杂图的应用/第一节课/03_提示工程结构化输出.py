"""
03_提示工程结构化输出
演示通过提示工程让大模型生成特定格式输出
"""
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")

# 创建提示模板，要求模型以JSON格式输出
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json`",
        ),
        ("human", "{query}"),
    ]
)

# 创建链
chain = prompt | llm

# 测试：提取用户信息
ans = chain.invoke({"query": "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052"})

print("提示工程输出结果：")
print(ans.content)