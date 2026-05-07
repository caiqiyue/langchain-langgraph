# -*- coding: utf-8 -*-
"""
【案例 3】Agent 内置工具分类
==============================

本案例展示 DeepAgents Agent 内置的工具分类。

工具分类：
1. 用户自定义工具（User Tools）
   - 用户传入的工具（如 TavilySearch）

2. 文件系统工具（FileSystem Tools）
   - ls: 浏览目录
   - read_file: 读取文件
   - write_file: 写入文件
   - edit_file: 修改文件
   - glob: 模式匹配
   - grep: 正则搜索
   - execute: 执行命令

3. 系统工具（System Tools）
   - write_todos: 写入待办事项
   - task: 创建子代理

要点：
1. 掌握工具分类
2. 理解文件系统工具用法
3. 了解待办事项工具
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 3: Agent 内置工具分类")
print("=" * 60)

# ============================================================
# 2. 工具分类表
# ============================================================
print("\n【工具分类表】")
print("-" * 50)

分类表 = """
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
"""
print(分类表)

# ============================================================
# 3. 文件系统工具详解
# ============================================================
print("\n【文件系统工具详解】")
print("-" * 50)

工具详解 = """
| 工具         | 功能                     | 特点                    |
|--------------|--------------------------|------------------------|
| ls           | 浏览目录结构              | 支持模式匹配            |
| read_file    | 读取文件内容              | 支持 offset/limit 分页 |
| write_file   | 创建新文件               | 整体覆盖写入            |
| edit_file    | 修改文件                  | 支持精确字符串替换      |
| glob         | 通配符查找文件            | 如 *.py, **/*.md        |
| grep         | 正则表达式搜索            | 代码定位神器            |
| execute      | 执行 Shell 命令           | 需 Sandbox 支持        |
"""
print(工具详解)

# ============================================================
# 4. 系统工具详解
# ============================================================
print("\n【系统工具详解】")
print("-" * 50)

print("""
write_todos（待办事项工具）：
  - 生成带优先级/依赖关系的 JSON 任务列表
  - 状态：pending → completed
  - 支持动态调整

task（子代理工具）：
  - 动态生成子 Agent
  - 支持独立上下文窗口
  - 结果通过文件系统回传
  - 可配置 max_iterations 防止无限递归
""")

# ============================================================
# 5. 获取工具列表代码
# ============================================================
print("\n【获取工具列表代码】")
print("-" * 50)

print("""
from rich.console import Console
from rich.table import Table

def print_agent_tools(agent):
    console = Console()
    table = Table(title="Agent 工具列表")

    # 获取 tools 节点
    tools_node = agent.nodes['tools'].bound
    tools = tools_node.tools_by_name

    for name, tool in tools.items():
        # 分类显示
        if name in ['ls', 'read_file', 'write_file', ...]:
            category = "文件系统工具"
        elif name in ['write_todos', 'task']:
            category = "系统工具"
        else:
            category = "用户工具"

        table.add_row(category, name, tool.description[:50])

    console.print(table)
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)