## <center>第五阶段、构建Agentic RAG系统

### 1. Agentic RAG系统概述

#### 1.1 传统 RAG vs Agentic RAG

| 维度 | 传统 RAG | Agentic RAG |
|------|----------|-------------|
| 检索次数 | 单次 | 多轮迭代 |
| LLM 角色 | 被动接收 | 主动决策 |
| 工具调用 | 无 | 有 |
| 复杂问题 | 局限 | 支持 |

**传统 RAG 流程**：
```
用户问题 → 检索 → 拼接上下文 → LLM 生成回答
```

**局限性**：
1. 一次检索可能不够（复杂问题）
2. 检索结果可能不相关
3. 无法判断检索是否足够
4. 无法多源检索（知识库+网络）

**Agentic RAG 流程**：
```
用户问题 → LLM 决策 → 是否检索？ → 工具调用 → 评估结果
                                              ↓
                                         补充检索？ → ...
                                              ↓
                                         生成回答
```

#### 1.2 Agentic RAG 核心组件

| 组件 | 作用 |
|------|------|
| Agent | 核心决策单元，控制工具调用 |
| RAG Tool | 将检索封装为可调用工具 |
| Middleware | 提供上下文压缩、重试、日志等 |
| LLM | 理解问题、评估结果、生成回答 |

#### 1.3 应用场景

| 场景 | 传统 RAG | Agentic RAG |
|------|----------|-------------|
| 简单问答 | ✅ 适用 | ✅ 适用 |
| 复杂多跳问题 | ❌ 局限 | ✅ 擅长 |
| 需要网络搜索 | ❌ 不支持 | ✅ 支持 |
| 敏感数据查询 | ❌ 不支持 | ✅ 支持 |
| 迭代优化检索 | ❌ 不支持 | ✅ 支持 |

### 2. 中间件组合设计

#### 2.1 中间件组合

```python
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
```

#### 2.2 各中间件职责

| 中间件 | Hook 点 | 职责 |
|--------|---------|------|
| summarization_middleware | before_model | 压缩上下文，减少 token |
| rag_optimized_prompt | wrap_model_call | 动态调整提示词 |
| retrieval_limit_middleware | after_model | 限制检索次数 |
| sensitive_limit_middleware | after_model | 限制敏感查询 |
| logging_middleware | after_model | 记录日志 |
| official_hitl_middleware | after_model | 人工审批 |
| retry_middleware | wrap_tool_call | 重试失败工具 |

#### 2.3 执行顺序图

```
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
```

#### 2.4 动态提示词示例

```python
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

### 3. 拓展思考

#### 3.1 Agentic RAG 的决策边界

&emsp;&empsp;Agentic RAG 的核心是让 LLM 自主决策何时检索、检索什么。但这种"自主"需要有明确的边界：

**决策树示例**：
```python
def should_retrieve(state) -> bool:
    """
    LLM 应该决定是否检索的决策逻辑
    """
    last_message = state["messages"][-1].content

    # 条件1：问题类型判断
    if is_factual_question(last_message):
        return True  # 事实性问题需要检索

    if is_opinion_question(last_message):
        return False  # 观点性问题不需要检索

    # 条件2：时间敏感判断
    if is_time_sensitive(last_message):
        return True  # 需要最新信息

    # 条件3：上下文判断
    if has_sufficient_context(state):
        return False  # 上下文已足够

    return True  # 默认检索
```

**Agentic RAG vs Plan-and-Execute 模式**：

| 模式 | 特点 | 适用场景 |
|------|------|---------|
| Agentic RAG | 边执行边决策，灵活 | 动态、多变的查询 |
| Plan-and-Execute | 先计划再执行，稳定 | 复杂但可预测的任务 |

#### 3.2 中间件组合的工程哲学

&emsp;&empsp;Agentic RAG 中，中间件的组合不是简单的堆叠，而是有策略的编排：

**中间件编排的三层架构**：

```
┌─────────────────────────────────────────────┐
│  Layer 1: 安全与信任                         │
│  ├── AuthenticationMiddleware                │
│  ├── RBACMiddleware                         │
│  └── PIIMiddleware                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 2: 质量与效率                         │
│  ├── SummarizationMiddleware                │
│  ├── ContextCompression                     │
│  └── ModelFallbackMiddleware                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Layer 3: 业务逻辑                           │
│  ├── RetrievalMiddleware                    │
│  ├── ResponseGeneration                      │
│  └── HumanInTheLoop                         │
└─────────────────────────────────────────────┘
```

**每一层只做一件事，避免重复和冲突**。

#### 3.3 检索迭代的终止条件

&empsp;&empsp;Agentic RAG 的关键问题：如何判断"检索足够"？

**常见终止条件**：

| 条件 | 说明 | 优缺点 |
|------|------|-------|
| 固定次数 | 检索 N 次后强制终止 | 简单，但可能不准确 |
| 相似度阈值 | 检索结果相似度 > 阈值 | 依赖阈值设置 |
| LLM 自我判断 | 让 LLM 判断信息是否足够 | 最智能，但成本高 |
| 穷尽判断 | 所有相关文档都被检索到 | 最准确，但慢 |

**实际推荐：混合条件**：
```python
def should_terminate(state, config):
    # 条件1：达到最大检索次数
    if retrieval_count >= config.max_retrievals:
        return True, "max_retrievals_reached"

    # 条件2：检索结果质量
    last_result = state["retrieval_results"][-1]
    if last_result.similarity < config.min_similarity:
        return True, "low_similarity"

    # 条件3：LLM 自我评估
    if llm_judges_sufficient(state):
        return True, "llm_judged_sufficient"

    return False, None
```

#### 3.4 生产环境的 Agentic RAG 监控

&emsp;&empsp;Agentic RAG 在生产环境中需要全面的可观测性：

**核心监控指标**：

| 指标 | 含义 | 告警阈值 |
|------|------|---------|
| retrieval_rate | 平均每次查询的检索次数 | > 5 或 < 0.5 |
| retrieval_precision | 检索结果的相关比例 | < 0.6 |
| context_window_usage | 上下文窗口使用率 | > 0.9 |
| end_to_end_latency | 端到端延迟 | > 10s |
| tool_failure_rate | 工具调用失败率 | > 0.1 |

**LangSmith 集成**：
```python
from langchain.callbacks import LangChainCallbackHandler

# 配置 LangSmith 追踪
callbacks = [
    LangChainCallbackHandler(
        project_name="agentic-rag-production",
        temperature=0.1,  # 采样率
        tracing=True
    )
]

# 运行 Agent
result = agent.invoke(
    {"messages": [HumanMessage(content=query)]},
    config={"callbacks": callbacks}
)
```
```