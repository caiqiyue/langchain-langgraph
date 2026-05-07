# -*- coding: utf-8 -*-
"""
【案例 5】ModelFallbackMiddleware - 模型故障自动切换
=====================================================

本案例展示如何使用 ModelFallbackMiddleware 实现模型故障自动切换，
当主模型调用失败时自动尝试备用模型。

核心特性：
1. 自动故障转移：主模型失败时切换到备用模型
2. 多级备份：支持配置多个备用模型
3. 无缝切换：对业务逻辑透明
4. 提高可用性：显著提升系统稳定性

要点：
1. 理解故障转移的重要性
2. 掌握 ModelFallbackMiddleware 配置
3. 理解多级备份的设计
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
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.tools import tool
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 5: ModelFallbackMiddleware 模型故障切换")
print("=" * 60)

# ============================================================
# 3. 定义工具
# ============================================================
@tool
def calculate_sum(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

@tool
def get_system_info() -> str:
    """获取系统信息"""
    return "系统运行正常，CPU使用率: 45%, 内存使用率: 60%"

tools = [calculate_sum, get_system_info]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 ModelFallbackMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

# 配置模型故障转移：主模型 -> 备用模型1 -> 备用模型2
fallback_middleware = ModelFallbackMiddleware(
    # 第一个备用模型
    ChatDeepSeek(model="deepseek-chat", temperature=0.3),
    # 第二个备用模型
    ChatDeepSeek(model="deepseek-reasoner", temperature=0.5),
)

print("故障转移链：")
print("  主模型: deepseek-chat (temperature=0.1)")
print("  备用1:  deepseek-chat (temperature=0.3)")
print("  备用2:  deepseek-reasoner (temperature=0.5)")

# ============================================================
# 6. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【调用流程】

用户请求
    │
    ▼
┌─────────────────┐
│  主模型调用      │
│ deepseek-chat   │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 成功？   │
    └────┬────┘
    是/     \\否
    │        │
    ▼        ▼
 返回结果  ┌─────────────────┐
          │ 备用模型 1 调用  │
          │ deepseek-chat   │
          └────────┬────────┘
                   │
              ┌────┴────┐
              │ 成功？   │
              └────┬────┘
              是/     \\否
              │        │
              ▼        ▼
           返回结果  ┌─────────────────┐
                    │ 备用模型 2 调用  │
                    │ deepseek-reasoner│
                    └────────┬────────┘
                             │
                        ┌────┴────┐
                        │ 成功？   │
                        └────┬────┘
                        是/     \\否
                        │        │
                        ▼        ▼
                    返回结果   抛出异常
""")

# ============================================================
# 7. 典型应用场景
# ============================================================
print("\n【典型应用场景】")
print("-" * 50)

场景说明 = """
| 场景                  | 推荐配置                        |
|---------------------|-------------------------------|
| 单一模型不稳定        | 主模型 + 1个备用（同提供商）    |
| 多地区部署           | 主模型 + 多地区备用模型         |
| 成本优化             | 主力模型 + 轻量备用模型         |
| 高可用系统           | 多级备用（不同提供商）          |
"""
print(场景说明)

print("\n【生产环境建议】")
print("-" * 50)
print("""
推荐配置不同提供商的模型：
  主模型:  openai:gpt-4o
  备用1:  anthropic:claude-sonnet-4-5-20250929
  备用2:  deepseek:deepseek-chat

这样可以确保：
  1. 一个提供商服务中断时，自动切换到其他提供商
  2. 保持服务可用性
  3. 减少服务中断时间
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)