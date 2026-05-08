# -*- coding: utf-8 -*-
"""
【说明】第二节课 - LangGraph核心底层机制
============================================

本节课内容：
1. Graph基类的结构与源码解析
2. StateGraph状态图的使用
3. TypedDict类型定义
4. Nodes节点的定义与添加
5. Edges边的类型与使用
6. Graph的编译与调用

要点：
1. Graph类是所有图结构的基础
2. StateGraph继承自Graph，用于管理状态
3. 节点是可执行函数，接收State并返回更新的State
4. 边定义节点间的流转逻辑
"""

# ============================================================
# 本节课核心概念
# ============================================================

"""
【核心组件】

1. Graph基类
   - nodes: 存储图中所有节点
   - edges: 存储图中所有边
   - branches: 存储条件分支
   - support_multiple_edges: 是否支持同一对节点间的多条边
   - compiled: 图是否已被编译

2. 核心方法
   - add_node(): 添加节点
   - add_edge(): 添加边
   - add_conditional_edges(): 添加条件边
   - set_entry_point(): 设置入口点
   - set_finish_point(): 设置结束点
   - compile(): 编译图

3. StateGraph
   - state_schema: 定义图状态的结构
   - config_schema: 定义配置的结构
   - 继承自Graph类
"""

print("第二节课 - LangGraph核心底层机制")
print("=" * 50)
print("本节课将深入解析Graph/StateGraph/Nodes/Edges的实现原理")
