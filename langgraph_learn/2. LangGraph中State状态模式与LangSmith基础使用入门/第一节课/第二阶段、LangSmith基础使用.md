## <center>第二阶段、LangSmith 基础使用</center>

&emsp;&emsp;LangSmith 是 LangChain/LangGraph 的官方调试和追踪平台，可以帮助开发者可视化和调试复杂的工作流程。本阶段我们将介绍 LangSmith 的基础配置和使用方法。

### 1. LangSmith 简介

&emsp;&emsp;LangSmith 是一个用于构建、调试和评估 LLM 应用的平台，提供以下核心功能：

| 功能 | 说明 |
| ---- | ---- |
| **追踪** | 记录每个步骤的输入、输出和状态 |
| **调试** | Playground 环境实时测试 |
| **评估** | 自动评估应用效果 |
| **协作** | 团队共享和注释 |

### 2. LangSmith 环境配置

&emsp;&emsp;要使用 LangSmith，需要进行以下环境配置：

```python
import os
import getpass

# 1. 启用 LangSmith 追踪
os.environ["LANGSMITH_TRACING"] = "true"

# 2. 设置 API Key
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")

# 3. 设置项目名称（可选）
os.environ["LANGSMITH_PROJECT"] = "langgraph-course"
```

&emsp;&emsp;获取 LangSmith API Key：
1. 访问 https://smith.langchain.com
2. 注册/登录账号
3. 在 Settings 中获取 API Key

### 3. LangGraph 集成 LangSmith

&emsp;&emsp;LangGraph 与 LangSmith 的集成是自动的。只需要配置环境变量，在 `compile()` 图时会自动启用追踪：

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(InputState, OutputState):
    pass

def llm_node(state: InputState):
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([("human", state["question"])])
    return {"answer": response.content}

builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("llm", llm_node)
builder.add_edge(START, "llm")
builder.add_edge("llm", END)

# 编译图（LangSmith 自动集成）
graph = builder.compile()

# 调用会自动发送到 LangSmith
result = graph.invoke({"question": "LangSmith 是什么？"})
```

### 4. 查看追踪结果

&emsp;&emsp;执行后，访问 LangSmith Dashboard 查看追踪：

![LangSmith追踪界面图](../assets/第二课_02_LangSmith追踪界面图.html)

**图解说明**：LangSmith 追踪界面 — 显示每个节点的输入、输出、耗时和 Token 消耗

| 追踪信息 | 说明 |
| -------- | ---- |
| Run Graph | 图执行的整体信息 |
| Node | 每个节点的详细信息 |
| Token Usage | Token 消耗统计 |
| Latency | 执行延迟分析 |

### 5. Checkpoints 检查点功能

&emsp;&emsp;LangGraph 支持检查点功能，可以在执行过程中的任何点保存和恢复状态：

```python
from langgraph.checkpoint.memory import MemorySaver

# 创建内存检查点
checkpointer = MemorySaver()

# 在 compile 时传入
graph = builder.compile(checkpointer=checkpointer)

# 使用 thread_id 维护会话
config = {"configurable": {"thread_id": "1"}}

# 第一次调用
result1 = graph.invoke(
    {"messages": [HumanMessage(content="我叫张三")]},
    config=config
)

# 第二次调用（可以访问之前的状态）
result2 = graph.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config=config
)
```

![LangGraph检查点图](../assets/第二课_03_LangGraph检查点图.html)

**图解说明**：LangGraph Checkpoints — 每个步骤后自动保存状态，支持暂停、恢复和时间旅行

### 6. 拓展思考

#### 6.1 LangSmith 的调试价值

&emsp;&emsp;在 LangGraph 这样复杂的系统中，LangSmith 的调试能力尤为重要：

1. **可视化工作流**：直观看到每个节点的执行和数据流转
2. **性能分析**：识别瓶颈和优化点
3. **错误追踪**：快速定位问题所在
4. **对话历史**：查看多轮对话的完整上下文

#### 6.2 何时使用 Checkpoints

&emsp;&emsp;检查点功能适用于：
- **人机交互工作流**：暂停等待用户确认
- **长时间运行的任务**：从错误中恢复
- **多轮对话**：维护会话上下文
- **时间旅行调试**：回溯到之前的状态

#### 6.3 LangSmith vs 本地调试

| 对比项 | LangSmith | 本地调试 |
| ------ | --------- | -------- |
| **可视化** | 完整的 Web 界面 | 有限的终端输出 |
| **协作** | 团队共享 | 单用户 |
| **离线** | 需要网络 | 完全离线 |
| **成本** | 免费额度有限 | 无额外成本 |
| **性能开销** | 有 | 无 |

&emsp;&emsp;**建议**：开发阶段可以使用本地调试， Production 环境使用 LangSmith 进行监控和问题排查。