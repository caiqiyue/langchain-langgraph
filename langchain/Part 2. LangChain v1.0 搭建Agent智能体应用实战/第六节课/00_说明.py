# -*- coding: utf-8 -*-
"""
第六阶段：Agent 记忆系统 - 代码案例索引
==========================================

本文件夹包含 Agent 记忆系统的代码案例

文件列表：
00_说明.py                  - 本索引文件
01_短期记忆InMemorySaver.py  - 会话级记忆
02_上下文裁剪trim_messages.py - Token 控制
03_自定义State扩展.py       - 扩展状态结构
04_长期记忆向量数据库.py    - 跨会话记忆
05_跨线程记忆BaseStore.py   - 结构化用户档案

记忆类型：
- 短期记忆 (Checkpointer)  - 与 thread_id 生命周期绑定
- 长期记忆 (VectorStore)   - 跨会话持久化
- 跨线程记忆 (BaseStore)   - 结构化用户档案

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "Part 2. LangChain v1.0 搭建Agent智能体应用实战/第六节课/01_短期记忆InMemorySaver.py"
"""

print("=" * 60)
print("第六阶段：Agent 记忆系统")
print("=" * 60)
print("""
Agent 记忆三层架构：

1. 短期记忆 (Checkpointer)
   • InMemorySaver：内存存储，开发环境
   • PostgresSaver：数据库存储，生产环境
   • 生命周期：与 thread_id 绑定

2. 长期记忆 (VectorStore)
   • Chroma：轻量级向量数据库
   • Pinecone：云原生向量数据库
   • 检索方式：语义相似度搜索

3. 跨线程记忆 (BaseStore)
   • 结构化键值存储
   • 跨会话持久化用户档案

代码案例：
01_短期记忆InMemorySaver.py  - 会话级记忆
02_上下文裁剪trim_messages.py - Token 控制
03_自定义State扩展.py       - 扩展状态结构
04_长期记忆向量数据库.py    - 跨会话记忆
05_跨线程记忆BaseStore.py   - 结构化用户档案
""")