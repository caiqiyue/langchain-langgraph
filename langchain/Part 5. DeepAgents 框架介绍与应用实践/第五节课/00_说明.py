# -*- coding: utf-8 -*-
"""
第五节课说明
==================================================

本节课涵盖以下内容：

1. 文件系统中间件
   - FilesystemMiddleware
   - 核心工具集（ls, read_file, write_file 等）

2. Backend 后端系统
   - FilesystemBackend（本地磁盘）
   - DockerBackend（Docker 容器）
   - E2BBackend（云端沙箱）
   - StoreBackend（数据库存储）
   - CompositeBackend（混合模式）

3. interrupt_on 参数
   - Human-in-the-Loop 配置
   - 人工审批机制

学习要点：
- 掌握文件系统工具的用法
- 理解各种 Backend 的适用场景
- 学会配置 HITL 人机交互
"""

print("=" * 60)
print("第五节课：文件系统与沙箱系统")
print("=" * 60)