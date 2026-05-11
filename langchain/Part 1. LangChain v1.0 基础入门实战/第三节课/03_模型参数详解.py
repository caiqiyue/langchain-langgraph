# -*- coding: utf-8 -*-
"""
【案例 3】模型参数详解
==========================================

本案例深入讲解模型的关键参数

要点：
1. temperature 温度参数
2. max_tokens 最大生成数
3. 重试机制
4. 速率限制
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
print("案例 3: 模型参数详解")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi

# ============================================================
# 1. temperature 温度参数
# ============================================================
print("\n1. temperature 温度参数")
print("-" * 30)

print("""
temperature 控制输出的随机性：

- temperature = 0.0：几乎确定输出，适合翻译、代码等需要精确的场景
- temperature = 0.3~0.7：平衡模式，适合一般对话
- temperature = 0.7~1.0：创意模式，适合写作、头脑风暴
- temperature > 1.0：不推荐，过度随机

数学原理：
- LLM 输出是概率分布 P(token)
- temperature 重新加权：P'(token) ∝ P(token)^(1/temperature)
- temperature → 0 时，趋向于 one-hot（最高概率）
- temperature → ∞ 时，趋向于均匀分布
""")

# 不同 temperature 的效果
model = ChatTongyi(model="qwen3-max", temperature=0.0)
response = model.invoke("给我一个 1-10 之间的随机数")
print(f"temperature=0.0: {response.content}")

model = ChatTongyi(model="qwen3-max", temperature=1.0)
response = model.invoke("给我一个 1-10 之间的随机数")
print(f"temperature=1.0: {response.content}")

# ============================================================
# 2. max_tokens 最大生成数
# ============================================================
print("\n2. max_tokens 最大生成数")
print("-" * 30)

print("""
max_tokens 控制单次回复的最大长度：

- 设置太小：回复可能被截断
- 设置太大：浪费 token，增加成本
- 实际是"最大"限制，不是精确控制

注意：LLM 是按 token 计费的
估算规则（英文）：
- 1 token ≈ 4 个字符
- 1 token ≈ 0.75 个单词
""")

model = ChatTongyi(model="qwen3-max", max_tokens=10)
response = model.invoke("写一篇 500 字的文章")
print(f"max_tokens=10 的回复: {response.content}")

model = ChatTongyi(model="qwen3-max", max_tokens=500)
response = model.invoke("写一篇 500 字的文章")
print(f"max_tokens=500 的回复长度: {len(response.content)} 字符")

# ============================================================
# 3. 重试机制
# ============================================================
print("\n3. 重试机制")
print("-" * 30)

print("""
.with_retry() 为模型调用添加重试策略：

参数：
- stop_after_attempt: 最多重试次数
- wait_exponential_jitter: 指数退避 + 随机抖动

指数退避：1s → 2s → 4s → 8s
抖动：避免多个客户端同时重试
""")

model = ChatTongyi(model="qwen3-max", temperature=0.7)
model_with_retry = model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

print("重试机制配置完成")
print(f"原始模型: {type(model)}")
print(f"带重试的模型: {type(model_with_retry)}")

# ============================================================
# 【补充】top_p（核采样）
# ============================================================
print("\n" + "=" * 50)
print("补充：top_p（核采样）")
print("=" * 50)
print("""
top_p 是 temperature 的替代方案：

- 按概率降序排列 tokens
- 从高到低累加概率
- 只保留累加概率达到 top_p 的 tokens
- 通常 top_p = 0.9

注意：通常只调 temperature 或 top_p，不同时调
""")


"""
一、先理解：LLM 到底怎么“选词”

假设模型现在要生成下一个 token。

模型内部会得到：

“今天天气真”

后面每个 token 的概率：

token	概率
好	0.40
不错	0.25
差	0.15
热	0.08
冷	0.05
香蕉	0.0001

模型下一步就是：

从这些 token 里抽一个
二、temperature 做了什么

temperature：

改变概率分布

比如：

temperature = 0

直接：

选概率最高的

即：

好

永远最稳定。

temperature = 1

保持原始概率。

正常随机。

temperature = 2

会把：

高概率压低
低概率抬高

于是：

香蕉

这种离谱词概率也变高。

所以会：

更发散
更随机
更疯
三、top_p 到底是什么

top_p 不改概率。

它：

先删词

比如：

原始概率：

token	概率
好	0.40
不错	0.25
差	0.15
热	0.08
冷	0.05
香蕉	0.0001

现在：

top_p = 0.8

模型会：

按概率从高到低累加
第一步
好 = 0.40

累计：

0.40

还没到 0.8。

继续。

第二步
不错 = 0.25

累计：

0.65

继续。

第三步
差 = 0.15

累计：

0.80

达到 top_p。

停止。

于是：

最终只保留：
token
好
不错
差

后面的：

热
冷
香蕉

全部删掉。

然后：

只在剩下的 token 中随机采样
四、你会发现：

temperature：

改概率

top_p：

改候选集合
五、为什么叫“核采样”

因为：

top_p 本质是：

保留“核心概率区域”

英文：

Nucleus Sampling

即：

核采样

只保留：

最可能的一小撮 token
六、top_p 为什么非常重要

因为：

temperature 有个问题：

会把垃圾 token 也升温

例如：

token	原概率
香蕉	0.000001

如果：

temperature = 2

它概率会上升。

模型可能开始胡说八道。

而 top_p：

直接：

把低概率垃圾词裁掉

所以：

很多时候：

top_p

比：

temperature

更稳定。

七、现代模型为什么更喜欢 top_p

因为：

top_p：

创造力更稳定
不容易崩
不容易幻觉
不容易离谱

因此：

很多生产环境：

temperature = 0.7
top_p = 0.9

或者：

temperature = 1
top_p = 0.95
八、为什么“不要同时调 temperature 和 top_p”

因为：

它们都在：

控制随机性

同时调：

会互相干扰。

例如：

temperature = 2
top_p = 0.2

一个：

拼命放飞

另一个：

拼命裁剪

会很奇怪。

所以工程实践：

通常：

只重点调一个
常见方案
稳定场景（代码/翻译）
temperature = 0
普通聊天
temperature = 0.7
创意写作
top_p = 0.95

或者：

temperature = 1
九、你可以这样记忆
temperature

像：

“加热大脑”

让模型更敢乱想。

top_p

像：

“限制可选答案范围”

只允许模型在：

最靠谱的一批词

里随机。

十、一个特别重要的理解（真正底层）

现代 LLM 推理：

本质是：

不断地：
预测下一个 token 的概率分布

然后：

采样

而：

temperature
top_p
top_k

全部都是：

Sampling Strategy（采样策略）

它们决定：

模型“怎么从概率分布里抽词”。

十一、再给你一个最直观例子

假设模型写小说。

temperature 高

会：

她走进房间。

→ 月光像融化的银。
→ 空气里漂浮着烧焦的记忆。

更有创造力。

top_p 低

会：

她走进房间。

→ 看见桌子。
→ 坐下。
→ 开灯。

因为：

模型只能从：

高概率安全词

里选。

十二、最后一句总结（非常重要）
temperature

控制：

“概率分布有多平”
top_p

控制：

“允许参与抽奖的 token 有多少”

这是理解采样机制的核心。
"""