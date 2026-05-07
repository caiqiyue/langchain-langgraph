# -*- coding: utf-8 -*-
"""
【案例 2】中间件组合设计
==========================

本案例展示 Agentic RAG 系统中多中间件的组合设计。

中间件组合：

before_model:
  - SummarizationMiddleware：上下文压缩

wrap_model_call:
  - dynamic_prompt：动态提示词

after_model:
  - ToolCallLimitMiddleware：调用限制
  - ToolLoggingMiddleware：日志记录
  - HumanInTheLoopMiddleware：人工审批

wrap_tool_call:
  - ToolRetryMiddleware：自动重试

执行顺序原则：
  - before_* 正序执行
  - wrap_* 嵌套执行
  - after_* 逆序执行

要点：
1. 掌握多中间件组合方法
2. 理解执行顺序设计
3. 学会根据场景调整中间件
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: 中间件组合设计")
print("=" * 60)

# ============================================================
# 2. 中间件组合
# ============================================================
print("\n【中间件组合】")
print("-" * 50)

print("""
middlewares = [
    # === before_model ===
    summarization_middleware,     # 上下文压缩

    # === wrap_model_call ===
    rag_optimized_prompt,        # 动态提示词

    # === after_model（逆序）===
    official_hitl_middleware,     # 人工审批（最后执行）
    logging_middleware,           # 日志记录
    sensitive_limit_middleware,   # 敏感工具限制
    retrieval_limit_middleware,   # 检索工具限制

    # === wrap_tool_call ===
    retry_middleware,            # 自动重试
]
""")

# ============================================================
# 3. 各中间件职责
# ============================================================
print("\n【各中间件职责】")
print("-" * 50)

职责表 = """
| 中间件 | Hook 点 | 职责 |
|--------|---------|------|
| summarization_middleware | before_model | 压缩上下文，减少 token |
| rag_optimized_prompt | wrap_model_call | 动态调整提示词 |
| retrieval_limit_middleware | after_model | 限制检索次数 |
| sensitive_limit_middleware | after_model | 限制敏感查询 |
| logging_middleware | after_model | 记录日志 |
| official_hitl_middleware | after_model | 人工审批 |
| retry_middleware | wrap_tool_call | 重试失败工具 |
"""
print(职责表)

# ============================================================
# 4. 执行顺序图
# ============================================================
print("\n【执行顺序图】")
print("-" * 50)

print("""
【完整执行流程】

用户请求 → before_model → wrap_model_call → Model → after_model → 用户响应
                   ↓
              wrap_tool_call（工具执行）
                   ↓
              after_model（后处理）

详细：
  1. SummarizationMiddleware（压缩上下文）
  2. dynamic_prompt（注入动态提示词）
  3. LLM 模型调用
  4. ToolRetryMiddleware（包装工具调用，可能多次）
  5. ToolCallLimitMiddleware（限制次数）
  6. ToolLoggingMiddleware（记录日志）
  7. HumanInTheLoopMiddleware（人工审批）
""")

# ============================================================
# 5. 动态提示词示例
# ============================================================
print("\n【动态提示词示例】")
print("-" * 50)

print("""
@dynamic_prompt
def rag_optimized_prompt(request: ModelRequest) -> str:
    # 统计检索次数
    retrieval_count = count_retrievals(request.messages)

    if retrieval_count == 0:
        return base_prompt + "❌ 禁止在没有检索的情况下直接回答。"

    elif retrieval_count < 3:
        return base_prompt + f"已检索 {retrieval_count} 次，请评估信息是否足够。"

    else:
        return base_prompt + "已达到最大检索次数，请基于已有信息生成回答。"
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)