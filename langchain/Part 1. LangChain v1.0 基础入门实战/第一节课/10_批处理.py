# -*- coding: utf-8 -*-
"""
【案例 10】批处理与并发控制
==========================================

本案例展示 LangChain 的批处理功能
用于一次性处理多个请求

要点：
1. batch() 批量调用
2. batch_as_completed() 逐个返回
3. 并发控制
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / ".env"
load_dotenv(env_path, override=True)

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")
os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 10: 批处理与并发控制")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnableConfig

model = ChatTongyi(model="qwen3-max", temperature=0.7)

questions = [
    "什么是 Python？",
    "什么是 JavaScript？",
    "什么是 Rust？",
    "什么是 Go？",
    "什么是 Java？"
]

# ============================================================
# 1. batch() 批量调用
# ============================================================
print("\n1. batch() 批量调用")
print("-" * 30)

print(f"准备处理 {len(questions)} 个问题...")

start = time.time()
responses = model.batch(questions)
end = time.time()

print(f"总耗时: {end - start:.2f} 秒")
print(f"\n结果:")
for i, resp in enumerate(responses):
    preview = resp.content[:40] + "..." if len(resp.content) > 40 else resp.content
    print(f"  {i+1}. {preview}")

# ============================================================
# 2. batch_as_completed() 逐个返回
# ============================================================
print("\n2. batch_as_completed() 逐个返回")
print("-" * 30)

print("先完成先返回:")
for future in model.batch_as_completed(questions):
    index, response = future
    preview = response.content[:30] + "..." if len(response.content) > 30 else response.content
    print(f"  [完成 {index}] {preview}")

# ============================================================
# 3. 并发控制
# ============================================================
print("\n3. 并发控制")
print("-" * 30)

"""
【并发控制的作用】
- 避免超出 API 速率限制
- 避免客户端资源耗尽
- 配合服务端的限流策略
"""

import asyncio

async def async_batch_with_control():
    config = RunnableConfig(
        max_concurrency=2,     # 最多 2 个并发
        timeout=30.0,          # 单任务超时
        metadata={"task": "batch_demo"}
    )

    print(f"并发数限制: 2")
    start = time.time()
    responses = await model.abatch(questions, config=config)
    end = time.time()

    print(f"耗时: {end - start:.2f} 秒")
    return responses

asyncio.run(async_batch_with_control())

# ============================================================
# 【补充】batch 原理
# ============================================================
print("\n" + "=" * 50)
print("batch 原理")
print("=" * 50)
print("""
【batch 的实现】

LangChain 的 batch 不是调用模型提供商的批量 API
（虽然有些提供商有批量 API）

而是：
1. 收集所有输入
2. 使用线程池/异步并发调用
3. 收集所有结果

【并发控制原理】

max_concurrency = 2 意味着：
- 同时最多只有 2 个任务在执行
- 第 3 个任务要等前 2 个中有一个完成

示意图：
Task1 ────────────────────────────────>
Task2 ─────────────────>
Task3 ───────（等待）──────>

【什么时候适合高并发？】
- I/O 密集型：API 调用（等待网络响应）
- CPU 密集型：不适合（单核占满时是竞争）

【什么时候不适合高并发？】
- 本地模型推理（GPU/CPU 密集型）
- 资源有限的服务器
""")

"""
这个案例其实已经进入：

LangChain 的“工程化”阶段了。

前面的：

invoke

PromptTemplate

stream

更多还是：

“怎么调用大模型”
而这里：

batch / 并发控制
开始变成：

“怎么高效、大规模调用大模型”
这是 AI 工程里非常核心的一块。

因为：

真正的 AI 系统，不会一次只处理一个请求。

比如：

批量生成摘要

批量翻译

批量向量化

批量评测

RAG 文档处理

Agent 多任务

全部都依赖：

并发 + 批处理
一、先建立整体认知
你现在必须先理解：

这里根本不是“大模型知识”
而是：

“并发编程 + IO 工程”
整个案例的核心：

功能	本质
batch()	同时发多个请求
batch_as_completed()	谁先完成先返回
max_concurrency	限制同时运行数量
abatch()	异步并发版本
RunnableConfig	运行时配置
并发	同时处理多个 IO 任务
二、为什么需要 batch？
普通 invoke 的问题
如果你这样：

for q in questions:
    model.invoke(q)
流程：

问题1 -> 等待完成
问题2 -> 等待完成
问题3 -> 等待完成
叫：

串行执行（Sequential）
假设：

每个请求 3 秒。

5 个问题：

3 × 5 = 15 秒
batch 的核心
batch：

model.batch(questions)
会：

5 个请求一起发
于是：

总时间 ≈ 最慢那个请求
可能：

只需要 4 秒
三、为什么 AI 调用特别适合并发？
因为：

AI API 调用属于：
I/O 密集型任务
什么意思？

真正耗时的是：

等待网络
等待服务器
等待模型生成
而不是：

CPU 计算
举例
你电脑其实一直在：

“等”
而不是：

“疯狂算”
所以：

等待期间：

电脑完全可以：

再去发别的请求
这就是并发的意义。

四、batch() 的本质是什么？
你代码：

responses = model.batch(questions)
其实内部大概是：

并发启动5个 invoke()
类似：

同时:
    invoke(q1)
    invoke(q2)
    invoke(q3)
LangChain 内部本质
实际上：

线程池
或
asyncio
做并发。

五、注意：batch ≠ 模型真正的批量推理
这个非常重要。

你代码里已经提到了：

LangChain 的 batch：
通常不是：

“模型一次处理多个输入”
而是：

“客户端同时发多个 HTTP 请求”
举例
不是：

一次请求：
[
 q1,
 q2,
 q3
]
而是：

同时发：

请求1
请求2
请求3
六、真正的 Batch API 是什么？
有些模型厂商支持：

真·批量推理
比如：

[
  {"prompt":"你好"},
  {"prompt":"Python是什么"}
]
模型内部：

GPU 一次处理多个输入
效率更高。

但 LangChain 的 batch：

默认不是这个。

七、batch_as_completed() 是什么？
这是工程里超级常见的模式。

普通 batch()
会：

等全部完成
再一起返回
batch_as_completed()
是：

谁先完成
谁先返回
举例
假设：

问题	耗时
Python	2 秒
Rust	8 秒
Go	3 秒
普通 batch：

等 8 秒
一起返回
batch_as_completed：

2秒 -> Python 返回
3秒 -> Go 返回
8秒 -> Rust 返回
为什么重要？
因为：

很多 AI 系统：

不需要等全部完成。
比如：

搜索系统
多个 Agent：

Agent1 搜网页

Agent2 查数据库

Agent3 查向量库

谁先回来：

先展示。

八、future 是什么？
这里：

for future in model.batch_as_completed(questions):
future 本质：

是：

“未来会完成的任务”
返回：

(index, response)
因为：

完成顺序：

不一定和输入顺序一致。

所以：

必须带 index。

九、为什么需要 max_concurrency？
这是：

AI 工程里最重要的控制之一。
因为：

你不能无限并发。

十、无限并发的问题
假设：

你：

同时发 1000 个请求
可能：

1. API 限流
例如：

OpenAI：

429 Too Many Requests
2. 本地资源爆炸
比如：

内存爆

socket 耗尽

CPU 飙升

3. 服务端封禁
很多平台：

检测异常流量
直接封号
十一、max_concurrency 的本质
max_concurrency=2
意思：

同时最多只允许 2 个任务运行
运行流程
开始：

Task1 执行
Task2 执行
Task3 等待
Task4 等待
Task1 完成：

Task3 开始
所以：

像：

“工位数量限制”
十二、为什么这是“协程池”思想
本质类似：

线程池
连接池
数据库池
核心：

限制资源使用
十三、abatch() 是什么？
这里：

await model.abatch()
是：

async batch
异步版本。

普通 batch()
内部可能：

线程池
abatch()
使用：

asyncio
异步协程。

十四、asyncio 是什么？
这是 Python 的：

单线程并发模型
核心思想：

遇到 IO 等待
先去做别的事
所以：

特别适合：

AI API 调用
因为：

AI 调用几乎全是 IO 等待。

十五、为什么 async 比线程更适合 AI 调用？
线程：

创建成本高
切换成本高
asyncio：

协程很轻量
可以：

同时跑几千请求
所以：

现代 AI 框架：

几乎都大量使用：

asyncio

async/await

十六、RunnableConfig 是什么？
这是：

LangChain 的运行时配置对象
类似：

requests.get(timeout=30)
但：

RunnableConfig：

控制的是：

整个 Runnable 的运行行为
十七、几个关键配置
1. max_concurrency
并发数。

2. timeout
超时控制。

比如：

30 秒还没返回
直接取消
为什么必须有 timeout？
否则：

某个请求卡死。

整个程序：

永远不结束
3. metadata
元数据。

用于：

日志

tracing

LangSmith

调试

十八、为什么本地模型不适合高并发？
这是很多人最容易误解的。

API 调用：
是：

远程服务器算
你本地只等待
适合高并发。

本地模型：
是：

你自己 GPU 真正在算
这属于：

CPU/GPU 密集型任务
这时候：

高并发反而：

资源竞争
会更慢。

十九、一个非常重要的工程认知
你现在必须理解：

并发 ≠ 并行
并发（Concurrency）
看起来同时执行
核心：

任务切换
并行（Parallelism）
真正同时执行
需要：

多核 CPU

多 GPU

asyncio 更多是：
并发
不是并行。

二十、整个案例的真实底层流程
model.batch()
内部：

创建任务列表
↓
放入线程池/协程池
↓
并发发 HTTP 请求
↓
等待返回
↓
收集结果
↓
返回 responses
batch_as_completed()
内部：

谁先结束
先 yield 谁
max_concurrency
内部：

类似：

Semaphore(2)
信号量控制。

二十一、你现在最应该记住的一句话
整个 batch 的本质：

“用并发同时调用多个 invoke()”
不是：

模型真正一次推理多个输入
二十二、最后给你一个真正 AI 工程中的典型场景
比如：

你有：

10 万篇文档
要：

批量生成摘要
你绝对不可能：

for doc in docs:
    invoke(doc)
因为：

会跑几天
而是：

abatch(
    docs,
    max_concurrency=50
)
这样：

几十倍加速
这才是真正的 AI 工程。


同步和异步解释一下

这个问题其实是：

Python 并发编程最核心的概念
很多人学 LangChain、FastAPI、Agent 时，

真正卡住的不是 AI。

而是：

同步 / 异步 / 并发
你只要真正理解：

“等待”到底发生了什么
就全通了。

一、先一句话理解
概念	人话
同步（Sync）	一件事做完再做下一件
异步（Async）	等待时先去做别的事
二、最经典例子：烧水
同步
你：

烧水
然后：

站在水壶旁边干等
直到：

水开
才能：

洗菜
这就是：

同步阻塞
异步
你：

烧水
然后：

利用等待时间去洗菜
水开后：

再回来。

这就是：

异步非阻塞
三、程序里的“等待”是什么？
程序最耗时的：

通常不是计算。

而是：

IO 等待
比如：

请求 AI API

数据库查询

网络请求

文件读取

例如：

response = requests.get(url)
真正耗时：

是：

等待服务器响应
CPU 大部分时间：

其实闲着。

四、同步代码长什么样？
同步（Sequential）
task1()
task2()
task3()
意思：

task1 做完
↓
task2 才开始
↓
task3 才开始
图示
时间轴：

Task1: ███████
Task2:        ███████
Task3:               ███████
总耗时：

全部加起来
五、异步代码长什么样？
async / await
async def task():
    await api_call()
这里：

await
非常关键。

意思：

“先暂停我”
“去执行别的任务”
六、await 到底是什么？
这是异步的灵魂。

await ≠ 等待
很多人误解。

实际上：

await
真正意思：

是：

“我现在卡 IO 了”
“CPU 别浪费”
“先去运行别的协程”
七、同步 vs 异步（最直观例子）
同步版本
import time

def task(name):
    print(f"{name} 开始")
    time.sleep(3)
    print(f"{name} 结束")

task("A")
task("B")
执行：

A开始
等待3秒
A结束

B开始
等待3秒
B结束
总耗时：

6秒
八、异步版本
import asyncio

async def task(name):
    print(f"{name} 开始")
    await asyncio.sleep(3)
    print(f"{name} 结束")

async def main():
    await asyncio.gather(
        task("A"),
        task("B")
    )

asyncio.run(main())
执行：

A开始
B开始

等待3秒

A结束
B结束
总耗时：

3秒
为什么变快？
因为：

同步：
A 睡觉时
CPU 干等
异步：
A 睡觉时
CPU 去执行 B
九、最重要的认知
异步：

不是让代码“更快”
而是：

“减少等待浪费”
十、同步和异步的本质区别
同步
必须等
异步
等待期间干别的
十一、为什么 AI 调用特别适合异步？
因为 AI API：

99% 时间都在：

等待网络
等待模型返回
所以：

特别适合：

asyncio
十二、同步阻塞是什么意思？
阻塞（Blocking）
意思：

卡住当前线程
例如：

time.sleep(5)
这5秒：

CPU 什么也不干。

非阻塞（Non-blocking）
例如：

await asyncio.sleep(5)
这5秒：

CPU：

可以去执行别的协程
十三、同步函数 vs 异步函数
同步函数
def func():
普通调用：

func()
异步函数
async def func():
调用不会立即执行。

返回：

coroutine object
必须：

await func()
或者：

asyncio.run()
十四、协程是什么？
异步函数运行后：

得到：

协程（Coroutine）
你可以理解成：

“可暂停的函数”
同步函数：

只能一口气跑完
协程：

运行到 await
可以暂停
十五、asyncio 是什么？
Python 的：

异步调度器
负责：

哪个协程运行
哪个暂停
哪个恢复
类似：

“任务调度中心”
十六、gather() 是什么？
这里：

asyncio.gather(
    task1(),
    task2()
)
意思：

同时运行多个协程
十七、同步适合什么？
CPU 密集型
例如：

图像处理

数学计算

模型训练

因为：

不是在等待
而是真在计算
十八、异步适合什么？
IO 密集型
例如：

AI API

数据库

HTTP 请求

文件系统

十九、线程 vs 异步
这是很多人混淆的。

线程
真正：

多个执行流
OS 调度。

asyncio
本质：

单线程任务切换
所以：

asyncio：

轻量
线程：

重
二十、AI 工程里的真实应用
同步
response = model.invoke(q)
一次一个。

异步
await model.abatch(questions)
同时发几十个请求。

二十一、为什么 FastAPI 全是 async？
因为 Web 服务：

大量时间：

都在等数据库
等 API
等网络
async 可以：

一个线程服务几千请求
二十二、最后一句话彻底理解
同步世界
做一件
等结束
再做下一件
异步世界
遇到等待
先做别的
回来继续
二十三、你现在应该真正记住的底层逻辑
整个 async/await 的核心：

“不要浪费等待时间”
AI 工程本质上：
大量都是：

IO等待
所以：

asyncio + 并发
几乎成了现代 AI 工程标配。

"""