# -*- coding: utf-8 -*-
"""
【说明】第一节课 - LangGraph框架基础介绍
============================================

本节课内容：
1. LangGraph框架概述
2. LangGraph与LangChain的关系
3. LangGraph的核心设计思想（Nodes/Edges/State）
4. LangChain Chain构建示例

要点：
1. LangGraph是基于LangChain表达式语言构建的AI Agent开发框架
2. LangGraph支持多种大模型接入
3. LangGraph通过图结构解决线性序列的局限性
"""

# ============================================================
# 本节课核心概念
# ============================================================

"""
【核心概念】

1. LangGraph是什么？
   - LangGraph是以LangChain表达式语言(LCEL)为基础构建的AI Agent开发框架
   - 解决了基于LCEL的线性序列构建方式在复杂场景下的局限性

2. 核心设计思想
   - Nodes（节点）：可执行的功能单元
   - Edges（边）：定义节点间的流转逻辑
   - State（状态）：在节点间传递的共享状态

3. 与LangChain的区别
   - LangChain构建的是DAG（有向无环图）
   - LangGraph引入了循环图，支持更复杂的AI Agent工作流
"""

print("第一节课 - LangGraph框架基础介绍")
print("=" * 50)
print("本节课将介绍LangGraph框架的基本概念和设计思想")
