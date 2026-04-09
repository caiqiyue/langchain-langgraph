# <center>第二阶段、LangChain **模块化管理**的定位与描述</center>

&emsp;&emsp;LangChain 把“核心抽象”与“具体实现/第三方集成/历史实现”拆分成多个包，以实现更清晰的 API 边界、减小核心包体积、并把社区贡献与厂商集成模块化管理。主要目标是：**核心更稳定、可维护；集成可按需安装。**

## 2.1 LangChain 1.0 核心依赖包及作用

<style>
/* 强制表格居中、自动换行并适应单元格宽度 */
.rendered_html table, .jp-RenderedHTMLCommon table {
    margin-left: auto !important;
    margin-right: auto !important;
    width: auto !important; /* 允许表格根据内容收缩 */
    max-width: 100%; /* 防止表格溢出单元格 */
    table-layout: fixed; /* 固定布局算法，对长文本换行至关重要 */
}
.rendered_html th, .jp-RenderedHTMLCommon th,
.rendered_html td, .jp-RenderedHTMLCommon td {
    white-space: normal !important; /* 允许自动换行 */
    word-wrap: break-word; /* 对长单词或URL进行强制换行 */
    text-align: left; /* 默认内容左对齐 */
}
.rendered_html th, .jp-RenderedHTMLCommon th {
    text-align: center !important; /* 表头文本居中 */
}
</style>

| **依赖包名称** | **核心作用** | **详细功能介绍** |
| :---: | :---: | :---: |
| **langchain-core** | **核心抽象层和 LCEL** | 定义所有组件（如模型、消息、提示词模板、工具、运行环境）的标准接口和基本抽象。它包含了 **LangChain 表达式语言 (LCEL)**，这是构建链式应用的基础。这是一个**轻量级**、**不含第三方集成**的基石包。  |
| **langchain** | **应用认知架构（主包）** | 包含构建 LLM 应用的**通用高阶逻辑**，如 Agents (如新的 create_agent() 函数)、Chains 和通用的检索策略 (Retrieval Strategies)。它建立在 langchain-core 之上，是用于组合核心组件的“胶水”层。  |
| **langchain-community** | **社区第三方集成** | 包含由 LangChain 社区维护的**非核心或不太流行的**第三方集成，例如：大部分的文档加载器 (Document Loaders)、向量存储 (Vector Stores)、不太流行的 LLM/Chat Model 集成等。为了保持包的轻量，所有依赖项都是可选的。 |
| **langchain-openai** / **langchain-[厂商名称]** | **特定厂商深度集成** | 针对 **关键合作伙伴** 的集成包（如 langchain-openai, langchain-anthropic）。它们被单独分离出来，以提供**更好的支持、可靠性**和**更轻量级的依赖**。它们只依赖于 langchain-core。  |
| **langchain-classic** | **旧版本兼容** | 包含 LangChain v0.x 版本中的**已弃用 (deprecated) 或旧版功能**，如旧的 LLMChain、旧版 Retrievers、Indexing API 和 Hub 模块。它的主要作用是为用户提供一个**平稳的迁移期**，确保旧代码在升级到 v1.0 后仍能运行。 |

### 1. langchain-core

- 包含 **核心抽象与接口**：LLM/ChatModel 抽象、Prompt 抽象、Chain/Agent 的基类、schema、消息格式等。

- **不包含**具体厂商的实现（例如没有 OpenAI client 的封装），而是定义“合同（interfaces）”，其他包在此之上实现具体功能。

- 这是构建 LangChain 应用生态的最小公共底座。

```python
# 安装：pip install langchain
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    "为生产{product}的公司起一个好名字？"
)

formatted_prompt = prompt_template.format(product="智能水杯")

response = model.invoke(formatted_prompt)
```

### 2. langchain 主包

- **对外的主入口包**：把 `langchain-core` 的核心抽象与“常用实现”组合在一起，便于快速上手。

- 在 v1.0 中，`langchain` 的命名空间被 **显著精简**，只保留构建 agent 的关键 API（更轻、更专注）。官方建议大多数用户直接使用此主包以获得“开箱即用”的体验。

<style>
/* 强制表格居中、自动换行并适应单元格宽度 */
.rendered_html table, .jp-RenderedHTMLCommon table {
    margin-left: auto !important;
    margin-right: auto !important;
    width: auto !important; /* 允许表格根据内容收缩 */
    max-width: 100%; /* 防止表格溢出单元格 */
    table-layout: fixed; /* 固定布局算法，对长文本换行至关重要 */
}
.rendered_html th, .jp-RenderedHTMLCommon th,
.rendered_html td, .jp-RenderedHTMLCommon td {
    white-space: normal !important; /* 允许自动换行 */
    word-wrap: break-word; /* 对长单词或URL进行强制换行 */
    text-align: left; /* 默认内容左对齐 */
}
.rendered_html th, .jp-RenderedHTMLCommon th {
    text-align: center !important; /* 表头文本居中 */
}
</style>

| 模块 | 核心内容 | 来源说明 |
| :---: | :---: | :---: |
| `langchain.agents` | `create_agent`, `AgentState` | 智能体创建核心 |
| `langchain.messages` | `AIMessage`, `HumanMessage`, `trim_messages` | 从langchain-core重新导出 |
| `langchain.tools` | `@tool`, `BaseTool` | 从langchain-core重新导出 |
| `langchain.chat_models` | `init_chat_model`, `BaseChatModel` | 统一模型初始化 |
| `langchain.embeddings` | `init_embeddings` | 嵌入模型管理 |

```python
from langchain.agents import create_agent

# 创建智能体
agent_executor = create_agent(llm, tools)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "会议决定：张三需要在下周一前完成项目报告"
    }]
})
```

### 3. langchain-community 第三方集成库

&emsp;&emsp;langchain-community 作为 LangChain 1.0 的“功能扩展层”，通过社区贡献的非官方集成组件显著扩展了主包的功能边界，其核心价值体现在工具类组件与平台集成两大维度。工具类组件覆盖文档处理全流程，包括 **DirectoryLoader** 文档加载器（支持 PDF、文本等多格式文件批量导入）、**RecursiveCharacterTextSplitter** 文本分割器（按语义边界将文档切分为检索友好的 Chunk）、**PGVector** 向量存储（PostgreSQL 生态的向量数据库适配）及 **HuggingFaceEmbeddings** 嵌入模型（本地部署模型的向量化能力），这些组件共同构成了 RAG 应用的技术基础。平台集成方面，支持与 DeepSeek、阿里云通义千问等模型的对接，例如通过 langchain_community.chat_models.ChatTongyi 类初始化通义千问模型，或利用 Ollama 类调用本地部署的 DeepSeek-R1 模型。

- 收集并维护 **社区/第三方贡献的集成**（例如某些云厂商、开源向量库、特殊工具适配器等）。这些集成**实现了 **`langchain-core`** 定义的接口**，但不属于主包维护范畴。官方会把这些放到 `langchain-community` 仓库/包，便于社区共同维护。

&emsp;&emsp;**包含内容**：

   - **数据库**：MySQL, PostgreSQL, MongoDB, Neo4j等连接器

   - **存储服务**：AWS S3, 阿里云OSS, Google Cloud Storage

   - **工具集成**：Slack, Notion, GitHub, ArXiv, YouTube等API

   - **向量数据库**：Chroma, Pinecone, Qdrant, Milvus等

   - **文档加载器**：PDF, CSV, HTML, Markdown解析器

&emsp;&emsp;**特点**：

- **质量参差不齐**：社区贡献，需自行验证稳定性

- **更新滞后**：依赖社区维护，响应速度慢于官方包

- **功能丰富**：覆盖95%的第三方服务集成需求

```python
# 安装：pip install langchain-community
from langchain_community.document_loaders import NotionDBLoader

# 从Notion数据库加载文档
loader = NotionDBLoader(
    integration_token="secret_...",
    database_id="your-db-id"
)

documents = loader.load()

print(f"加载了{len(documents)}条文档")

```

###  4. langchain-openai（厂商/提供者集成包）

&emsp;&emsp;厂商特定集成包（如 langchain-openai、langchain-anthropic、langchain-google 等）通过封装 API 细节，为开发者提供“零适配成本”的模型对接方案，其核心价值在于简化特定 API 对接流程，使开发者能够直接使用厂商特有功能。以 langchain-openai 为例，其关键组件包括模型客户端、工具调用适配和多模型支持三大模块。

&emsp;&emsp;此外，该类还支持通过配置 openai_api_base 和 openai_api_key 参数对接兼容 OpenAI API 格式的第三方模型，如 DeepSeek 模型

- **专门负责把 OpenAI 的 SDK 与 LangChain 抽象连接起来**：提供 `ChatOpenAI`、`OpenAIEmbeddings`、`OpenAI`等类的实现。

- 这类包通常是 “按厂商拆分”：`langchain-openai`、`langchain-azure`、`langchain-anthropic`、`langchain-deepseek`等。

- **官方深度集成**特定LLM提供商，更新频繁，功能最全.

```python
#!pip install langchain-openai
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

question = "你好，请你介绍一下你自己。"

result = model.invoke(question)
print(result.content)
```

&emsp;&emsp;**主流厂商包列表**：

- `langchain-openai`：OpenAI, Azure OpenAI

- `langchain-anthropic`：Claude系列

- `langchain-google`：Gemini, Vertex AI

- `langchain-deepseek`：DeepSeek模型

- `langchain-ollama`：本地Ollama部署

&emsp;&emsp;**与**`langchain-community`**的区别**：

<style>
/* 强制表格居中、自动换行并适应单元格宽度 */
.rendered_html table, .jp-RenderedHTMLCommon table {
    margin-left: auto !important;
    margin-right: auto !important;
    width: auto !important; /* 允许表格根据内容收缩 */
    max-width: 100%; /* 防止表格溢出单元格 */
    table-layout: fixed; /* 固定布局算法，对长文本换行至关重要 */
}
.rendered_html th, .jp-RenderedHTMLCommon th,
.rendered_html td, .jp-RenderedHTMLCommon td {
    white-space: normal !important; /* 允许自动换行 */
    word-wrap: break-word; /* 对长单词或URL进行强制换行 */
    text-align: left; /* 默认内容左对齐 */
}
.rendered_html th, .jp-RenderedHTMLCommon th {
    text-align: center !important; /* 表头文本居中 */
}
</style>

| **维度** |   `langchain-openai`   | `langchain-community`<br/>**中的OpenAI** |
| :---: |:----------------------:|:--------------------------------------:|
| 维护方 | OpenAI官方 + LangChain团队 |                  社区维护                  |
| 更新频率 |       即时跟进API更新        |                  延迟数周                  |
| 功能完整性 |    支持所有新特性（如音频、视觉）     |                 仅基础功能                  |
| 生产可用性 |         ✅ 强烈推荐         |                ⚠️ 谨慎使用                 |

&emsp;&emsp;为什么要单独拆出来？

- 让 `langchain` 主包保持轻量（不强制安装所有厂商 SDK）；

- 用户按需安装对应厂商，例如你只用 OpenAI，就只装 `langchain-openai`。

&emsp;&emsp;**最佳实践**：

- **生产环境务必使用厂商包**：享受最新功能

- **开发环境可用community**：快速验证想法

- **多厂商切换用**`init_chat_model`：业务代码无需改动

### 5. langchain-classic

- **兼容包 / 迁移包**：把 LangChain v0.x 中的“老 API / legacy 功能”搬到单独包里，以便 v1.0 保持精简，但仍给用户向后兼容的迁移通道。

- 包含如：老的 Chain 实现、旧版 retrievers、索引 API、hub 模块等被标记为“legacy”的功能。

  - 旧版`AgentExecutor`

  - Legacy Chains（`LLMChain`, `SequentialChain`等）

```python
#!pip intsall langchain-classic
from langchain_classic.chat_models import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
res = model.invoke("请介绍一下你自己")
```
