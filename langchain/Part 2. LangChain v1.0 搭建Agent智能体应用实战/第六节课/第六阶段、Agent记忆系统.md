## <center>第六阶段、Agent 记忆系统</center>

&emsp;&emsp;LangChain 1.0的记忆管理与LangGraph的状态机制深度绑定。在 LangGraph 中，**记忆就是"持久化的状态（Persisted State）"**。

### 1. 记忆三层架构

![记忆三层架构](../assets/第六课_01_记忆三层架构.html)

**图解说明**：Agent 记忆三层架构 — 短期记忆(Checkpointer)管理会话级对话 → 长期记忆(VectorStore)存储跨会话知识 → 跨线程记忆(BaseStore)保存结构化用户档案

#### 短期 vs 长期记忆的分界标准

| **误区** | **正确理解** |
| :--- | :--- |
| "内存 = 短期记忆" | 存储介质 ≠ 记忆类型 |
| "数据库 = 长期记忆" | 短期/长期取决于生命周期绑定 |

- **短期记忆**：数据与会话（thread进程）生命周期绑定，随会话结束而被清理
- **长期记忆**：数据与用户/业务实体生命周期绑定，跨会话持久保留

### 2. 短期记忆管理

通过LangGraph的`AgentState`（一个TypedDict）来管理对话历史，并通过检查点（Checkpoints）机制在每次迭代后持久化。

#### InMemorySaver() 内存记忆

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[get_user_info],
    checkpointer=memory  # 启用短期记忆
)

config = {"configurable": {"thread_id": "user_123"}}
response = agent.invoke({"messages": [...]}, config=config)
```

#### PostgresSaver() 数据库持久化

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer
    )
```

### 3. 上下文裁剪

&emsp;&emsp;真正的**记忆管理**还涉及"上下文窗口控制"（防止对话太长撑爆 Token），需要配合 `trim_messages` 使用。

**问题**：随着对话进行，`state["messages"]` 会包含几千条消息，导致：

- 烧钱（token 费用）
- 超过上下文限制报错

**解决**：使用 `trim_messages` 裁剪后只传最近的 N 个 Token

```python
from langchain_core.messages import trim_messages

trimmed_messages = trim_messages(
    existing_messages,
    max_tokens=4000,
    strategy="last",
    include_system=True,
    start_on="human"
)
```

### 4. 自定义 State 扩展

扩展 State 的本质：在 LangGraph 中，State 是 Agent 的"内存"和"消息总线"。

```python
from typing import TypedDict

class CustomAgentState(AgentState):
    messages: list
    user_id: str           # 用户身份
    preferences: dict       # 用户偏好
    visit_count: int        # 访问次数
```

### 5. 记忆核心原则

```
┌─────────────────────────────────────────────────────────────┐
│                    记忆核心原则                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 隔离性：每个用户必须分配唯一 thread_id                   │
│                                                             │
│  2. 持久化：生产环境必须使用数据库检查点                      │
│                                                             │
│  3. 可控性：自定义 State 和中间件实现业务分离                │
│                                                             │
│  4. 性能：长对话必须启用摘要机制，防止 token 超限            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6. 课程案例

本阶段的代码案例位于 `第六节课/` 目录下：

| 文件 | 内容说明 |
|------|---------|
| `01_短期记忆InMemorySaver.py` | 会话级记忆演示 |
| `02_上下文裁剪trim_messages.py` | Token 控制演示 |

**运行示例**：

```bash
python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第六节课/01_短期记忆InMemorySaver.py"
```