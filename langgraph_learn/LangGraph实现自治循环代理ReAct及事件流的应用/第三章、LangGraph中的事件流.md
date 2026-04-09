# 3. LangGraph中的事件流

&emsp;&emsp;大模型的流式输出功能我们在《Ch.6 OpenAI Assistant API 高阶应用 - 流式输出功能》中首次提到。这一功能与非流式输出不同，后者在 `Agent` 内部处理完成后一次性输出结果。**流式输出的作用在于，它能实时捕捉并输出任务处理过程中的状态变化。这意味着，任何中间过程中的新状态和值都可以被即时获取到。**所以，流式输出功能本质上不直接参与`Agent`的执行过程，仅仅是用来追踪、记录`Agent`在处理不同任务时产生的各个事件、状态和值。

&emsp;&emsp;在实际应用中，流式输出尤其适用于需要快速反馈的业务场景，如聊天机器人，因为**大语言模型可能需要几秒钟才能生成对查询的完整响应，这远远慢于应用程序对最终用户的响应速度约为 200-300 毫秒的阈值**，如果是涉及多个大模型调用的复杂应用程序，这种延时会变得更加明显。让应用程序感觉响应更快的关键策略是显示中间进度；即，通过 `token` 流式传输大模型`Token`的输出，以此来显著提升用户体验。而在开发阶段，利用流式输出功能可以准确追踪到事件的具体执行阶段，并捕获相关数据，从而接入不同逻辑的数据处理和决策流程。是我们在应用开发中必须理解和掌握的技术点。

&emsp;&emsp;流式输出功能在`LangGraph` 框架中的实现方式，相较于`Assistant API`是简单很多的，但基本思路一样。因为`LangGraph`底层是基于 `LangChain` 构建的，所有就直接把`LangChain`中的回调系统拿过来使用了。**在`LangChain`中的流式输出是：以块的形式传输最终输出，即一旦监测到有可用的块，就直接生成它。**最常见和最关键的流数据是大模型本身生成的输出。 大模型通常需要时间才能生成完整的响应，通过实时流式传输输出，用户可以在生成时看到部分结果，这可以提供即时反馈并有助于减少用户的等待时间。如下所示：

```python
import getpass
import os
from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


llm = ChatOpenAI(model="gpt-4o")```

```python
chunks = []
async for chunk in llm.astream("你好，请你详细的介绍一下你自己。"):
    chunks.append(chunk)
    print(chunk.content, end="|", flush=True)```

```python
chunks[0]```

&emsp;&emsp;每一个块，都是一个`AIMessageChunk`对象，用来代表`AIMessage`对象的一部分。消息块在设计上是可加的，比如：

```python
chunks[0] + chunks[1] + chunks[2] + chunks[3] + chunks[4]```

&emsp;&emsp;而进一步的，除了流式传输大模型的输出之外，通过更复杂的工作流程或管道流式传输进度也很有用，比如 `AI Agent` 中的中间处理过程，这就涉及到工作流概念。
