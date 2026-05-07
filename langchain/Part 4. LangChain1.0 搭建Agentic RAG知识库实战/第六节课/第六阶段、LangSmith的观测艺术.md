## <center>第六阶段、LangSmith的观测艺术

### 1. LangSmith核心概念

#### 1.1 层级结构

```
LangSmith 层级关系：

Project（项目）
  │
  └── Trace（轨迹）← 一次完整执行
         │
         └── Run（运行）← 单个节点
                │
                └── Feedback（反馈）← 质量评估
                       │
                       └── Metadata（元数据）
```

| 层级 | 说明 |
|------|------|
| Project | 你的应用或服务 |
| Trace | 一次用户请求的完整处理过程 |
| Run | Trace 中的单个操作（LLM调用、工具调用等） |
| Feedback | 对 Run 的质量评分 |
| Metadata | 附加信息（版本、用户ID等） |

#### 1.2 Trace 详解

**Trace 包含**：
1. 输入：用户问题
2. 输出：最终回答
3. 中间步骤：
   - LLM 决策
   - 工具调用
   - 检索结果
   - 迭代过程
4. 元数据：
   - 执行时间
   - Token 消耗
   - 模型名称

**Trace 用途**：
- 调试：看到每一步的执行
- 性能分析：识别瓶颈
- 成本追踪：统计 Token 消耗

#### 1.3 Run 详解

**Run 类型**：
- LLM Run：模型调用
- Tool Run：工具调用
- Chain Run：链式调用
- Agent Run：Agent 执行

**Run 信息**：
- 输入/输出
- 执行时间
- Token 使用
- 错误信息

**父子关系**：
```
Root Run
  ├── LLM Run 1
  │    └── Tool Run 1
  │         └── Tool Run 2
  └── LLM Run 2
```

#### 1.4 Feedback 和 Metadata

**Feedback（反馈）**：
- 对 Run 的质量评分
- 标签（如 "answer_correctness"）
- 分数（0-1 或分类）
- 可人工或自动生成

**Metadata（元数据）**：
- 附加在 Run 上的键值对
- `{"version": "v1.0", "env": "production"}`
- 用于分类和筛选

#### 1.5 免费版限制

| 资源 | 限制 |
|------|------|
| Trace | 5000 条/月 |
| 保留期 | 14 天 |
| 并发 | 500MB/小时 |
| 席位 | 1 个用户 |

### 2. LangSmith配置与使用

#### 2.1 环境变量配置

```python
# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = "your-api-key"
os.environ["LANGSMITH_PROJECT"] = "My_Agentic_RAG"
```

#### 2.2 完整配置示例

```python
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# 配置 LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = "ls_xxxxx"
os.environ["LANGSMITH_PROJECT"] = "Agentic_RAG_Demo"

# 初始化模型和工具
model = ChatDeepSeek(model="deepseek-chat")
web_search = TavilySearch(max_results=2)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="你是一个智能助手。"
)

# 执行（自动被追踪）
result = agent.invoke(
    {"messages": [{"role": "user", "content": "2024年诺贝尔物理学奖是谁？"}]}
)
```

#### 2.3 LangSmith Dashboard 功能

| 功能 | 说明 |
|------|------|
| Trace List | 查看所有追踪记录 |
| Trace Detail | 查看单个追踪的详细信息 |
| Run Tree | 可视化执行树 |
| Token Usage | Token 消耗统计 |
| Feedback | 质量反馈管理 |
| Filter | 按时间/标签/元数据筛选 |

#### 2.4 追踪结果查看

```
登录 LangSmith Dashboard (https://smith.langchain.com)

1. 选择你的项目
2. 查看 Trace List
3. 点击任意 Trace 查看详情
4. 可看到：
   - 完整的调用链
   - 每个 Run 的输入/输出
   - Token 消耗
   - 执行时间
   - 错误信息（如有）
```

### 3. 拓展思考

#### 3.1 LangSmith 的底层架构

&emsp;&empsp;LangSmith 的追踪能力基于 LangChain 的回调机制（Callbacks）：

**回调机制原理**：
```python
# LangChain 的回调接口
class CallbackHandler:
    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM 调用开始"""

    def on_llm_end(self, response, **kwargs):
        """LLM 调用结束"""

    def on_tool_start(self, serialized, input_str, **kwargs):
        """工具调用开始"""

    def on_tool_end(self, output, **kwargs):
        """工具调用结束"""
```

**追踪数据流**：
```
Agent.invoke()
    │
    ├── LLM Callbacks → LangSmith Server
    │       │
    │       ├── on_llm_start
    │       ├── on_chat_model_start
    │       └── on_llm_end
    │
    ├── Tool Callbacks
    │       │
    │       ├── on_tool_start
    │       └── on_tool_end
    │
    └── Custom Callbacks
            │
            └── 自定义监控事件
```

#### 3.2 追踪数据的分析维度

&emsp;&empsp;LangSmith 收集的数据可以用于多个分析维度：

**1. 成本分析**：
```python
# 分析 Token 消耗
trace_data = langsmith.get_trace(trace_id)
total_tokens = sum(run.token_usage.total_tokens for run in trace_data.runs)
cost = total_tokens * price_per_token
```

**2. 性能分析**：
```python
# 分析延迟分布
latencies = [run.latency_ms for run in trace_data.runs if run.type == "llm"]
p50 = percentile(latencies, 50)
p95 = percentile(latencies, 95)
p99 = percentile(latencies, 99)
```

**3. 质量分析**：
```python
# 结合 Feedback 分析
feedback_scores = [run.feedback.score for run in trace_data.runs]
avg_score = sum(feedback_scores) / len(feedback_scores)

# 分析低分 Trace 的共同特征
low_score_traces = [t for t in traces if t.feedback.score < 3]
common_patterns = analyze_patterns(low_score_traces)
```

#### 3.3 私有化部署的替代方案

&emsp;&empsp;LangSmith 是 SaaS 服务，有些场景需要私有化部署：

**开源替代方案对比**：

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| LangSmith | 完整功能、SaaS | 快速启动、云部署 |
| LangFuse | 开源、可自托管 | 数据隐私要求 |
| PromptLayer | OpenAI 优化 | API 成本优化 |
| AgentOps | Agent 专精 | 复杂 Agent 调试 |

**LangFuse 自托管**：
```python
# LangFuse 配置
from langfuse import Langfuse

langfuse = Langfuse(
    host="https://your-langfuse-server.com",
    api_key="sk-xxx",
    secret_key="sk-xxx"
)

# 替换 LangSmith
callbacks = [langfuse.callback_handler()]
```

#### 3.4 追踪数据的脱敏处理

&emsp;&empsp;在生产环境中，追踪数据可能包含敏感信息，需要脱敏：

**脱敏策略**：
```python
from langchain.callbacks import CallbackHandler

class SensitiveDataMasker(CallbackHandler):
    """脱敏回调处理器"""

    SENSITIVE_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
    }

    def on_llm_start(self, serialized, prompts, **kwargs):
        # 脱敏 prompts
        sanitized_prompts = [self.mask_sensitive(p) for p in prompts]
        return {"prompts": sanitized_prompts}

    def mask_sensitive(self, text):
        for pattern_name, regex in self.SENSITIVE_PATTERNS.items():
            text = re.sub(regex, f"[{pattern_name}_masked]", text)
        return text
```

**注意事项**：
1. 脱敏应在回调层面处理，不影响正常业务逻辑
2. 保留足够的信息用于调试
3. 定期审查脱敏规则是否完整