# -*- coding: utf-8 -*-
"""
【案例 8】LLMToolEmulator - LLM 工具模拟中间件
==============================================

本案例展示如何使用 LLMToolEmulator 使用 LLM 模拟工具执行，
在不执行真实操作的情况下测试 Agent 逻辑。

核心特性：
1. LLM 模拟执行：使用 LLM 生成模拟结果
2. 选择性模拟：可指定模拟哪些工具
3. 安全测试：避免执行危险操作
4. 快速原型：无需实现真实工具即可测试

要点：
1. 理解 LLMToolEmulator 的使用场景
2. 掌握 tools 参数配置
3. 理解模拟 vs 真实执行的区别
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 2. 导入 LangChain 核心组件
# ============================================================
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain_core.tools import tool
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 8: LLMToolEmulator LLM 工具模拟")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def send_real_email(recipient: str, subject: str, body: str) -> str:
    """
    发送真实邮件（在测试中会被模拟）
    """
    print(f"[真实执行] 发送邮件到 {recipient}")
    return f"真实邮件已发送给 {recipient}"

@tool
def charge_credit_card(card_number: str, amount: float) -> str:
    """
    真实扣款（在测试中会被模拟）
    """
    print(f"[真实执行] 从卡号 {card_number} 扣款 ${amount}")
    return f"已扣款 ${amount}"

@tool
def delete_database_record(record_id: str) -> str:
    """
    删除数据库记录（在测试中会被模拟）
    """
    print(f"[真实执行] 删除记录 {record_id}")
    return f"已删除 {record_id}"

@tool
def safe_query_tool(query: str) -> str:
    """
    安全的查询工具（不会被模拟）
    """
    print(f"[真实执行] 查询: {query}")
    return f"查询结果: 找到关于 '{query}' 的 5 条记录"

tools = [send_real_email, charge_credit_card, delete_database_record, safe_query_tool]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 LLMToolEmulator
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

emulator_middleware = LLMToolEmulator(
    tools=["send_real_email", "charge_credit_card", "delete_database_record"],
    model=ChatDeepSeek(model="deepseek-chat", temperature=0.7),
)

print("模拟工具列表：")
print("  - send_real_email（发送邮件）")
print("  - charge_credit_card（扣款）")
print("  - delete_database_record（删除数据）")
print()
print("真实执行工具：")
print("  - safe_query_tool（安全查询）")

# ============================================================
# 6. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【模拟执行流程】

用户请求: "请发送邮件到 test@example.com"
    │
    ▼
┌─────────────────────────────────┐
│  Agent 决定调用 send_email      │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  LLMToolEmulator 拦截           │
│  (wrap_tool_call 阶段)          │
│                                 │
│  检测到 send_email 在模拟列表中 │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  LLM 生成模拟结果               │
│  model=deepseek-chat            │
│  生成合理的模拟返回              │
└─────────────────────────────────┘
    │
    ▼
返回: "邮件已成功发送给 test@example.com"
    （而不是真实发送邮件）

【对比：真实执行】
用户请求: "请查询用户信息"
    │
    ▼
┌─────────────────────────────────┐
│  safe_query_tool               │
│  不在模拟列表中                 │
└─────────────────────────────────┘
    │
    ▼
真实执行查询逻辑
    │
    ▼
返回真实查询结果
""")

# ============================================================
# 7. 使用场景
# ============================================================
print("\n【使用场景】")
print("-" * 50)

场景说明 = """
| 场景              | 说明                                |
|------------------|-------------------------------------|
| 测试环境          | 避免执行危险操作（删除、扣款等）      |
| 快速原型          | 无需实现真实工具即可测试 Agent 流程   |
| 演示系统          | 展示功能而不触发真实操作             |
| 开发调试          | 在开发阶段模拟外部 API 调用          |
"""
print(场景说明)

print("\n【最佳实践】")
print("-" * 50)
print("""
1. 在测试环境中模拟所有危险操作
2. 在生产环境中移除模拟中间件
3. 使用环境变量控制是否启用模拟
4. 模拟结果应该尽可能接近真实结果
5. 记录哪些工具被模拟（用于日志）
""")

# ============================================================
# 8. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

# 配置中间件
emulator = LLMToolEmulator(
    tools=["send_email", "charge_credit_card", "delete_record"],
    model=ChatDeepSeek(model="deepseek-chat", temperature=0.7),
)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[emulator],
    context_schema=UserContext,
)

# 执行（危险工具被模拟）
result = agent.invoke({
    "messages": [HumanMessage(content="请发送邮件到 test@example.com")]
})
# → 不会真实发送邮件，LLM 生成模拟结果
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)