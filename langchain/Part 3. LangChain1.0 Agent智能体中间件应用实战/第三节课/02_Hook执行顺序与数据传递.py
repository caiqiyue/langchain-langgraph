# -*- coding: utf-8 -*-
"""
【案例 2】中间件六大 Hook 执行顺序 - 深入生命周期
==================================================

中间件的 6 个 Hook 点构成完整的生命周期：

1. before_agent    - Agent 执行前最后机会修改输入
2. before_model   - 模型调用前修改 prompt / 选择模型
3. wrap_model_call - 包裹模型调用（异常处理、重试）
4. wrap_tool_call  - 包裹工具调用（异常处理、重试）
5. after_model    - 模型调用后修改输出
6. after_agent    - Agent 执行完成后的最终处理

要点：
1. 理解六大 Hook 的执行顺序和职责
2. 掌握数据在 Hook 间的传递机制
3. 理解元数据传递和状态管理
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
from langchain.agents.middleware import (
    AgentMiddleware,
    hook_config,
    ModelRequest,
    ModelResponse,
    wrap_model_call
)
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Callable, List

print("=" * 60)
print("案例 2: 中间件六大 Hook 执行顺序")
print("=" * 60)

# ============================================================
# 3. Hook 执行顺序图示
# ============================================================
print("""
    ┌─────────────────────────────────────────────────────────┐
    │                    Agent 执行流程                        │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │   ┌───────────────┐                                    │
    │   │  before_agent │  ← 第1步：全局初始化、安全检查       │
    │   └───────┬───────┘                                    │
    │           ↓                                            │
    │   ┌───────────────┐                                    │
    │   │  before_model │  ← 第2步：输入预处理、预算检查       │
    │   └───────┬───────┘                                    │
    │           ↓                                            │
    │   ┌───────────────┐     ┌───────────────┐              │
    │   │ wrap_model_call│ ←→ │  模型实际调用  │              │
    │   └───────┬───────┘     └───────────────┘              │
    │           ↓                                            │
    │   ┌───────────────┐     ┌───────────────┐              │
    │   │ wrap_tool_call │ ←→ │  工具实际执行  │              │
    │   └───────┬───────┘     └───────────────┘              │
    │           ↓                                            │
    │   ┌───────────────┐                                    │
    │   │  after_model  │  ← 第5步：输出验证、格式转换        │
    │   └───────┬───────┘                                    │
    │           ↓                                            │
    │   ┌───────────────┐                                    │
    │   │  after_agent  │  ← 第6步：资源清理、生成报告        │
    │   └───────────────┘                                    │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
""")

# ============================================================
# 4. 各 Hook 详细说明
# ============================================================

# ----- 4.1 before_agent -----
print("\n" + "-" * 50)
print("【Hook 1】before_agent - Agent 执行前的最后机会")
print("-" * 50)
print("""
职责：
  - 全局状态初始化
  - 环境配置检查
  - 安全检查（危险操作拦截）
  - 权限验证

特点：
  - 可跳转到 'end' 提前终止执行
  - 是执行顺序中最先执行的 Hook
  - 适合放安全检查、身份验证等

示例场景：
  - 检测用户是否登录
  - 检查 API Key 是否配置
  - 拦截危险操作关键词
""")

# ----- 4.2 before_model -----
print("\n" + "-" * 50)
print("【Hook 2】before_model - 模型调用前的预处理")
print("-" * 50)
print("""
职责：
  - 输入数据预处理、验证、清洗
  - 选择模型（路由到不同模型）
  - 注入动态 System Prompt
  - Token 预算检查

特点：
  - 在模型实际调用前执行
  - 可以修改 messages、选择模型
  - 适合放输入验证、预算控制等

示例场景：
  - SummarizationMiddleware 压缩历史消息
  - PIIMiddleware 脱敏处理
  - 根据用户等级选择不同模型
""")

# ----- 4.3 wrap_model_call -----
print("\n" + "-" * 50)
print("【Hook 3】wrap_model_call - 包裹模型调用的核心逻辑")
print("-" * 50)
print("""
职责：
  - 包装模型调用的完整过程
  - 实现缓存、重试、熔断逻辑
  - 动态修改模型或参数
  - 异常处理和超时控制

特点：
  - 嵌套结构：before → actual → after
  - 可访问 ModelRequest 中的所有数据
  - 是实现高级功能的核心 Hook

示例场景：
  - ModelFallbackMiddleware 故障自动切换
  - LLMToolSelectorMiddleware 智能选择工具
  - 缓存中间件避免重复调用
""")

# ----- 4.4 wrap_tool_call -----
print("\n" + "-" * 50)
print("【Hook 4】wrap_tool_call - 包裹工具调用的执行")
print("-" * 50)
print("""
职责：
  - 拦截和控制工具的实际执行
  - 参数验证、权限检查
  - 重试逻辑、日志记录
  - 人工审批拦截

特点：
  - 嵌套结构：before → actual → after
  - 可修改工具参数
  - 可拦截工具执行

示例场景：
  - ToolRetryMiddleware 自动重试失败工具
  - HumanInTheLoopMiddleware 人工审批
  - LLMToolEmulator LLM模拟工具执行
""")

# ----- 4.5 after_model -----
print("\n" + "-" * 50)
print("【Hook 5】after_model - 模型调用后的处理")
print("-" * 50)
print("""
职责：
  - 处理模型返回的原始结果
  - 验证输出质量
  - 格式转换、信息提取
  - 审计日志记录

特点：
  - 在模型调用返回后执行
  - 只能读取 state，不能修改 request
  - 适合放输出验证、审计日志

示例场景：
  - ResponseValidator 验证响应格式
  - AuditLogger 记录操作日志
  - 提取关键信息进行后处理
""")

# ----- 4.6 after_agent -----
print("\n" + "-" * 50)
print("【Hook 6】after_agent - Agent 执行完成的收尾工作")
print("-" * 50)
print("""
职责：
  - 清理系统资源
  - 记录最终状态
  - 生成执行报告
  - 持久化会话数据

特点：
  - 整个生命周期的最后一步
  - 保证系统处于良好状态
  - 为下一次请求做准备

示例场景：
  - persist_session 会话持久化
  - 生成执行摘要报告
  - 资源释放和连接池清理
""")

# ============================================================
# 5. 数据传递机制
# ============================================================
print("\n" + "=" * 60)
print("Hook 间数据传递机制")
print("=" * 60)

print("""
中间件 Hook 间通过两种机制传递数据：

1. AgentState（全局状态容器）
   - 贯穿整个 Agent 执行流程
   - 跨多次模型调用持久化
   - 类似 Redux Store
   - 来源：before_agent, before_model, after_model 等

2. ModelRequest/Response（单次调用）
   - 仅作用于单次模型/工具调用
   - 包含当前调用的具体参数
   - 可直接修改（框架特批）
   - 来源：wrap_model_call, wrap_tool_call

对比表：
|-----------|-----------------------------------|------------------|
| 类型       | ModelRequest/Response             | AgentState       |
|-----------|-----------------------------------|------------------|
| 作用域     | 单次模型调用                      | 整个 Agent 会话   |
| 生命周期   | 瞬态                              | 持久化            |
| 可修改性   | 可直接赋值修改                    | 通过返回值更新    |
| 典型来源   | wrap_model_call, wrap_tool_call   | before_agent等   |
|-----------|-----------------------------------|------------------|
""")

# ============================================================
# 6. 自定义中间件示例
# ============================================================
print("\n" + "=" * 60)
print("自定义中间件示例")
print("=" * 60)

class DemoMiddleware(AgentMiddleware):
    """演示中间件 - 在各 Hook 点打印日志"""

    def __init__(self):
        super().__init__()
        self.call_order = []

    def before_agent(self, state, runtime) -> Optional[Dict[str, Any]]:
        """第1步：before_agent"""
        self.call_order.append("before_agent")
        print(">>> [Hook 1] before_agent - Agent 执行前检查")
        return None

    def before_model(self, state, runtime) -> Optional[Dict[str, Any]]:
        """第2步：before_model"""
        self.call_order.append("before_model")
        print(">>> [Hook 2] before_model - 模型调用前处理")
        return None

    def after_model(self, state, runtime) -> Optional[Dict[str, Any]]:
        """第5步：after_model"""
        self.call_order.append("after_model")
        print(">>> [Hook 5] after_model - 模型调用后处理")
        return None

    def after_agent(self, state, runtime) -> Optional[Dict[str, Any]]:
        """第6步：after_agent"""
        self.call_order.append("after_agent")
        print(">>> [Hook 6] after_agent - Agent 执行完成")
        return None

@wrap_model_call
def demo_wrap_model(request: ModelRequest, handler: Callable) -> ModelResponse:
    """第3步：wrap_model_call"""
    print(">>> [Hook 3] wrap_model_call - 包裹模型调用（开始）")
    response = handler(request)
    print(">>> [Hook 3] wrap_model_call - 包裹模型调用（结束）")
    return response

print("\n【执行顺序验证】")
demo_middleware = DemoMiddleware()
print(f"注册的 Hook: {demo_middleware.call_order}")
print("\n说明：")
print("  1. before_agent 最先执行（正序）")
print("  2. before_model 次之（正序）")
print("  3. wrap_model_call 嵌套执行")
print("  4. after_model 最后执行（逆序）")
print("  5. after_agent 最后执行（逆序）")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)