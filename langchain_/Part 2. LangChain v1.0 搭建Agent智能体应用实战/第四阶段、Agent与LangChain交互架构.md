## <center>第四阶段、 Agent与LangChain结合机制

&emsp;&emsp;LangChain 1.0通过将Agent的决策与LangGraph的图式执行相结合，提供了生产级的Agent运行时。其结合机制体现在以下几个方面：

### 4.1 核心结合点：`create_agent` + LangGraph

&emsp;&emsp;`create_agent`作为上层统一入口，其内部实现依赖于LangGraph。当调用`create_agent`时，LangChain会自动构建一个基于ReAct（推理+行动）范式的图结构。这个图包含了Agent决策、工具调用、状态更新等核心节点，并通过边来控制逻辑流转。这种设计将Agent的"思考"过程映射为图的遍历，使得整个执行流程变得透明、可控。

<center><img src="https://ml2022.oss-cn-hangzhou.aliyuncs.com/img/image-20251028154837987.png" alt="image-20251028154837987" style="zoom:50%;" />

LangChain 1.0 的 create_agent 通过这 9 个核心参数，实现了从快速原型到生产部署的全覆盖，开发者可根据场景灵活组合。

* create_agent 的核心价值在于它通过 "三要素 + 三扩展" 的极简抽象，彻底重构了 Agent 的开发范式。所谓三要素，即模型（Model）、工具（Tools）与提示词（System Prompt），这三者构成了 Agent 的"灵魂"——决定了它能思考什么、能做什么以及行为边界何在。而三扩展——中间件（Middleware）、内存管理（Memory）与状态管理（State）——则构建了 Agent 的"神经系统"，使其具备生产级应用所需的可靠性、可观测性与可维护性。

* 这一设计将开发者从繁琐的 ReAct 循环手写、工具调用异常处理、上下文压缩等底层细节中解放出来，转而采用声明式编程模式：只需描述"Agent 应该做什么"，框架自动编译为高效、可靠、安全的执行计划。其本质是 LangGraph 的编译器前端 ，将高层意图转换为优化的图结构，自动集成持久化、流式输出、断点恢复等运行时能力。
这种架构带来了三重革命性影响：首先，开发效率提升 10 倍，10 行代码即可构建一个可投产的智能客服或数据分析 Agent；其次，运维成本降低 60%，中间件机制将 PII 检测、人工审批、自动重试等横切关注点解耦，无需侵入业务代码；最后，可扩展性实现质的飞跃，通过 TypedDict 扩展 State，可无缝集成用户画像、多模态输入、性能监控等复杂场景。

| 参数              | 类型      | 必填 | 默认值     | 核心作用   | 最佳实践                 |
| ----------------- | --------- | ---- | ---------- | ---------- | ------------------------ |
| `model`           | str/实例  | ✅    | -          | 推理引擎   | 生产环境实例化配置       |
| `tools`           | list      | ✅    | \[]        | 执行能力   | 描述清晰，按需添加       |
| `system_prompt`   | str       | ❌    | None       | 行为准则   | 明确角色和约束           |
| `middleware`      | list      | ❌    | \[]        | 功能扩展   | 组合日志、安全、摘要     |
| `checkpointer`    | Saver     | ❌    | None       | 短期记忆   | 生产用 PostgresSaver     |
| `store`           | Store     | ❌    | None       | 长期记忆   | 跨会话用 PostgresStore   |
| `state_schema`    | TypedDict | ❌    | AgentState | 扩展状态   | 用 TypedDict 非 Pydantic |
| `context_schema`  | TypedDict | ❌    | None       | 动态上下文 | 配合 middleware 使用     |
| `response_format` | BaseModel | ❌    | None       | 结构化输出 | API 对接场景启用         |

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,                    # 模型
    tools=[order_query_tool],       # 工具
    system_prompt="你是一个订单查询助手，能够查询订单状态和明细。" , # 系统提示
    middlewares=[order_query_middleware],                    # 中间件
    checkpointer=checkpointer,      # 检查点短期记忆
    store=store,                    # 状态存储长期记忆
    state_schema=OrderQueryState,   # 扩展状态（如需要）
    context_schema=AgentContext,    # 上下文状态（如需要）
    response_format=ResponseModel   # 结构化输出（如需要）
)

# ============ 限制最大 3 次循环 ============
config = {
    "configurable": {"thread_id": "limit_demo"}, # 限制thread_id 线程ID
    "recursion_limit": 3  # 最多 3 次迭代，或使用中间件进行精确跟踪和终止循环
}

result = agent.invoke(
        {"messages": [{"role": "user", "content": "LangChain 1.0 发布日期"}]},
        config=config
    )
```

### 4.2 ReAct范式与执行循环

&emsp;&emsp;ReAct(Reasoning + Acting)范式强调"推理—行动—观察"的闭环:Agent先形成Thought(推理),据此选择并调用工具(Action),再吸收工具返回的Observation(观察),进入下一轮决策。闭环在达到最终答案、迭代上限或时间上限时终止。在LangGraph中,这一闭环由状态机与检查点驱动,保证每次行动的原子性、状态的可见性与轨迹的可回放性。并且推理与规划不是代码逻辑，而是LLM的生成行为，关键的 Thought: 步骤并非由确定性算法执行，而是prompt触发LLM生成推理文本。模型能力是ReAct性能的天花板

<div align=center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251125215020369.png" width=60%></div>

Agent的认知循环本质上是一个闭环反馈系统。每一次"行动"的执行结果都会作为新的输入反馈到系统，影响下一轮的"思考"和"行动"。这种反馈机制使得Agent能够动态调整策略，应对不确定的环境和复杂任务。在LangChain中，这一循环被实现为：

1. **Thought (推理)**：大模型基于当前输入和历史记录进行思考，决定下一步行动。

2. **Action (行动)**：大模型选择一个工具并构造输入参数，形成一个`AgentAction`。

3. **Observation (观察)**：工具被执行，其返回结果作为观察值，并与`AgentAction`一起被添加到中间步骤（intermediate_steps）中。

4. **循环决策**：Agent将新的观察结果纳入上下文，进入下一轮"推理-行动"循环，直至达到最终目标或触发终止条件（如达到最大迭代次数）。
