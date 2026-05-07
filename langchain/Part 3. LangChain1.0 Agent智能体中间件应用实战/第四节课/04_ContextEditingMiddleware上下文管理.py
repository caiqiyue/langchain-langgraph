# -*- coding: utf-8 -*-
"""
【案例 4】ContextEditingMiddleware - 上下文管理中间件
=====================================================

本案例展示如何使用 ContextEditingMiddleware 自动管理上下文大小，
通过清理旧的工具调用结果来防止超出 token 限制。

核心特性：
1. 自动上下文管理：Token 超阈值时自动清理
2. 灵活配置：触发阈值、保留数量、排除工具
3. 智能清理：保留最近的 N 个工具结果
4. 无缝集成：对业务逻辑透明

要点：
1. 理解上下文膨胀的问题
2. 掌握 ClearToolUsesEdit 配置参数
3. 学会使用 exclude_tools 保护重要结果
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
from langchain.agents.middleware import ContextEditingMiddleware
from langchain.agents.middleware.context_editing import ClearToolUsesEdit
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import ensure_config
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 4: ContextEditingMiddleware 上下文管理")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def search_database(query: str) -> str:
    """搜索数据库并返回大量结果"""
    result = f"搜索 '{query}' 的结果：\n"
    result += "\n".join([f"记录 {i}: 这是关于 {query} 的详细信息..." * 5 for i in range(10)])
    return result

@tool
def analyze_data(data_id: str) -> str:
    """分析数据并返回详细报告"""
    result = f"数据 {data_id} 的分析报告：\n"
    result += "详细分析内容包括统计数据、趋势分析..." * 20
    return result

@tool
def generate_report(topic: str) -> str:
    """生成报告（重要操作，不应被清理）"""
    result = f"关于 '{topic}' 的报告：\n"
    result += "报告内容包括背景介绍、现状分析、未来展望..."
    return result

tools = [search_database, analyze_data, generate_report]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 ContextEditingMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

custom_context_middleware = ContextEditingMiddleware(
    edits=[
        ClearToolUsesEdit(
            trigger=800,  # Token 超过 800 时触发
            keep=1,  # 只保留最近 1 个工具结果
            clear_at_least=0,
            clear_tool_inputs=False,  # 不清理工具输入参数
            exclude_tools=["generate_report"],  # 重要操作不清理
            placeholder="[已清理以节省空间]",
        )
    ],
    token_count_method="approximate"  # 使用近似计数（更快）
)

print("ClearToolUsesEdit 配置：")
print(f"  trigger: 800 tokens（超过此值触发清理）")
print(f"  keep: 1（保留最近 1 个工具结果）")
print(f"  exclude_tools: ['generate_report']（重要操作不清理）")
print(f"  placeholder: '[已清理以节省空间]'")

# ============================================================
# 6. ClearToolUsesEdit 参数详解
# ============================================================
print("\n【ClearToolUsesEdit 参数详解】")
print("-" * 50)

参数说明 = """
| 参数               | 类型    | 默认值        | 说明                      |
|------------------|--------|--------------|-------------------------|
| trigger          | int    | 100000       | 触发清理的 token 阈值     |
| keep             | int    | 3            | 保留最近的 N 个工具结果   |
| clear_at_least    | int    | 0            | 最少清理的 token 数量     |
| clear_tool_inputs | bool   | False        | 是否清理工具输入参数       |
| exclude_tools     | list   | []           | 排除不清理的工具列表       |
| placeholder       | str    | "[cleared]"  | 清理后的占位符文本         |
"""
print(参数说明)

# ============================================================
# 7. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【触发前】（5次工具调用，约 1500 tokens）
┌─────────────────────────────────────────────────┐
│ 工具1结果: 搜索 'AI技术' 的结果 (约300tokens)   │
│ 工具2结果: 分析 'dataset_001' 的报告 (约300tokens)│
│ 工具3结果: 搜索 '机器学习' 的结果 (约300tokens)  │
│ 工具4结果: 分析 'dataset_002' 的报告 (约300tokens)│
│ 工具5结果: 生成 '人工智能' 报告 (约300tokens)   │
└─────────────────────────────────────────────────┘
                    ↓
        ┌─────────────────────────┐
        │  ContextEditingMiddleware│
        │  trigger=800, keep=1    │
        │  exclude_tools=[生成报告] │
        └─────────────────────────┘
                    ↓
【触发后】（1次工具调用 + 摘要，约 400 tokens）
┌─────────────────────────────────────────────────┐
│ [已清理以节省空间]                              │
│ [已清理以节省空间]                              │
│ [已清理以节省空间]                              │
│ [已清理以节省空间]                              │
│ 工具5结果: 生成 '人工智能' 报告 (保留，不清理)   │
└─────────────────────────────────────────────────┘

Token 节省：约 73%
""")

# ============================================================
# 8. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware
from langchain.agents.middleware.context_editing import ClearToolUsesEdit

# 配置中间件
context_middleware = ContextEditingMiddleware(
    edits=[
        ClearToolUsesEdit(
            trigger=800,
            keep=1,
            exclude_tools=["generate_report"],
            placeholder="[已清理以节省空间]",
        )
    ],
    token_count_method="approximate"
)

# 创建 Agent（需要 checkpointer 来累积消息）
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[context_middleware],
    context_schema=UserContext,
    checkpointer=MemorySaver(),  # 关键：保存消息历史
    debug=True,
)

# 在同一线程中执行多次查询
config = {"configurable": {"thread_id": "session_001"}}
for query in queries:
    result = agent.invoke(
        {"messages": [HumanMessage(content=query)]},
        context=UserContext(user_id="user_001"),
        config=config
    )
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)