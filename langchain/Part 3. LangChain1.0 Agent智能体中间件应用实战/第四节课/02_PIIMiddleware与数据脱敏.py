# -*- coding: utf-8 -*-
"""
【案例 2】PIIMiddleware - 个人身份信息脱敏中间件
==================================================

本案例展示如何使用 PIIMiddleware 自动检测和脱敏个人身份信息（PII），
保护用户隐私和数据安全。

核心特性：
1. 自动 PII 检测：支持多种 PII 类型
2. 智能脱敏：block/redact/mask/hash 四种策略
3. 灵活配置：可针对不同字段应用不同策略
4. 无缝集成：在模型调用前自动处理

支持的 PII 类型：
- email：电子邮件地址
- credit_card：信用卡号
- ip：IP 地址
- phone：电话号码
- ssn：社会保障号

要点：
1. 理解 PII 脱敏的应用场景
2. 掌握四种脱敏策略的区别
3. 学会配置 PIIMiddleware
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
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
import re

print("=" * 60)
print("案例 2: PIIMiddleware 个人身份信息脱敏")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def verify_credit_card(card_number: str) -> dict:
    """验证信用卡号有效性（模拟）"""
    print(f"工具接收到的卡号: {card_number}")
    if len(card_number) >= 16:
        return {"is_valid": True, "card_type": "Visa", "masked_card": card_number}
    return {"is_valid": False}

@tool
def process_payment(card_number: str, amount: float) -> str:
    """处理信用卡支付（模拟）"""
    print(f"支付工具接收到的卡号: {card_number}")
    return f"支付成功！金额: ${amount}, 卡号: {card_number}"

@tool
def search_user_history(user_id: str) -> str:
    """查询用户历史记录"""
    return f"用户 {user_id} 的历史订单：订单123, 订单456"

tools = [verify_credit_card, process_payment, search_user_history]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")
    department: str = Field(..., description="所属部门")
    security_level: str = Field(default="normal", description="安全级别")

# ============================================================
# 5. 四种脱敏策略对比
# ============================================================
print("\n【四种脱敏策略】")
print("-" * 50)

test_data = "我的银行卡号是 4532-1234-5678-9010"

策略对比 = """
| 策略      | 效果示例                            | 适用场景           |
|----------|------------------------------------|-------------------|
| block    | 阻止包含PII的消息                   | 高安全要求场景     |
| redact   | 我的银行卡号是 [REDACTED]           | 完全移除敏感信息   |
| mask     | 我的银行卡号是 ****-****-****-9010 | 显示部分，隐藏大部分|
| hash     | 我的银行卡号是 a1b2c3d4...          | 可逆脱敏（需密钥） |
"""
print(策略对比)

print(f"\n原始数据: {test_data}")
print("\n各策略效果：")
print(f"  block:  [消息被阻止]")
print(f"  redact:  我的银行卡号是 [REDACTED]")
print(f"  mask:    我的银行卡号是 ****-****-****-9010")
print(f"  hash:    我的银行卡号是 7f8a9b2c...")

# ============================================================
# 6. 配置 PIIMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

# 信用卡掩码中间件
piim_credit_card = PIIMiddleware(
    "credit_card",
    detector=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # 匹配格式: 1234-5678-9012-3456
    strategy="mask",  # 掩码策略
    apply_to_input=True,
    apply_to_output=False,
)

# 邮箱脱敏中间件
piim_email = PIIMiddleware(
    "email",
    detector=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    strategy="redact",
    apply_to_input=True,
    apply_to_output=True,
)

print("【信用卡掩码配置】")
print(f"  detector: \\b(?:\\d{{4}}[-\\s]?){{3}}\\d{{4}}\\b")
print(f"  strategy: mask")
print(f"  apply_to_input: True")
print(f"  apply_to_output: False")

print("\n【邮箱脱敏配置】")
print(f"  detector: \\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\\b")
print(f"  strategy: redact")
print(f"  apply_to_input: True")
print(f"  apply_to_output: True")

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
用户输入（包含敏感信息）：
┌─────────────────────────────────────────────────┐
│ 请帮我验证信用卡 4532-1234-5678-9010，          │
│ 并发送到 test@example.com 确认                 │
└─────────────────────────────────────────────────┘
                        ↓
            ┌─────────────────────┐
            │  PIIMiddleware       │
            │  (before_model)     │
            │                     │
            │  1. 扫描消息内容    │
            │  2. 识别信用卡号    │
            │  3. 应用掩码策略    │
            │  4. 识别邮箱        │
            │  5. 应用脱敏策略    │
            └─────────────────────┘
                        ↓
模型接收（已脱敏）：
┌─────────────────────────────────────────────────┐
│ 请帮我验证信用卡 ****-****-****-9010，          │
│ 并发送到 [REDACTED] 确认                       │
└─────────────────────────────────────────────────┘
""")

# ============================================================
# 8. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

# 配置中间件
piimiddleware = PIIMiddleware(
    "credit_card",
    detector=r"\\b(?:\\d{4}[-\\s]?){3}\\d{4}\\b",
    strategy="mask",
    apply_to_input=True,
    apply_to_output=False,
)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[piimiddleware],
    context_schema=UserContext,
)

# 执行
result = agent.invoke({
    "messages": [HumanMessage(content="我的卡号是 4532-1234-5678-9010")]
})
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)