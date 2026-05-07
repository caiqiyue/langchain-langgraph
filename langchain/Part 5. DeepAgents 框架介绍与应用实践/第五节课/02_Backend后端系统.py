# -*- coding: utf-8 -*-
"""
【案例 2】Backend 后端系统
===========================

本案例展示 DeepAgents 的各种 Backend 后端实现。

Backend 作用：
- 定义"外部世界"的交互能力
- 文件存在哪？代码在哪跑？

Backend 类型：

1. FilesystemBackend
   - 本地磁盘操作
   - 支持虚拟文件系统

2. DockerBackend
   - Docker 容器隔离
   - 安全执行代码

3. E2BBackend
   - 云端沙箱
   - 无需本地 Docker

4. StoreBackend
   - 数据库存储
   - PostgreSQL 支持

5. CompositeBackend
   - 混合模式
   - 根据路径路由到不同后端

Backend vs Checkpointer vs Store：
- Backend：环境层（文件在哪、代码在哪跑）
- Checkpointer：状态层（当前对话上下文）
- Store：记忆层（跨会话知识积累）

要点：
1. 理解各种 Backend 的适用场景
2. 掌握 Backend 配置方法
3. 理解 Backend 与其他组件的区别
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: Backend 后端系统")
print("=" * 60)

# ============================================================
# 2. Backend 类型对比
# ============================================================
print("\n【Backend 类型对比】")
print("-" * 50)

类型对比 = """
| Backend            | 存储位置   | 执行环境   | 适用场景              |
|--------------------|-----------|-----------|----------------------|
| FilesystemBackend  | 本地磁盘   | 宿主机     | 本地开发、快速原型    |
| DockerBackend      | 本地磁盘   | Docker 容器 | 安全隔离、标准化环境  |
| E2BBackend         | 云端       | 云端沙箱   | 云端部署、多租户     |
| StoreBackend       | 数据库     | 宿主机     | 数据持久化、查询      |
| CompositeBackend   | 混合       | 混合       | 性能优化、混合云      |
"""
print(类型对比)

# ============================================================
# 3. FilesystemBackend
# ============================================================
print("\n【FilesystemBackend】")
print("-" * 50)

print("""
FilesystemBackend 直接操作本地磁盘：

backend = FilesystemBackend(
    root_dir="./workspace",
    virtual_mode=True  # 启用虚拟文件系统
)

特点：
  - 简单易用
  - 适合本地开发
  - virtual_mode 将 Agent 操作映射到指定目录
""")

# ============================================================
# 4. DockerBackend
# ============================================================
print("\n【DockerBackend】")
print("-" * 50)

print("""
DockerBackend 在 Docker 容器中执行：

backend = DockerBackend(
    image="python:3.11-slim",
    auto_remove=True,
    cpu_quota=50000,
    memory_limit="512m",
    network_disabled=False
)

特点：
  - 安全隔离（代码在容器内运行）
  - 环境一致性（标准化镜像）
  - 生命周期自动管理
  - 可配置资源限制
""")

# ============================================================
# 5. E2BBackend
# ============================================================
print("\n【E2BBackend】")
print("-" * 50)

print("""
E2BBackend 使用云端沙箱：

backend = E2BBackend(
    template="base",
    api_key=os.getenv("E2B_API_KEY")
)

特点：
  - 无需本地 Docker
  - 云端安全隔离
  - 适合生产环境
  - 按使用时长计费
""")

# ============================================================
# 6. Backend vs Checkpointer vs Store
# ============================================================
print("\n【Backend vs Checkpointer vs Store】")
print("-" * 50)

对比表 = """
| 组件          | 层级        | 负责              | 生命周期     |
|---------------|-------------|-------------------|--------------|
| Backend       | 环境层       | 文件存在哪、代码在哪跑 | 任务级      |
| Checkpointer  | 状态层       | 当前对话上下文      | 线程级       |
| Store         | 记忆层       | 跨会话知识积累      | 全局级       |

比喻：
  - Backend = 工作台/电脑
  - Checkpointer = 大脑工作记忆
  - Store = 日记本/知识库
"""
print(对比表)

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)