## <center>第一阶段、Agent开发项目的可观测性基石</center>

### 1. LangSmith 核心概念

LangSmith 是 LangChain 的监控平台，提供三大核心功能：

- **Trace**：端到端追踪，记录完整请求链路
- **Run**：单次执行节点，记录单个步骤的执行
- **Feedback**：质量评估，支持分数和标签

```
层级关系：Project > Trace > Run > Feedback
```

### 2. LangSmith 配置步骤

```python
# 1. 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = "your-api-key"
os.environ["LANGSMITH_PROJECT"] = "your-project"

# 2. Agent 执行自动被追踪
agent = create_agent(model, tools, ...)
result = agent.invoke({"messages": [...]})
```

### 3. 可观测性工具栈

| 工具 | 作用 |
|------|------|
| LangGraph Studio | 图结构可视化与调试 |
| LangGraph CLI | 服务部署工具 |
| LangSmith | 监控框架 |

### 4. 课程案例

本阶段的代码案例位于 `第一节课/` 目录下：

| 文件 | 内容说明 |
|------|---------|
| `01_LangSmith入门.py` | LangSmith 平台配置与使用 |

**运行示例**：

```bash
python "Part 3. LangChain1.0 Agent智能体中间件应用实战/第一节课/01_LangSmith入门.py"
```