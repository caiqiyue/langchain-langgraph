## <center>第一阶段、DeepAgents框架定位与价值</center>

### 1. DeepAgents 定位

DeepAgents 是基于 LangChain/LangGraph 的企业级 Agent 框架。

![DeepAgents框架定位](../assets/第一课_01_DeepAgents定位.html)

**图解说明**：LangChain（积木） → LangGraph（地基） → DeepAgents（加速器）

### 2. 解决的五大问题

| 问题 | DeepAgents 解决方案 |
|------|-------------------|
| 规划能力缺失 | 内置规划工具（write_todos/read_todos） |
| 遗忘与混乱 | 上下文压缩 + 记忆管理 |
| 环境交互困难 | 文件系统 + 沙箱系统 |
| 上下文污染 | 状态隔离 + 中间件控制 |
| 协作编排复杂 | 子代理机制 + 统一调度 |

### 3. 四大支柱

| 支柱 | 角色定位 | 核心功能 |
|------|---------|---------|
| 系统提示词 | 行为总导演 | 定义 Agent"世界观" |
| 规划工具 | 任务架构师 | write_todos/read_todos |
| 文件系统 | 上下文仓库 | ls/read/write/edit |
| 子代理 | 执行特派员 | task 工具动态生成 |

### 4. 核心 API

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-4o",
    tools=[custom_tools],
    system_prompt="你是一个专业研究助手",
    subagents=[research_agent, writing_agent],
    backend="docker",
    interrupt_on=True
)
```

### 5. 课程案例

| 文件 | 内容说明 |
|------|---------|
| `01_DeepAgents框架介绍.py` | 框架定位与核心价值 |

**运行示例**：

```bash
python "Part 5. DeepAgents 框架介绍与应用实践/第一节课/01_DeepAgents框架介绍.py"
```