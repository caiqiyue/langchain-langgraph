# -*- coding: utf-8 -*-
"""
【案例 5】langchain-openai 厂商深度集成
==========================================

本案例展示 langchain-openai 包的用法
官方维护，更新及时，功能完整

要点：
1. ChatOpenAI 的高级功能
2. OpenAIEmbeddings
3. 厂商包 vs community 包
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 50)
print("案例 5: langchain-openai 厂商深度集成")
print("=" * 50)

# ============================================================
# 1. ChatOpenAI 基础用法
# ============================================================
print("\n1. ChatOpenAI 基础用法")
print("-" * 30)
print("""
langchain-openai 封装了 OpenAI 的 API：

ChatOpenAI 参数：
- model: 模型名称（gpt-4o, gpt-4o-mini, gpt-3.5-turbo 等）
- temperature: 随机性
- max_tokens: 最大生成 token 数
- timeout: 超时时间
- api_key: API 密钥

注意：实际使用需要 OPENAI_API_KEY 环境变量
""")

# ============================================================
# 2. 厂商包支持的功能
# ============================================================
print("\n2. 厂商包支持的功能")
print("-" * 30)
print("""
langchain-openai 支持 OpenAI 的最新特性：

1. response_format - JSON 模式
   response = ChatOpenAI(
       model="gpt-4o",
       response_format={"type": "json_object"}
   )

2. seed - 确定性输出
   response = ChatOpenAI(
       model="gpt-4o",
       seed=42
   )

3. logprobs - 获取概率
   response = ChatOpenAI(
       model="gpt-4o",
       logprobs=True,
       top_logprobs=5
   )

4. tools / tool_choice - 函数调用
   model.bind_tools([tool1, tool2])
""")

# ============================================================
# 3. 与 community 包对比
# ============================================================
print("\n3. 与 community 包对比")
print("-" * 30)

print("""
| 维度       | langchain-openai (官方) | langchain-community |
|------------|------------------------|---------------------|
| 维护方     | OpenAI + LangChain 团队 | 社区维护            |
| 更新       | 即时跟进 API 更新        | 延迟数周            |
| 功能       | 所有新特性              | 基础功能            |
| 可靠性     | 高                     | 中                  |
| 生产推荐   | ✅                     | ⚠️                 |
""")

print("\n建议：生产环境使用官方包，开发环境可用 community 包快速验证")
