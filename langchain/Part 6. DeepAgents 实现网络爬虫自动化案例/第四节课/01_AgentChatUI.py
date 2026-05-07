# -*- coding: utf-8 -*-
"""
【案例 1】Agent Chat CLI 工具
==============================

本案例展示 Agent Chat UI 的安装和配置。

Agent Chat UI：
- LangGraph/LangChain 官方前端对话面板
- 用于与后端 Agent 进行实时互动

核心功能：
- 上传文件
- 多工具协同
- 结构化输出
- 多轮对话
- 调试标注

安装步骤：
1. Git 克隆项目
2. 安装 Node.js / npm
3. 安装 pnpm
4. 安装项目依赖
5. 启动服务

要点：
1. 掌握 Agent Chat UI 安装方法
2. 理解前端配置
3. 学会启动和使用对话界面
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 1: Agent Chat CLI 工具")
print("=" * 60)

# ============================================================
# 2. Agent Chat UI 简介
# ============================================================
print("\n【Agent Chat UI 简介】")
print("-" * 50)

print("""
Agent Chat UI 是 LangGraph/LangChain 官方提供的：

  - 多智能体前端对话面板
  - 用于与后端 Agent 进行实时互动

项目主页：https://github.com/langchain-ai/agent-chat-ui

核心功能：
  - 上传文件
  - 多工具协同
  - 结构化输出
  - 多轮对话
  - 调试标注
""")

# ============================================================
# 3. 安装步骤
# ============================================================
print("\n【安装步骤】")
print("-" * 50)

步骤表 = """
| 步骤 | 命令                        | 说明           |
|------|----------------------------|----------------|
| 1    | git clone <repo>           | 克隆项目       |
| 2    | npm install -g pnpm         | 安装 pnpm       |
| 3    | pnpm install                | 安装依赖        |
| 4    | pnpm dev                    | 启动开发服务器  |
"""
print(步骤表)

# ============================================================
# 4. 安装命令
# ============================================================
print("\n【安装命令】")
print("-" * 50)

print("""
# Step 1: Git 克隆项目
git clone https://github.com/langchain-ai/agent-chat-ui.git
cd agent-chat-ui

# Step 2: 安装 pnpm
npm install -g pnpm

# Step 3: 安装项目依赖
pnpm install

# Step 4: 启动服务
pnpm dev
""")

# ============================================================
# 5. 配置后端
# ============================================================
print("\n【配置后端】")
print("-" * 50)

print("""
Agent Chat UI 需要连接后端 Agent 服务：

1. 配置环境变量
   - LANGCHAIN_API_KEY
   - LANGCHAIN_TRACING_V2
   - 后端服务地址

2. 启动后端服务
   - 确保 Agent 服务运行
   - 默认端口 8000

3. 前端对接
   - 修改 .env 配置
   - 重启前端服务
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)