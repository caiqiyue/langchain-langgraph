# -*- coding: utf-8 -*-
"""
【案例 2】create_deep_agent 详解
=================================

本案例展示 create_deep_agent 的核心用法和参数。

核心函数：create_deep_agent()
- 创建功能完整的深度智能体
- 封装了 LangGraph 的复杂逻辑
- 提供高级 API

关键参数：
- model: 语言模型
- tools: 自定义工具集
- system_prompt: 系统提示词
- subagents: 子代理配置
- backend: 文件存储后端
- interrupt_on: 人机交互配置

要点：
1. 掌握 create_deep_agent 基本用法
2. 理解关键参数作用
3. 学会配置 DeepAgent
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: create_deep_agent 详解")
print("=" * 60)

# ============================================================
# 2. 默认配置
# ============================================================
print("\n【默认配置】")
print("-" * 50)

print("""
create_deep_agent 默认配置：

1. 默认模型：
   - Claude Sonnet 4 或 GPT-4o（推荐）

2. 内置工具：
   - 7 个核心文件操作工具
   - 待办事项管理功能

3. 子代理支持：
   - 支持子代理调用
   - 自动隔离上下文
""")

# ============================================================
# 3. 关键参数
# ============================================================
print("\n【关键参数】")
print("-" * 50)

参数表 = """
| 参数            | 类型                | 说明                        |
|-----------------|---------------------|----------------------------|
| model           | BaseChatModel       | 语言模型                    |
| tools           | list[BaseTool]      | 自定义工具集                |
| system_prompt   | str                 | 系统提示词                  |
| subagents       | list[dict]          | 子代理配置                  |
| backend         | SandboxBackend      | 文件存储后端                |
| interrupt_on    | dict[str, bool]     | 人机交互配置                |
| checkpointer    | BaseCheckpointSaver | 检查点（状态持久化）        |
"""
print(参数表)

# ============================================================
# 4. 基本使用示例
# ============================================================
print("\n【基本使用示例】")
print("-" * 50)

print("""
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
""")

# ============================================================
# 5. interrupt_on 参数
# ============================================================
print("\n【interrupt_on 参数】")
print("-" * 50)

print("""
interrupt_on 用于人机交互配置（HITL）：

- 类型：dict[str, bool | InterruptOnConfig]
- 作用：控制何时中断执行等待人工审批

示例：
  interrupt_on={"write_file": True}
  # 当 Agent 试图调用 write_file 时暂停

使用场景：
  1. 安全审核（删除文件）
  2. 成本控制（调用昂贵 API）
  3. 质量保证（人工确认）
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)