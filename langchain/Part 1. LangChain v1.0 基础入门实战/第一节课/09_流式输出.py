# -*- coding: utf-8 -*-
"""
【案例 9】流式输出 Streaming
==========================================

本案例展示 LangChain 的流式输出功能
实现打字机效果，提升用户体验

要点：
1. stream() 方法的使用
2. 流式输出的原理（SSE）
3. 消息块累积
"""

import os
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
print("案例 9: 流式输出 Streaming")
print("=" * 50)

from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(model="qwen3-max", temperature=0.7)

# ============================================================
# 1. 基础流式调用
# ============================================================
print("\n1. 基础流式调用")
print("-" * 30)

print("AI: ", end="", flush=True)
full_response = ""

for chunk in model.stream("给我讲一个关于猫的笑话"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
        full_response += chunk.content

print("\n")  # 换行

# ============================================================
# 2. 消息块累积
# ============================================================
print("2. 消息块累积")
print("-" * 30)

print("AI: ", end="", flush=True)
accumulated = None

for chunk in model.stream("解释一下什么是量子计算"):
    # AIMessageChunk 可以通过 + 拼接
    accumulated = chunk if accumulated is None else accumulated + chunk
    print(chunk.content if chunk.content else "", end="", flush=True)

print("\n\n累积消息信息:")
print(f"  类型: {type(accumulated)}")
print(f"  内容长度: {len(accumulated.content)} 字符")
print(f"  内容块数量: {len(accumulated.content_blocks)}")

# ============================================================
# 【补充】SSE 原理
# ============================================================
print("\n" + "=" * 50)
print("Server-Sent Events (SSE) 原理")
print("=" * 50)
print("""
【问题】
HTTP 协议是请求-响应模型，一次请求只能一次响应。
但流式需要服务端分批发数据，客户端逐步显示。

【SSE 解决方案】

1. HTTP 响应头设置：
   Content-Type: text/event-stream
   Cache-Control: no-cache
   Connection: keep-alive

2. 服务端分次发送数据：
   data: {"token": "你"}\n\n
   data: {"token": "好"}\n\n
   data: {"token": "啊"}\n\n
   data: [DONE]\n\n

3. 客户端通过 EventSource 接收：
   const source = new EventSource('/stream');
   source.onmessage = (event) => {
       console.log(event.data);
   };

【LangChain 的处理】
- LangChain 封装了 SSE 协议
- stream() 返回一个生成器
- 每个 chunk 是 AIMessageChunk 对象
- chunk.content 是本次返回的文本片段
""")


"""
一、先理解：普通调用 vs 流式调用
普通调用（invoke）

你之前一直用：

response = model.invoke("你好")

这时候：

AI 会：

思考 -> 生成完整答案 -> 一次性返回

所以你会等几秒。

最后突然：

你好！有什么可以帮助你的？

一次性全部出来。

流式调用（stream）

而：

model.stream(...)

是：

生成一点
返回一点

再生成一点
再返回一点

像 ChatGPT 网页版一样：

你
好
呀
～

一点点蹦出来。

二、为什么需要流式输出？

因为：

用户体验差别非常大
不流式

用户：

点发送
等待 10 秒
突然全部出来

会觉得：

是不是卡了？
流式

用户：

点发送
立刻开始输出

即使总耗时一样：

用户也会觉得：

AI 很快
三、stream() 到底返回什么？

这是核心。

你看到：
for chunk in model.stream("给我讲一个关于猫的笑话"):

说明：

model.stream()

返回的是：

生成器（generator）

即：

yield
yield
yield

不断返回数据。

类似：
def test():
    yield "你"
    yield "好"
    yield "呀"

然后：

for x in test():
    print(x)

输出：

你
好
呀
四、chunk 到底是什么？

这是最关键的。

AI 不是一次返回完整句子

而是：

第1块：你好
第2块：，我
第3块：是AI
第4块：助手

每一小块：

就是：

chunk
LangChain 中：

chunk 类型是：

AIMessageChunk

你可以理解成：

“AI 返回的一小段消息”
五、chunk.content 是什么？

就是：

本次新增的文本

例如：

第一次循环：

chunk.content = "你好"

第二次：

chunk.content = "，我是"

第三次：

chunk.content = "AI助手"

所以：

print(chunk.content, end="")

才能实现：

你好，我是AI助手

逐步打印。

六、为什么 full_response += chunk.content

因为：

每次只拿到一小段。

你得自己拼接。

举例

第一次：

full_response = "你好"

第二次：

full_response = "你好，我是"

第三次：

full_response = "你好，我是AI助手"

所以：

full_response += chunk.content

本质是：

手动累计完整回答

七、AIMessageChunk 为什么能 + 拼接？

这里：

accumulated = chunk if accumulated is None else accumulated + chunk

这是 LangChain 很巧妙的设计。

它允许：

AIMessageChunk + AIMessageChunk

自动合并。

比如：

第一次
chunk1.content = "你好"
第二次
chunk2.content = "呀"

拼接：

chunk1 + chunk2

得到：

"你好呀"

所以：

accumulated.content

最后就是：

完整回答。

八、content_blocks 是什么？

这个是新版 LangChain 的结构化内容。

因为 AI 返回的：

不一定只是文字。

未来可能：

文字
图片
工具调用
代码
音频

所以内部会拆成：

content_blocks

类似：

[
    {"type": "text", "text": "..."},
    {"type": "image", ...}
]

现在你先理解成：

content_blocks
=
内部消息块列表

即可。

九、最难的：SSE 到底是什么？

这是整个流式输出的底层。

先理解 HTTP 的问题

普通 HTTP：

客户端请求
↓
服务器一次性返回
↓
连接结束

不能：

返回一点
再返回一点
但 AI 流式需要：
先返回“你”
再返回“好”
再返回“呀”

怎么办？

SSE 方案

Server-Sent Events

意思：

“服务器持续推送消息”

本质就是：

HTTP 不断保持连接。

不关闭。

服务端持续发送：
data: 你

data: 好

data: 呀

data: [DONE]
浏览器实时接收

所以：

页面就能：

你
你好
你好呀

实时显示。

十、你可以把 SSE 理解成：

普通 HTTP：

发快递
一次送完

SSE：

开着电话
边说边听
十一、LangChain 帮你做了什么？

你不用自己解析 SSE。

LangChain 已经：

帮你：
建立 SSE 连接
接收 token
解析数据
封装 chunk
返回生成器

所以你只需要：

for chunk in model.stream():

即可。

十二、整个流程（超级重要）

这是你必须真正理解的。

真实运行流程
1. 你调用
model.stream(prompt)
2. LangChain 发 HTTP 请求

请求：

stream=true

告诉大模型：

我要流式
3. 大模型开启 SSE

持续发送：

data: token1
data: token2
data: token3
4. LangChain 接收

每收到一个：

转换成：

AIMessageChunk
5. stream() yield 返回

于是：

for chunk in ...

开始不断循环。

6. 你打印
print(chunk.content)

于是实现：

打字机效果
十三、最后一句话总结整个案例

你可以直接记：

知识点	本质
stream()	流式生成器
chunk	AI 返回的一小段内容
chunk.content	当前新增文本
accumulated + chunk	拼接完整消息
SSE	服务器持续推送数据
流式输出	边生成边显示
十四、你现在最应该真正记住的一句话

整个流式输出：

本质就是：

大模型不断生成 token
↓
SSE 不断推送 token
↓
LangChain 不断封装 chunk
↓
Python for 循环不断接收
↓
print 实时打印

这就是完整原理。

"""