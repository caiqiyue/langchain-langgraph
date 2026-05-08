# 第1阶段说明
# 本节课程：State状态模式的定义

## 学习目标
1. 理解LangGraph中State的概念和作用
2. 掌握使用字典类型定义状态的方法
3. 理解节点如何访问、读取和写入状态

## 核心概念
- State：共享的数据结构，用于在图的各个节点之间传递信息
- Node：节点，通过边来指示下一个工作步骤
- Edge：边，连接节点的连线

## 课程文件
- 01_字典类型定义状态.py：演示使用dict定义State
- 02_State定义模式.py：使用TypedDict定义State
- 03_图可视化与执行.py：图的编译和执行

## 注意事项
- 安装依赖：pip install pyppeteer ipython