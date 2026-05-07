# -*- coding: utf-8 -*-
"""
【案例 9】HumanInTheLoopMiddleware - 人工审批中间件
==================================================

本案例展示如何使用 HumanInTheLoopMiddleware 实现人工审批流程，
确保关键操作在执行前得到人工确认。

核心特性：
1. 工具调用拦截：在执行前暂停
2. 灵活审批策略：approve/edit/reject
3. 无缝集成：自动处理中断和恢复逻辑
4. 适用场景：敏感操作、高风险操作

审批决策类型：
- approve：批准执行，使用原始参数
- edit：修改参数后执行
- reject：拒绝执行，返回错误消息

要点：
1. 理解 Human-In-The-Loop 的应用场景
2. 掌握中断和恢复机制
3. 理解三种审批决策的用法
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
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.human_in_the_loop import (
    HITLResponse, ApproveDecision, EditDecision, RejectDecision
)
from langchain_core.tools import tool
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 9: HumanInTheLoopMiddleware 人工审批")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """发送邮件（敏感操作，需要审批）"""
    return f"邮件已成功发送给 {recipient}"

@tool
def query_database(query: str) -> str:
    """查询数据库（普通操作，无需审批）"""
    return f"数据库查询结果: 找到 3 条记录"

tools = [send_email, query_database]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 HumanInTheLoopMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={"send_email": True},  # send_email 需要审批
    description_prefix="需要人工批准才能发送邮件"
)

print("interrupt_on 配置：")
print("  send_email: 需要审批（True）")
print("  query_database: 无需审批（未配置）")

# ============================================================
# 6. 三种审批决策
# ============================================================
print("\n【三种审批决策】")
print("-" * 50)

决策说明 = """
| 决策类型  | 行为                         | 使用场景                |
|----------|-----------------------------|----------------------|
| Approve  | 批准执行，使用原始参数         | 确认操作无误           |
| Edit     | 修改参数后执行                | 需要调整参数            |
| Reject   | 拒绝执行，返回错误消息          | 操作不符合要求          |
"""
print(决策说明)

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【执行流程】

用户请求: "帮我发送邮件到 hr@example.com"
    │
    ▼
┌─────────────────────────────────┐
│  Agent 分析请求                  │
│  决定调用 send_email 工具        │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  HumanInTheLoopMiddleware       │
│  检测到需要审批的工具            │
│  → 触发中断 (interrupt)        │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  等待人工决策                    │
│                                 │
│  【审批界面】                   │
│  工具: send_email               │
│  参数: recipient=hr@example.com │
│          subject=休假申请        │
│          body=下周一想请假        │
│                                 │
│  [批准] [编辑] [拒绝]          │
└─────────────────────────────────┘
    │
    ├──→ [批准] → 执行原始调用
    ├──→ [编辑] → 修改参数后执行
    └──→ [拒绝] → 返回拒绝消息
""")

# ============================================================
# 8. 代码示例
# ============================================================
print("\n【代码示例】")
print("-" * 50)

print("""
# 1. 配置中间件
hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={"send_email": True}
)

# 2. 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[hitl_middleware]
)

# 3. 第一次执行（触发中断）
for event in agent.stream(
    {"messages": [{"role": "user", "content": "发送邮件..."}]},
    config=config
):
    # 检测到中断，暂停执行
    if event.get("interrupt"):
        break

# 4. 获取待审批操作
snapshot = agent.get_state(config)
tool_call = snapshot.values["messages"][-1].tool_calls[0]

# 5. 人工审批
approval = input("是否批准？(y/n/e): ")

# 6. 根据审批结果恢复执行
if approval == "y":
    response = HITLResponse(decisions=[ApproveDecision(type="approve")])
elif approval == "e":
    response = HITLResponse(decisions=[EditDecision(
        type="edit",
        edited_action={"name": "send_email", "args": {...}}
    )])
else:
    response = HITLResponse(decisions=[RejectDecision(
        type="reject",
        message="操作被管理员拒绝"
    )])

# 7. 恢复执行
agent.stream(Command(resume=response), config=config)
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)