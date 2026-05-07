# -*- coding: utf-8 -*-
"""
【案例 1】ModelRequest 与 ModelResponse - 参数传递机制
======================================================

本案例深入讲解中间件中 ModelRequest/Response 的结构和使用方法，
这是 wrap_model_call 等包裹式钩子的核心数据类型。

核心概念：
1. ModelRequest：单次调用级别的"细粒度控制"
2. ModelResponse：模型返回的响应数据
3. AgentState：整个 Agent 生命周期的"全局状态容器"

三者区别：
| 类型           | 作用域       | 生命周期   | 可修改性     |
|--------------|------------|----------|------------|
| ModelRequest | 单次模型调用  | 瞬态      | 可直接修改    |
| ModelResponse| 单次模型调用  | 瞬态      | 只读        |
| AgentState   | 整个Agent会话 | 持久化    | 通过返回值更新 |

要点：
1. 理解 ModelRequest 的结构和字段
2. 掌握如何在中间件中修改请求
3. 理解 AgentState 与 ModelRequest 的区别
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
from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    AgentState,
    wrap_model_call
)

print("=" * 60)
print("案例 1: ModelRequest 与 ModelResponse 参数传递")
print("=" * 60)

# ============================================================
# 3. ModelRequest 结构详解
# ============================================================
print("\n【ModelRequest 结构】")
print("-" * 50)

print("""
ModelRequest 是单次模型调用的请求对象，包含以下字段：

request.model      # 当前要调用的模型实例（可修改）
request.messages   # 消息列表（可修改）
request.tools      # 可用工具列表（可修改）
request.state      # Agent 的当前状态（只读）
request.runtime    # 运行时上下文

示例结构：
┌─────────────────────────────────────────┐
│ ModelRequest                            │
├─────────────────────────────────────────┤
│ model: ChatOpenAI(...)    ← 可修改     │
│ messages: [HumanMsg, AIMsg, ...] ← 可修改│
│ tools: [search, calculate, ...] ← 可修改│
│ state: {'messages': [...]}   ← 只读     │
│ runtime: RuntimeContext(...)  ← 上下文  │
└─────────────────────────────────────────┘
""")

# ============================================================
# 4. ModelRequest 使用示例
# ============================================================
print("\n【ModelRequest 使用示例】")
print("-" * 50)

示例代码1 = """
@wrap_model_call
def dynamic_model_router(request: ModelRequest, handler) -> ModelResponse:
    # 1. 获取当前对话状态
    messages = request.state.get("messages", [])
    print(f"当前消息数: {len(messages)}")

    # 2. 从 runtime 获取上下文
    user_role = request.runtime.context.get("user_role", "user")
    print(f"用户角色: {user_role}")

    # 3. 动态切换模型
    if len(messages) > 5:
        # 长对话切换到大模型
        request = request.override(model=large_model)
        print("切换到大模型")

    # 4. 继续执行
    return handler(request)
"""
print(示例代码1)

# ============================================================
# 5. AgentState 结构详解
# ============================================================
print("\n【AgentState 结构】")
print("-" * 50)

print("""
AgentState 是整个 Agent 生命周期的状态容器：

AgentState 包含：
  - messages: 完整的对话历史
  - user_info: 用户信息（由中间件注入）
  - user_permissions: 用户权限（由中间件注入）
  - 其他业务状态字段

特点：
  - 贯穿整个 Agent 执行流程
  - 跨多次模型调用持久化
  - 类似 Redux Store 或全局上下文

示例结构：
┌─────────────────────────────────────────┐
│ AgentState                              │
├─────────────────────────────────────────┤
│ messages: [HumanMsg, AIMsg, ToolMsg...]│
│ user_info: {'user_id': '001', ...}     │
│ user_permissions: ['read', 'write']    │
│ checkpoint: 'xxx' (用于恢复)            │
└─────────────────────────────────────────┘
""")

# ============================================================
# 6. AgentState vs ModelRequest
# ============================================================
print("\n【对比总结】")
print("-" * 50)

对比表 = """
| 维度      | ModelRequest/Response     | AgentState          |
|----------|-------------------------|---------------------|
| 作用域    | 单次模型调用              | 整个 Agent 会话       |
| 生命周期  | 瞬态                     | 持久化               |
| 可修改性  | 可直接赋值修改            | 通过返回值更新         |
| 典型来源  | wrap_model_call          | before_agent 等     |
| 主要用途  | 动态路由、参数调整         | 权限注入、状态管理     |
"""
print(对比表)

# ============================================================
# 7. request.override() 方法
# ============================================================
print("\n【request.override() 方法】")
print("-" * 50)

print("""
request.override() 用于创建修改后的请求副本：

# 修改模型
request = request.override(model=new_model)

# 修改消息
request = request.override(messages=new_messages)

# 修改工具
request = request.override(tools=new_tools)

# 多个修改可以链式调用
request = request.override(
    model=new_model,
    messages=new_messages
)

注意：override() 返回新副本，不修改原始 request
""")

# ============================================================
# 8. 完整中间件示例
# ============================================================
print("\n" + "=" * 60)
print("完整中间件示例")
print("=" * 60)

print("""
from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    wrap_model_call
)

@wrap_model_call
def my_middleware(request: ModelRequest, handler: ModelResponse):
    '''
    完整的中间件处理流程
    '''
    # 1. 读取阶段
    current_model = request.model
    messages = list(request.messages)  # 复制一份
    tools = request.tools
    state = request.state
    runtime_context = request.runtime.context

    # 2. 分析阶段
    if len(messages) > 10:
        print("长对话检测，准备切换模型...")

    # 3. 修改阶段
    if some_condition:
        request = request.override(model=alternative_model)
        request = request.override(messages=modified_messages)

    # 4. 执行阶段
    response = handler(request)

    # 5. 后处理阶段（如果有 after_model）

    return response
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)