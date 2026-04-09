# <center>第三阶段、 DeepAgents 核心功能介绍

* **注意：** 没有学习LangChain的用户，建议先学习LangChain1.0的基础内容，再学习DeepAgents。

## 一、安装环境与依赖

```python
!python --version```

```python
# 安装deepagents依赖
!pip install deepagents```

```python
# 查看版本
!pip list | grep -E 'langchain|deepagents'
```

```python
# from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

# 1. 加载.env环境变量
load_dotenv(override=True)

# 2. 初始化模型
model = ChatDeepSeek(model="deepseek-chat", temperature=0)
model.invoke("你好")```

## 二、 核心入口：`create_deep_agent()`


这是整个框架的核心函数，它创建了一个功能完整的深度智能体。

**默认配置**：

- 使用 Claude Sonnet 4 或 GPT-4o 作为默认模型（推荐）。

- 集成 7 个核心文件操作工具。

- 提供待办事项管理功能。

- 支持子代理调用。

**关键参数**：

- `model`: 支持自定义语言模型。

- `tools`: 自定义工具集。

- `system_prompt` : 系统提示词

- `subagents`: 子代理配置。

- `backend`: 文件存储后端。

- `interrupt_on`: **人机交互配置 (Human-in-the-Loop)**。允许在特定节点暂停 Agent 执行，等待人工干预。这对于安全审核（删除文件）、成本控制（调用昂贵 API）和质量保证至关重要。

```python
from deepagents import create_deep_agent

create_deep_agent?```

```python
# 安装网络搜索工具
!pip install langchain-tavily```

```python
from deepagents import create_deep_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

# 1. 初始化 Tavily 搜索工具
tavily = TavilySearch(max_results=3)

# 2. 编写系统提示词
research_instructions = """
您是一位资深的研究人员。您的工作是进行深入的研究，然后撰写一份精美的报告。
您可以通过互联网搜索引擎作为主要的信息收集工具。
## 可用工具
### `互联网搜索`
使用此功能针对给定的查询进行互联网搜索。您可以指定要返回的最大结果数量、主题以及是否包含原始内容。
### `写入本地文件`
使用此功能将研究报告保存到本地文件。当您完成研究并生成报告后，请使用此工具将完整的报告内容保存到文
件中。
- 文件路径建议使用 .md 格式（Markdown），例如 "research_report.md" 或 "./reports/报告名
称.md"
- 请确保报告内容完整、结构清晰，包含所有章节和引用来源
## 工作流程
在进行研究时：
1. 首先将研究任务分解为清晰的步骤
2. 使用互联网搜索来收集全面的信息
3. 将信息整合成一份结构清晰的报告
4. **重要**：完成报告后，务必使用 `写入本地文件` 工具将完整报告保存到本地文件
5. 务必引用你的资料来源
**注意**：请确保在完成研究后，将完整的报告内容保存到文件中，这样用户可以方便地查看和保存报告。
"""

# 2. 创建 DeepAgents 智能体
agent = create_deep_agent(
    name="DeepAgents_Agent",       # 智能体名称
    tools=[tavily],                # 可调用工具Tool
    model=model,                   # 模型Model
    system_prompt=research_instructions,  # 系统提示词
    checkpointer=InMemorySaver(),  # 检查点Checkpointer，内存检查点
)

# 3. 配置线程 ID
config = {"configurable": {"thread_id": "1"}}

result = agent.invoke({"messages": [{"role": "user", "content": "帮我查询一下有关deepagents框架的最新动态"}]}, config=config)
```

```python
print(result["messages"][-1].content)
```

## 三、 `create_deep_agent` 内部结构


* 源码参数截图

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251216190623938.png
" width=70%></div>


```python
# 安装美化代码库Rich
!pip install rich
```

```python
# 导入Rich库，用于美化代码
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
RICH_AVAILABLE = True
console = Console()

def print_agent_tools(agent):
    """
    打印 Agent 中加载的所有工具
    包括用户自定义工具、文件系统工具、系统工具等
    """
    # 获取 agent 的 nodes (LangGraph 的节点)
    if hasattr(agent, 'nodes') and 'tools' in agent.nodes:
        tools_node = agent.nodes['tools']

        # tools_node 是 PregelNode，真正的 ToolNode 在 bound 属性中
        if hasattr(tools_node, 'bound'):
            tool_node = tools_node.bound

            # 从 ToolNode 获取工具
            if hasattr(tool_node, 'tools_by_name'):
                tools = tool_node.tools_by_name

                # 分类工具
                user_tools = []
                filesystem_tools = []
                system_tools = []

                for tool_name, tool in tools.items():
                    tool_info = {
                        'name': tool_name,
                        'description': getattr(tool, 'description', '无描述')
                    }

                    # 分类
                    if tool_name in ['ls', 'read_file', 'write_file', 'edit_file', 'glob', 'grep', 'execute']:
                        filesystem_tools.append(tool_info)
                    elif tool_name in ['write_todos', 'task']:
                        system_tools.append(tool_info)
                    else:
                        user_tools.append(tool_info)

                # 打印加载工具的输出
                _print_tools_rich(user_tools, filesystem_tools, system_tools)

            else:
                print("无法获取工具列表 (tools_by_name 不存在)")
        else:
            print("无法获取工具列表 (bound 属性不存在)")
    else:
        print("无法获取工具列表 (nodes 结构不符合预期)")

def _print_tools_rich(user_tools, filesystem_tools, system_tools):
    """使用 Rich 库美化打印工具列表"""
    console.print()

    # 创建表格
    table = Table(title="Agent 加载的工具列表", show_header=True, header_style="bold magenta")
    table.add_column("类别", style="cyan", width=20)
    table.add_column("工具名称", style="green", width=20)
    table.add_column("描述", style="white", width=60)

    # 添加用户工具
    for i, tool in enumerate(user_tools):
        category = "用户工具" if i == 0 else ""
        desc = tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
        table.add_row(category, tool['name'], desc)

    # 添加文件系统工具
    for i, tool in enumerate(filesystem_tools):
        category = "文件系统工具" if i == 0 else ""
        desc = tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
        table.add_row(category, tool['name'], desc)

    # 添加系统工具
    for i, tool in enumerate(system_tools):
        category = "系统工具" if i == 0 else ""
        desc = tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
        table.add_row(category, tool['name'], desc)

    console.print(table)

    # 打印统计
    total = len(user_tools) + len(filesystem_tools) + len(system_tools)
    console.print(Panel(
        f"[bold green]共计 {total} 个工具[/bold green]\n\n"
        f"• 用户工具: {len(user_tools)} 个\n"
        f"• 文件系统工具: {len(filesystem_tools)} 个\n"
        f"• 系统工具: {len(system_tools)} 个",
        title="统计信息",
        border_style="green"
    ))
    console.print()```

```python
print_agent_tools(agent)```

这里可以看到，除了自己定义的工具（如 Tavily 搜索），DeepAgents 还默认添加了一些其他工具：

* **文件系统中间件**（FileSystemMiddleware）: 用于读写、查询、执行文件系统中的文件。

* **待办事项中间件**（TodoListMiddleware）: write_todos 用于写入待办事项，task 用于创建子agent来执行待办事项。

这些都是 DeepAgents 特有的功能，用于支持智能体在实际应用中的各种场景。那么，接下来我们来看看这些功能的具体应用。

* Langgraph Studio 中可视化结构图：能看到

    * PatchToolCallsMiddleware用于 自动检测并修复“悬空”的工具调用 的关键中间件，确保工具调用的完整性和正确性。

    * SummarizationMiddleware上下文压缩中间件，防止上下文过长

<div align=center><img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251216190623943.png
" width=70%></div>

