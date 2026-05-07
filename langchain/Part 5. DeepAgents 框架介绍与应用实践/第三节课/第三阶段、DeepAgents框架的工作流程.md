## <center>第三阶段、DeepAgents框架的工作流程

### 1. 环境安装与配置

#### 1.1 安装命令

```bash
# 安装 deepagents 框架
!pip install deepagents

# 安装网络搜索工具（可选）
!pip install langchain-tavily

# 安装代码美化库（可选）
!pip install rich
```

#### 1.2 环境变量配置

```bash
# .env 文件内容示例
DEEPSEEK_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
TAVILY_API_KEY=your-api-key
LANGSMITH_API_KEY=your-api-key
```

#### 1.3 快速初始化

```python
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 初始化模型
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0
)

# 测试模型
response = model.invoke("你好")
print(response.content)
```

### 2. create_deep_agent详解

#### 2.1 默认配置

| 配置项 | 默认值 |
|--------|--------|
| 默认模型 | Claude Sonnet 4 或 GPT-4o（推荐） |
| 内置工具 | 7 个核心文件操作工具 |
| 子代理支持 | 支持子代理调用，自动隔离上下文 |

#### 2.2 关键参数

| 参数 | 类型 | 说明 |
|------|------|------|
| model | BaseChatModel | 语言模型 |
| tools | list[BaseTool] | 自定义工具集 |
| system_prompt | str | 系统提示词 |
| subagents | list[dict] | 子代理配置 |
| backend | SandboxBackend | 文件存储后端 |
| interrupt_on | dict[str, bool] | 人机交互配置 |
| checkpointer | BaseCheckpointSaver | 检查点（状态持久化） |

#### 2.3 基本使用示例

```python
from deepagents import create_deep_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

# 1. 初始化工具
tavily = TavilySearch(max_results=3)

# 2. 编写系统提示词
system_prompt = """
您是一位资深的研究人员。
您的工作是进行深入的研究。
## 可用工具
### 互联网搜索
使用此功能进行搜索。
## 工作流程
1. 分解任务步骤
2. 收集信息
3. 整合报告
4. 保存文件
"""

# 3. 创建 DeepAgent
agent = create_deep_agent(
    name="DeepAgent_Researcher",
    tools=[tavily],
    model=model,
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
)

# 4. 执行任务
config = {"configurable": {"thread_id": "1"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "查询 deepagents 框架动态"}]},
    config=config
)
```

#### 2.4 interrupt_on 参数

```python
# interrupt_on 用于人机交互配置（HITL）
interrupt_on={"write_file": True}
# 当 Agent 试图调用 write_file 时暂停

# 使用场景：
# 1. 安全审核（删除文件）
# 2. 成本控制（调用昂贵 API）
# 3. 质量保证（人工确认）
```

### 3. Agent内置工具分类

#### 3.1 工具分类表

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 工具分类                        │
├──────────────────┬──────────────────────────────────────┤
│ 用户工具          │ TavilySearch, Calculator, MCP Tools   │
├──────────────────┼──────────────────────────────────────┤
│ 文件系统工具      │ ls, read_file, write_file, edit_file   │
│                  │ glob, grep, execute                   │
├──────────────────┼──────────────────────────────────────┤
│ 系统工具          │ write_todos, task                    │
└──────────────────┴──────────────────────────────────────┘
```

#### 3.2 文件系统工具详解

| 工具 | 功能 | 特点 |
|------|------|------|
| ls | 浏览目录结构 | 支持模式匹配 |
| read_file | 读取文件内容 | 支持 offset/limit 分页 |
| write_file | 创建新文件 | 整体覆盖写入 |
| edit_file | 修改文件 | 支持精确字符串替换 |
| glob | 通配符查找文件 | 如 *.py, **/*.md |
| grep | 正则表达式搜索 | 代码定位神器 |
| execute | 执行 Shell 命令 | 需 Sandbox 支持 |

#### 3.3 系统工具详解

**write_todos（待办事项工具）**：
- 生成带优先级/依赖关系的 JSON 任务列表
- 状态：pending → completed
- 支持动态调整

**task（子代理工具）**：
- 动态生成子 Agent
- 支持独立上下文窗口
- 结果通过文件系统回传
- 可配置 max_iterations 防止无限递归

### 4. 拓展思考

#### 4.1 create_deep_agent 的底层实现

&emsp;&emsp;理解 `create_deep_agent` 的底层实现有助于更好地使用它：

**核心流程**：
```python
def create_deep_agent(model, tools, system_prompt, ...):
    # 1. 构建系统提示词
    full_system_prompt = build_system_prompt(
        base_prompt=BASE_AGENT_PROMPT,
        custom_prompt=system_prompt
    )

    # 2. 创建 Agent（基于 LangGraph）
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=full_system_prompt,
        ...
    )

    # 3. 应用中间件
    agent = apply_middlewares(agent, middlewares)

    return agent
```

#### 4.2 与 LangChain Agents 的对比

&emsp;&emsp;DeepAgents 的 `create_deep_agent` 与 LangChain 的 `create_agent` 有何不同？

| 特性 | LangChain create_agent | DeepAgents create_deep_agent |
|------|------------------------|------------------------------|
| 内置工具 | 无 | 7个文件系统 + 规划/子代理 |
| 中间件 | 手动配置 | 自动应用 Base Agent 提示词 |
| Backend | 无 | Filesystem/Docker/E2B |
| 子代理 | 需手动实现 | 内置 task 工具 |