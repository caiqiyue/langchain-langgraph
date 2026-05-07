# -*- coding: utf-8 -*-
"""
【案例 1】环境安装与配置
==========================

本案例展示 DeepAgents 的安装和基本配置。

安装步骤：
1. 安装 deepagents 包
2. 安装网络搜索工具（可选）
3. 加载环境变量
4. 初始化模型

要点：
1. 掌握 deepagents 安装方法
2. 理解基本配置流程
3. 了解常用依赖
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 1: 环境安装与配置")
print("=" * 60)

# ============================================================
# 2. 安装命令
# ============================================================
print("\n【安装命令】")
print("-" * 50)

print("""
# 安装 deepagents 框架
!pip install deepagents

# 安装网络搜索工具（可选）
!pip install langchain-tavily

# 安装代码美化库（可选）
!pip install rich
""")

# ============================================================
# 3. 环境变量
# ============================================================
print("\n【环境变量配置】")
print("-" * 50)

print("""
# .env 文件内容示例
DEEPSEEK_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
TAVILY_API_KEY=your-api-key
LANGSMITH_API_KEY=your-api-key
""")

# ============================================================
# 4. 快速初始化
# ============================================================
print("\n【快速初始化示例】")
print("-" * 50)

print("""
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
""")

# ============================================================
# 5. 版本检查
# ============================================================
print("\n【版本检查命令】")
print("-" * 50)

print("""
# 查看已安装版本
!pip list | grep -E 'langchain|deepagents'

# 检查 Python 版本
!python --version
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)