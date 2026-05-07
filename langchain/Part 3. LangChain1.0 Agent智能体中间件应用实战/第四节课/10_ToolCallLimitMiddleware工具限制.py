# -*- coding: utf-8 -*-
"""
【案例 10】ToolCallLimitMiddleware - 工具调用限制中间件
======================================================

本案例展示如何使用 ToolCallLimitMiddleware 限制 Agent 的工具调用次数，
防止工具被滥用或过度消耗资源。

核心特性：
1. 资源保护：防止特定工具被频繁调用
2. 灵活配置：支持全局限制或特定工具限制
3. 自动熔断：达到限制后阻止执行
4. 可追溯：记录调用次数用于监控

要点：
1. 理解全局限制 vs 特定工具限制
2. 掌握 run_limit 和 thread_limit 配置
3. 理解 exit_behavior 的两种模式
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
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import ensure_config
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 10: ToolCallLimitMiddleware 工具调用限制")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def check_server_status(server_id: str) -> str:
    """检查服务器状态"""
    return f"服务器 {server_id} 运行正常，负载 45%"

@tool
def restart_server(server_id: str) -> str:
    """重启服务器（高消耗操作）"""
    return f"服务器 {server_id} 已重启"

tools = [check_server_status, restart_server]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 两种限制方式
# ============================================================
print("\n【两种限制方式】")
print("-" * 50)

# 方式1: 全局限制
global_limiter = ToolCallLimitMiddleware(
    tool_name=None,  # None = 限制所有工具
    run_limit=5,  # 每次运行最多 5 次工具调用
    exit_behavior="continue"
)
print("【全局限制】")
print(f"  tool_name: None（所有工具）")
print(f"  run_limit: 5")
print(f"  exit_behavior: continue")

# 方式2: 特定工具限制
specific_limiter = ToolCallLimitMiddleware(
    tool_name="restart_server",  # 只限制此工具
    thread_limit=10,  # 整个线程最多 10 次
    run_limit=2,  # 每次运行最多 2 次
    exit_behavior="error"
)
print("\n【特定工具限制】")
print(f"  tool_name: restart_server")
print(f"  thread_limit: 10（线程级别）")
print(f"  run_limit: 2（运行级别）")
print(f"  exit_behavior: error")

# ============================================================
# 6. 参数对比
# ============================================================
print("\n【参数详解】")
print("-" * 50)

参数说明 = """
| 参数          | 类型   | 说明                          |
|-------------|------|------------------------------|
| tool_name   | str  | 工具名称，None 表示全局限制    |
| run_limit   | int  | 每次运行的限制                 |
| thread_limit| int  | 整个线程的限制                 |
| exit_behavior| str | 'error' 或 'continue'         |
"""
print(参数说明)

# ============================================================
# 7. 限制级别对比
# ============================================================
print("\n【限制级别对比】")
print("-" * 50)

级别说明 = """
| 级别      | 作用域              | 重置时机        | 用途              |
|----------|-------------------|---------------|-----------------|
| run_limit | 单次 invoke/stream | 每次调用时     | 防止单次请求滥用  |
| thread_limit| 整个 thread_id  | 永不过期        | 防止长期累积滥用  |
"""
print(级别说明)

# ============================================================
# 8. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【场景】用户连续请求重启多台服务器

用户输入：
┌─────────────────────────────────────────────────┐
│ 请帮我重启 Server-A、Server-B、Server-C、Server-D │
└─────────────────────────────────────────────────┘

【执行过程】（配置 run_limit=2）

调用 1: restart_server("Server-A") ✓ 成功
调用 2: restart_server("Server-B") ✓ 成功
调用 3: restart_server("Server-C") ✗ 被拦截！
    → ToolCallLimitMiddleware 触发
    → 阻止调用，返回错误或继续执行

【结果】
  - Server-A 和 Server-B 已重启
  - Server-C 和 Server-D 未执行
  - 避免了资源过度消耗
""")

# ============================================================
# 9. 典型应用场景
# ============================================================
print("\n【典型应用场景】")
print("-" * 50)

场景说明 = """
| 场景              | 配置建议                          |
|-----------------|---------------------------------|
| 高消耗工具限制     | tool_name='restart_server', run_limit=2 |
| 全局防滥用        | tool_name=None, run_limit=10    |
| 线程级别长期限制   | tool_name=None, thread_limit=100 |
| 关键操作保护       | tool_name='delete', run_limit=1  |
"""
print(场景说明)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)