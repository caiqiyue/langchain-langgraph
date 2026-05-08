"""
第1阶段、ReAct构建原理
======================

本节内容：
1. LangGraph 与 ReAct 的关系
2. ReAct Agent 在 LangGraph 中的底层实现
3. Tool Calling Agent 与 ReAct 的区别

前置知识：
- 了解 LangGraph 基础概念（StateGraph、Node、Edge）
- 了解 Agent 基本原理
- 了解 Tool Calling 机制

学习目标：
- 理解 LangGraph 预置 ReAct 结构的实现原理
- 理解 Tool Calling 模式与 ReAct 模式的区别
- 掌握如何使用 create_react_agent 创建 ReAct Agent
"""