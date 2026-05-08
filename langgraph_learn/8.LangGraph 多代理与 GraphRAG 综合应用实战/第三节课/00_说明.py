# -*- coding: utf-8 -*-
"""
第三阶段 + 第四阶段 + 第五阶段：GraphRAG 与混合多知识库检索 - 代码案例索引
==============================================================================

本文件夹包含以下阶段的代码案例：
- 第三阶段：GraphRAG基本介绍
- 第四阶段：GraphRAG核心架构
- 第五阶段：Multi-Agent实现混合多知识库检索

文件列表：
00_说明.py                  - 代码案例索引说明（当前文件）
01_GraphRAG环境配置.py        - GraphRAG环境配置与Neo4j连接
02_GraphRAG系统实现.py        - GraphRAG系统实现
03_混合多知识库检索.py        - 混合多知识库检索案例

运行方式：
    cd E:\langchain_learning
    conda activate langchain_learning
    python "第三节课/00_说明.py"

配置：
    Neo4j Aura: neo4j+s://xxx.databases.neo4j.io
    Milvus Cloud: https://in03-xxx.serverless.gcp-us-west1.cloud.zilliz.com
"""

print("=" * 60)
print("第三阶段 + 第四阶段 + 第五阶段")
print("GraphRAG 与混合多知识库检索")
print("=" * 60)
print("""
本文件夹包含以下阶段的代码案例：

第三阶段：GraphRAG基本介绍
  - 了解GraphRAG与传统RAG的区别
  - 理解GraphRAG的核心概念

第四阶段：GraphRAG核心架构
  - Neo4j图数据库的配置与使用
  - GraphRAG索引与查询流程

第五阶段：Multi-Agent实现混合多知识库检索
  - 结合GraphRAG和传统RAG
  - Supervisor架构协调多知识库检索

文件列表：
00_说明.py                  - 代码案例索引说明（当前文件）
01_GraphRAG环境配置.py        - GraphRAG环境配置与Neo4j连接
02_GraphRAG系统实现.py        - GraphRAG系统实现
03_混合多知识库检索.py        - 混合多知识库检索案例

运行示例：
    python "第三节课/01_GraphRAG环境配置.py"
""")