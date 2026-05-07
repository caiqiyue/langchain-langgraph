# -*- coding: utf-8 -*-
"""
【案例 1】环境配置与依赖安装
============================================

本案例展示 LangGraph 开发环境的基本配置和依赖安装

要点：
1. LangGraph 核心依赖安装
2. LangChain 和 LangGraph 的关系
3. OpenAI API 环境配置
"""

# ============================================================
# 1. 依赖安装
# ============================================================
# ! pip install langgraph==0.2.35
# ! pip install langchain==0.3.3 langchain-openai

# ============================================================
# 2. 环境配置
# ============================================================
import getpass
import os

# 配置 OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

print("=" * 50)
print("环境配置完成")
print("=" * 50)
print(f"LangGraph 版本已配置")
print(f"OpenAI API Key 已设置")