"""
第3阶段、基于记忆Store知识库

本节内容概述：
- 长期记忆与Store机制
- InMemoryStore的使用
- 跨线程记忆共享
- 知识库构建

代码文件列表：
- 01_InMemoryStore初始化.py：初始化InMemoryStore
- 02_定义命名空间.py：定义存储的命名空间
- 03_保存记忆到存储.py：使用put方法保存记忆
- 04_检索记忆.py：检索命名空间中的记忆
- 05_带Store的图构建.py：构建带Store的完整图
- 06_跨线程测试.py：跨线程记忆测试（相同user_id）
- 07_新线程测试.py：新线程测试（相同user_id）
- 08_新用户测试.py：新用户测试（新user_id）
- 09_查看存储的记忆.py：直接访问store查看记忆信息
"""