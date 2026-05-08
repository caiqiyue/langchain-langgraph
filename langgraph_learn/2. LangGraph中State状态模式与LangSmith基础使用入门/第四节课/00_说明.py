# 第4阶段说明
# 本节课程：MessageGraph源码解析

## 学习目标
1. 理解MessageGraph类的定义和作用
2. 掌握add_messages函数的核心逻辑
3. 理解MessageGraph与StateGraph的区别

## 核心概念
- MessageGraph：专门用于以消息为中心的工作流程的图
- add_messages：LangGraph预构建的Reducer函数
- StateGraph：更通用的状态图，支持复杂状态结构

## 课程文件
- 01_MessageGraph基础.py：演示MessageGraph的基本用法
- 02_add_messages函数.py：演示add_messages函数的行为

## 注意事项
- MessageGraph是StateGraph的子类
- add_messages可以跟踪消息ID并覆盖现有消息