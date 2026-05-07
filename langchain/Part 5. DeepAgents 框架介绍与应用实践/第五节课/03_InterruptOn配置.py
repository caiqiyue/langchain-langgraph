# -*- coding: utf-8 -*-
"""
【案例 3】interrupt_on 配置
=============================

本案例展示 DeepAgents 的 Human-in-the-Loop (HITL) 配置。

interrupt_on 参数：
- 类型：dict[str, bool | InterruptOnConfig]
- 作用：控制何时中断执行等待人工审批

使用场景：
1. 安全审核（删除文件）
2. 成本控制（调用昂贵 API）
3. 质量保证（人工确认）

审批操作：
- ApproveDecision：批准继续执行
- RejectDecision：拒绝并停止
- EditDecision：编辑后继续

要点：
1. 理解 HITL 的作用
2. 掌握 interrupt_on 配置
3. 学会实现人工审批流程
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 3: interrupt_on 配置")
print("=" * 60)

# ============================================================
# 2. interrupt_on 概述
# ============================================================
print("\n【interrupt_on 概述】")
print("-" * 50)

print("""
interrupt_on 是 HITL（Human-in-the-Loop）开关：

- 类型：dict[str, bool | InterruptOnConfig]
- 映射"工具名称"到"中断配置"
- 当 Agent 调用指定工具时暂停执行
- 等待人工审批后才能继续

典型使用：
  interrupt_on={"write_file": True}
  # 当 Agent 试图调用 write_file 时中断
""")

# ============================================================
# 3. 配置示例
# ============================================================
print("\n【配置示例】")
print("-" * 50)

print("""
from langgraph.checkpoint.memory import InMemorySaver
from langchain_tavily import TavilySearch

# 创建 Agent，配置中断
agent = create_deep_agent(
    model=llm,
    tools=[TavilySearch(max_results=2)],
    backend=FilesystemBackend(root_dir="./workspace"),
    checkpointer=InMemorySaver(),  # 必须！支持中断和恢复
    interrupt_on={
        "write_file": True,     # 写入文件时中断
        "tavily_search": True, # 搜索时中断
    }
)
""")

# ============================================================
# 4. 审批操作
# ============================================================
print("\n【审批操作】")
print("-" * 50)

print("""
审批操作类型：

1. ApproveDecision
   - 批准操作继续执行

2. RejectDecision
   - 拒绝操作，停止执行

3. EditDecision
   - 编辑参数后继续执行

使用示例：

from langchain.agents.middleware.human_in_the_loop import (
    HITLResponse,
    ApproveDecision,
    RejectDecision,
    EditDecision
)

# 批准
hitl_response = HITLResponse(
    decisions=[ApproveDecision(type="approve")]
)

# 拒绝
hitl_response = HITLResponse(
    decisions=[RejectDecision(reason="内容不合适")]
)

# 恢复执行
async for event in agent.astream(
    Command(resume=hitl_response),
    config=config
):
    ...
""")

# ============================================================
# 5. 完整流程
# ============================================================
print("\n【完整流程】")
print("-" * 50)

流程图 = """
┌─────────────────────────────────────────────────────────┐
│                    HITL 完整流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   1. Agent.invoke() 执行                               │
│          ↓                                              │
│   2. 遇到配置了 interrupt_on 的工具调用                   │
│          ↓                                              │
│   3. 执行暂停（Suspend）                                │
│          ↓                                              │
│   4. 人工介入审查                                        │
│          ↓                                              │
│   5a. 批准 → 继续执行                                   │
│   5b. 拒绝 → 停止                                       │
│   5c. 编辑 → 修改参数后继续                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
"""
print(流程图)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)