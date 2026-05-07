## <center>第四阶段、Agent与LangChain交互架构</center>

&emsp;&emsp;LangChain 1.0通过将Agent的决策与LangGraph的图式执行相结合，提供了生产级的Agent运行时。

### 1. create_agent 核心 API

`create_agent`作为上层统一入口，其内部实现依赖于LangGraph，是 LangChain 1.0 Agent 开发的核心入口。

![create_agent参数图](../assets/第四课_01_create_agent参数图.html)

**图解说明**：create_agent 九大参数 — 必填(model, tools) + 可选(system_prompt, middleware, checkpointer, store, state_schema, context_schema, response_format)

#### 九大核心参数

| 参数 | 类型 | 必填 | 默认值 | 核心作用 |
| :--- | :--- | :--- | :--- | :--- |
| `model` | str/实例 | ✅ | - | 推理引擎 |
| `tools` | list | ✅ | [] | 执行能力 |
| `system_prompt` | str | ❌ | None | 行为准则 |
| `middleware` | list | ❌ | [] | 功能扩展 |
| `checkpointer` | Saver | ❌ | None | 短期记忆 |
| `store` | Store | ❌ | None | 长期记忆 |
| `state_schema` | TypedDict | ❌ | AgentState | 扩展状态 |
| `context_schema` | TypedDict | ❌ | None | 动态上下文 |
| `response_format` | BaseModel | ❌ | None | 结构化输出 |

#### 核心价值

* create_agent 的核心价值在于它通过 "三要素 + 三扩展" 的极简抽象，彻底重构了 Agent 的开发范式。

- **三要素**：模型（Model）、工具（Tools）与提示词（System Prompt）
- **三扩展**：中间件（Middleware）、内存管理（Memory）与状态管理（State）

### 2. ReAct 范式与执行循环

ReAct(Reasoning + Acting)范式强调"推理—行动—观察"的闭环，是 Agent 自主决策的核心机制。

![ReAct执行循环图](../assets/第一课_02_ReAct执行循环图.html)

**图解说明**：ReAct 循环 — Thought 思考 → Action 行动 → Observation 观察 → 循环直到任务完成

**关键特性**：

- 推理与规划不是代码逻辑，而是 LLM 的生成行为
- Thought 步骤并非由确定性算法执行，而是 prompt 触发 LLM 生成推理文本
- 模型能力是 ReAct 性能的天花板

### 3. 配置示例

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,                    # 模型
    tools=[order_query_tool],       # 工具
    system_prompt="你是一个订单查询助手",  # 系统提示
    middlewares=[order_middleware], # 中间件
    checkpointer=checkpointer,      # 短期记忆
    store=store,                    # 长期记忆
)

# 限制最大循环次数
config = {
    "configurable": {"thread_id": "limit_demo"},
    "recursion_limit": 3  # 最多 3 次迭代
}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "LangChain 1.0 发布日期"}]},
    config=config
)
```

### 4. 课程案例

本阶段的代码案例位于 `第四节课/` 目录下：

| 文件 | 内容说明 |
|------|---------|
| `01_create_agent九大参数.py` | create_agent 完整参数解析与最佳实践 |
| `02_RecursionLimit控制.py` | 如何限制 Agent 最大循环次数 |
| `03_流式输出观察.py` | stream_mode 三种模式的对比演示 |

**运行示例**：

```bash
python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第四节课/01_create_agent九大参数.py"
```