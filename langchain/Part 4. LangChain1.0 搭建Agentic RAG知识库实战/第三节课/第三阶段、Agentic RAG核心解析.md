## <center>第三阶段、Agentic RAG核心解析

### 1. Tool与Middleware的区别

#### 1.1 本质区别

| 维度 | Tool（工具） | Middleware（中间件） |
|------|------------|-------------------|
| 作用对象 | 封装业务功能 | 封装执行流程控制 |
| 调用方式 | LLM 自主决策调用 | 自动触发 |
| 设计目的 | 扩展能力边界 | 增强可靠性/安全性/可观测性 |
| 状态访问 | 接收参数，返回结果 | 可直接读写 AgentState |
| 执行概率 | 不确定（0-100%） | 确定（100%） |

```
┌─────────────────────────────────────────────────────────┐
│                      Tool vs Middleware                  │
├─────────────────────────────────────────────────────────┤
│  Tool（工具）                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  LLM 自主决定是否调用                            │   │
│  │  通过 function calling 执行                       │   │
│  │  类似人的"手脚"                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Middleware（中间件）                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Agent 执行流程中自动触发                        │   │
│  │  类似"过滤器"或"拦截器"                         │   │
│  │  类似人的"条件反射"                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 1.2 三个灵魂判断问题

**问题1：谁来决定"做不做"？**

| 情况 | 选择 | 示例 |
|------|------|------|
| 需要 LLM 根据上下文判断是否执行 | Tool | 搜索互联网、查询天气 |
| 业务流程规定必须执行 | Middleware | 权限校验、敏感词过滤、日志记录 |

**问题2：参数从哪里来？**

| 情况 | 选择 | 示例 |
|------|------|------|
| 参数需要从用户的自然语言中提取 | Tool | 用户说"帮我查下特斯拉的股价" |
| 参数是系统上下文或环境变量 | Middleware | UserID、SessionID、数据库配置 |

**问题3：失败了怎么办？**

| 情况 | 选择 | 示例 |
|------|------|------|
| 失败了需要 LLM 换个方式重试 | Tool | 搜索不到结果，LLM 尝试换个关键词 |
| 失败了直接抛异常或走系统降级 | Middleware | 数据库连接断开、API 鉴权失败 |

#### 1.3 典型场景选择

| 场景 | 选择 | 原因 |
|------|------|------|
| RAG 检索 | Tool | LLM 决定是否检索、检索什么 |
| 权限验证 | Middleware | 每个请求都要检查 |
| 敏感词过滤 | Middleware | 自动过滤，不需要 LLM 决策 |
| 调用外部 API | Tool | LLM 决定何时调用、如何调用 |
| 日志记录 | Middleware | 每个请求都要记录 |
| 人工审批 | Middleware | 自动触发审批流程 |

### 2. 将RAG封装为Tool

#### 2.1 定义工具函数

```python
from pydantic import BaseModel, Field

# 定义工具输入参数
class QAWithRetrievalArgs(BaseModel):
    query: str = Field(description="用户的问题")

def query_retrieval_knowledge(query: str) -> str:
    """
    一个基于 LangChain 知识库检索的问答工具。
    专门用于回答与 LangChain 相关的技术问题。

    ⚠️ 重要：此工具仅适用于 LangChain 相关问题！
    如果问题与 LangChain 无关，请使用网络搜索工具。
    """
    # 检查是否与 LangChain 相关
    langchain_keywords = ['langchain', 'langgraph', 'langsmith', ...]
    query_lower = query.lower()
    is_related = any(kw in query_lower for kw in langchain_keywords)

    if not is_related:
        return "❌ 检测到此问题与 LangChain 知识库无关..."

    # 执行检索
    retrieval_chain = ensemble_retriever | format_docs
    docs = retrieval_chain.invoke(query)

    return docs
```

#### 2.2 创建 StructuredTool

```python
from langchain_core.tools import StructuredTool

# 创建 StructuredTool
qa_tool = StructuredTool.from_function(
    func=query_retrieval_knowledge,
    name="query_retrieval_knowledge",
    description="...",
    args_schema=QAWithRetrievalArgs,
    return_direct=False
)
```

#### 2.3 工具描述的四大要素

| 要素 | 说明 |
|------|------|
| 核心功能 | 工具做什么 |
| 适用范围 | 什么时候用 |
| 返回格式 | 返回什么 |
| 限制说明 | 什么情况下不能用 |

#### 2.4 工具描述检查清单

```
□ 1. 功能描述：工具做什么？
□ 2. 适用范围：什么时候用？
□ 3. 限制条件：什么情况下不能用？
□ 4. 返回格式：返回什么？
□ 5. 依赖说明：需要什么前提条件？
□ 6. 替代方案：不能用什么代替？
□ 7. 注意事项：有什么特别提醒？
```

### 3. Agent执行工具调用

#### 3.1 创建 Agent

```python
from typing import TypedDict
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 定义上下文类型
class Context(TypedDict):
    user_role: str

# 创建 Agent
agent = create_agent(
    tools=tools,                    # 工具列表
    model=model,                    # LLM 模型
    debug=False,                    # 调试模式
    checkpointer=InMemorySaver(),   # 状态持久化
    context_schema=Context           # 上下文类型
)
```

#### 3.2 执行 Agent

```python
# 配置线程 ID（用于状态持久化）
config = {"configurable": {"thread_id": "test-thread-001"}}

# 执行 Agent
for event in agent.stream(
    {"messages": [{"role": "user", "content": "LangChain支持哪些模型？"}]},
    config=config,
    stream_mode="values",
    context={"user_role": "大模型工程师"}
):
    if "messages" in event:
        last_msg = event["messages"][-1]
        if last_msg.type == "ai":
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                print(f"🤖 决策: 调用 {last_msg.tool_calls[0]['name']}")
            elif last_msg.content:
                print(f"💬 回复: {last_msg.content}")
```

#### 3.3 stream vs invoke

| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| stream | 流式输出 | 实时看到中间步骤 | 代码复杂 |
| invoke | 完整执行 | 代码简单 | 等待完成才能看到结果 |

#### 3.4 执行流程图

```
【Agent 执行流程】

用户输入: "LangChain支持哪些模型？"
    │
    ▼
┌─────────────────────────────────────────────┐
│  Agent 接收消息                              │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  LLM 分析用户问题                            │
│  → 决策：需要调用工具获取信息               │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  调用 query_retrieval_knowledge 工具        │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  检索 LangChain 知识库                      │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  LLM 收到检索结果，生成回答                  │
└─────────────────────────────────────────────┘
    │
    ▼
最终回复: "LangChain 支持多种模型，包括..."

### 4. 拓展思考

#### 4.1 Tool Calling 的底层机制

&emsp;&empsp;LLM 如何决定调用哪个 Tool？这涉及到 Function Calling 的技术原理：

**Function Calling 的工作流程**：

```
用户问题 → LLM 分析 → 是否需要调用函数？
    │
    ├── 不需要 → 直接生成回答
    │
    └── 需要 → 提取函数名和参数 → JSON 输出 → 执行函数 → 将结果返回给 LLM → 生成回答
```

**LLM 如何"决定"调用工具？**

1. **工具描述编码**：工具的 description 会被加入到 prompt 中
2. **注意力机制**：LLM 学习"问题-工具"的对应关系
3. **函数签名理解**：LLM 理解参数类型和约束

**为什么 Tool Calling 有时不准？**

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 选错工具 | 工具描述模糊 | 优化 description |
| 参数错误 | 参数说明不清晰 | 提供详细的 args_schema |
| 不调用工具 | LLM 判断不需要 | 调整 system prompt |

#### 4.2 RAG as Tool vs RAG as Middleware

&emsp;&empsp;在 Agentic RAG 中，RAG 可以作为 Tool 或 Middleware 使用，各有优劣：

**RAG as Tool（推荐）**：

```python
# RAG 作为 Tool，LLM 自主决定是否调用
@tool
def query_knowledge_base(query: str) -> str:
    """查询知识库获取相关信息

    适用场景：用户问题涉及专业知识、需要事实依据时使用。
    返回：检索到的相关信息片段。
    """
    docs = retriever.get_relevant_documents(query)
    return format_docs(docs)
```

**优点**：
- LLM 自主判断是否需要检索
- 避免不必要的检索，节省成本
- 更符合 Agent 自主决策的理念

**RAG as Middleware**：

```python
# RAG 作为 Middleware，每次请求都自动检索
class AutoRetrievalMiddleware(AgentMiddleware):
    def before_model(self, state, runtime):
        query = state["messages"][-1].content
        docs = retriever.get_relevant_documents(query)

        # 将检索结果注入到 messages 中
        retrieval_message = HumanMessage(
            content=f"相关背景信息：{format_docs(docs)}"
        )
        return {"messages": state["messages"] + [retrieval_message]}
```

**适用场景**：
- 知识密集型 Agent（几乎每个问题都需要检索）
- 对召回率要求高于精确度的场景

#### 4.3 工具描述的优化技巧

&emsp;&empsp;工具描述的质量直接影响 LLM 的工具选择和参数提取：

**优秀工具描述的公式**：

```python
description = """
{name} - {core_function}

{when_to_use}

{what_it_returns}

{constraints/limitations}
"""
```

**实际示例**：
```python
tool = StructuredTool.from_function(
    func=search_documents,
    name="search_documents",
    description="""
search_documents - 在文档库中搜索相关文档

适用场景：
- 用户询问公司政策、流程、规范
- 需要引用具体文档内容作为依据
- 用户问题包含"文档"、"规定"、"政策"等关键词

返回格式：
[
  {"title": "文档标题", "content": "相关段落...", "source": "文件名.pdf"},
  ...
]

限制说明：
- 搜索范围仅限已索引的内部文档
- 不支持互联网搜索
- 每次最多返回 5 个相关文档
"""
)
```

#### 4.4 Agentic RAG 的迭代优化

&emsp;&empsp;Agentic RAG 不是一次性实现的，需要持续迭代优化：

**迭代路径**：

```
第1阶段：Naive RAG
   简单检索 → 直接返回
   问题：召回率低、上下文不完整

第2阶段：RAG with Query Rewrite
   查询改写 → 多次检索 → 融合结果
   改进：提高召回率

第3阶段：RAG with Reranking
   初步检索 → 重排序 → 返回 Top-K
   改进：提高精确度

第4阶段：Agentic RAG（完整版）
   LLM 决策 → 迭代检索 → 自我验证 → 生成
   改进：自适应、智能决策
```

**关键优化指标**：

| 指标 | 含义 | 优化方向 |
|------|------|---------|
| 召回率 | 相关文档被检索到的比例 | 增加检索次数、优化查询 |
| 精确度 | 检索结果中相关的比例 | 添加重排序、过滤器 |
| 答案质量 | 最终回答的满意度 | 优化 prompt、多次迭代 |
| 响应延迟 | 从提问到回答的时间 | 缓存、异步处理 |
```