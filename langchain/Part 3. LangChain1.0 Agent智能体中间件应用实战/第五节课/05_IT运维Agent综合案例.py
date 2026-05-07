# -*- coding: utf-8 -*-
"""
【案例 5】IT 运维 Agent - 多中间件组合应用
==========================================

本案例展示一个完整的 IT 运维 Agent，集成了多种中间件：
1. SecurityGuardrail - 安全检查
2. RBACMiddleware - 权限验证
3. dynamic_system_prompt - 动态提示词
4. dynamic_model_router - 智能模型切换
5. ContextEditingMiddleware - 上下文管理
6. ResponseValidator - 响应验证
7. AuditLogger - 审计日志

执行顺序：
before_agent:
  1. SecurityGuardrail（安全检查）
  2. RBACMiddleware（权限验证）
before_model:
  3. RBACMiddleware（注入用户信息）
wrap_model_call:
  4. dynamic_system_prompt（动态提示词）
  5. dynamic_model_router（模型切换）
  6. ContextEditingMiddleware（上下文清理）
after_model:
  7. ResponseValidator（验证）
  8. AuditLogger（审计）

要点：
1. 理解多中间件组合的设计思路
2. 掌握执行顺序的设计原则
3. 理解各中间件的协作机制
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 5: IT 运维 Agent - 多中间件组合")
print("=" * 60)

# ============================================================
# 2. 用户角色和权限定义
# ============================================================
print("\n【角色与权限定义】")
print("-" * 50)

print("""
角色定义：
┌─────────────────────────────────────────┐
│ ADMIN（管理员）   → 所有权限            │
│ OPERATOR（运维）  → 查询、重启权限      │
│ VIEWER（查看者）  → 仅查询权限          │
│ GUEST（访客）     → 无权限              │
└─────────────────────────────────────────┘

权限定义：
  - VIEW_STATUS：查看状态
  - VIEW_LOGS：查看日志
  - RESTART_SERVICE：重启服务
  - MODIFY_CONFIG：修改配置
  - VIEW_METRICS：查看监控指标
""")

# ============================================================
# 3. 工具定义
# ============================================================
print("\n【运维工具】")
print("-" * 50)

print("""
tools = [
    check_server_status,   # 查看服务器状态（需 VIEW_STATUS）
    view_service_logs,     # 查看服务日志（需 VIEW_LOGS）
    restart_service,       # 重启服务（需 RESTART_SERVICE）
    get_system_metrics     # 获取系统指标（需 VIEW_METRICS）
]
""")

# ============================================================
# 4. 中间件组合
# ============================================================
print("\n【中间件组合配置】")
print("-" * 50)

print("""
middlewares = [
    # === before_agent ===
    SecurityGuardrail(),           # 1. 安全检查（危险操作拦截）
    RBACMiddleware(),             # 2. 权限验证

    # === before_model ===
    RBACMiddleware(),             # 3. 注入用户信息到 state

    # === wrap_model_call ===
    dynamic_system_prompt,        # 4. 动态提示词注入
    dynamic_model_router,         # 5. 智能模型切换
    custom_context_middleware,    # 6. 上下文管理

    # === after_model ===
    ResponseValidator(),          # 7. 响应验证
    AuditLogger(),                # 8. 审计日志
]

执行原则：
  - 安全类永远优先
  - before_agent 正序执行
  - wrap_model_call 嵌套执行
  - after_model 逆序执行
""")

# ============================================================
# 5. 各中间件职责
# ============================================================
print("\n【各中间件职责】")
print("-" * 50)

职责表 = """
| 序号 | 中间件                | Hook 点        | 职责                    |
|-----|---------------------|---------------|------------------------|
| 1  | SecurityGuardrail   | before_agent  | 危险操作关键词检测        |
| 2  | RBACMiddleware      | before_agent  | 用户权限验证             |
| 3  | RBACMiddleware      | before_model  | 注入 user_info          |
| 4  | dynamic_prompt      | wrap_model_call| 角色专属提示词           |
| 5  | dynamic_model_router| wrap_model_call| 长对话切换大模型         |
| 6  | ContextEditing      | wrap_model_call| 清理旧工具结果          |
| 7  | ResponseValidator   | after_model   | 工具调用权限验证          |
| 8  | AuditLogger         | after_model   | 操作审计日志             |
"""
print(职责表)

# ============================================================
# 6. 执行流程图
# ============================================================
print("\n" + "=" * 60)
print("执行流程图")
print("=" * 60)

print("""
用户请求: "请重启 Server-A"
    │
    ▼
┌─────────────────────────────────────┐
│ before_agent                        │
│ ┌─────────────────────────────┐     │
│ │ 1. SecurityGuardrail       │     │
│ │    → 检查危险关键词          │     │
│ └─────────────────────────────┘     │
│ ┌─────────────────────────────┐     │
│ │ 2. RBACMiddleware          │     │
│ │    → 验证用户权限           │     │
│ └─────────────────────────────┘     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ before_model                        │
│ ┌─────────────────────────────┐     │
│ │ 3. RBACMiddleware           │     │
│ │    → 注入 user_info 到 state │     │
│ └─────────────────────────────┘     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ wrap_model_call                     │
│ ┌─────────────────────────────┐     │
│ │ 4. dynamic_system_prompt   │     │
│ │    → 注入角色专属提示词      │     │
│ └─────────────────────────────┘     │
│ ┌─────────────────────────────┐     │
│ │ 5. dynamic_model_router    │     │
│ │    → 判断是否切换模型        │     │
│ └─────────────────────────────┘     │
│ ┌─────────────────────────────┐     │
│ │ 6. ContextEditing          │     │
│ │    → 清理旧工具结果         │     │
│ └─────────────────────────────┘     │
│ ┌─────────────────────────────┐     │
│ │ Model Call                 │     │
│ └─────────────────────────────┘     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ after_model                         │
│ ┌─────────────────────────────┐     │
│ │ 7. ResponseValidator       │     │
│ │    → 验证工具调用权限        │     │
│ └─────────────────────────────┘     │
│ ┌─────────────────────────────┐     │
│ │ 8. AuditLogger              │     │
│ │    → 记录审计日志            │     │
│ └─────────────────────────────┘     │
└─────────────────────────────────────┘
    │
    ▼
返回结果给用户
""")

# ============================================================
# 7. 完整代码结构
# ============================================================
print("\n【完整代码结构】")
print("-" * 50)

print("""
# 1. 定义中间件
class SecurityGuardrail(AgentMiddleware):
    def before_agent(self, state, runtime):
        # 检查危险操作关键词
        ...

class RBACMiddleware(AgentMiddleware):
    def before_agent(self, state, runtime):
        # 验证用户权限
        ...
    def before_model(self, state, runtime):
        # 注入用户信息
        return {"user_info": ..., "user_permissions": [...]}

# 2. 定义动态中间件
@wrap_model_call
def dynamic_system_prompt(request, handler):
    # 根据角色注入提示词
    ...

@wrap_model_call
def dynamic_model_router(request, handler):
    # 根据条件切换模型
    ...

# 3. 组合中间件
middlewares = [
    SecurityGuardrail(),
    RBACMiddleware(),
    dynamic_system_prompt,
    dynamic_model_router,
    custom_context_middleware,
    ResponseValidator(),
    AuditLogger(),
]

# 4. 创建 Agent
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个IT运维助手...",
    middleware=middlewares,
    context_schema=UserContext,
    debug=True,
)
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)