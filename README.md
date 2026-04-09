# LangChain & LangGraph AI Agent 开发实战

本项目基于 LangChain 1.0 / LangGraph 框架，系统讲解 AI Agent 的核心概念、技术栈与项目实战。

## 环境要求

- **Python**: `>=3.10, <3.13`
- **Node.js**: `>=18` (用于 LangGraph CLI 工具)
- **推荐操作系统**: macOS / Linux / Windows WSL2

## 创建环境（使用 uv）

```bash
# 1. 创建虚拟环境
uv venv .venv --python 3.12

# 2. 激活环境
source .venv/bin/activate      # macOS / Linux
# 或
.venv\Scripts\activate         # Windows

# 3. 安装依赖
uv pip install -r requirements.txt
```

## 依赖说明

| 类别 | 库 | 说明 |
|------|-----|------|
| 核心框架 | `langchain>=0.3`, `langgraph>=0.2` | LangChain 1.0 与 LangGraph |
| LLM 调用 | `langchain-openai`, `langchain-ollama`, `langchain-deepseek` | 主流模型集成 |
| Agent 框架 | `deepagents` | LangChain 官方深度 Agent 框架 |
| 工具集成 | `langchain-tavily`, `langchain-mcp-adapters` | 搜索、MCP 工具 |
| 向量库 | `langchain-chroma`, `langchain-milvus`, `faiss-cpu` | RAG 向量存储 |
| 数据库 | `sqlalchemy`, `psycopg-pool` | 数据库连接与连接池 |
| 检查点 | `langgraph-checkpoint-sqlite`, `langgraph-checkpoint-postgres` | LangGraph 状态持久化 |
| 中间件 UI | `gradio`, `rich` | 可视化界面与美化输出 |
| 网络爬虫 | `requests`, `httpx`, `bs4`, `scrapy`, `playwright` | 网页抓取与自动化 |
| 工具库 | `pydantic`, `python-dotenv`, `faker`, `tiktoken` | 数据验证与环境配置 |

## 项目结构

```
langchain_learning/
├── langchain_/          # LangChain Part 1-6 实战
│   ├── Part 1. LangChain v1.0 基础入门实战/
│   ├── Part 2. LangChain v1.0 搭建Agent智能体应用实战/
│   ├── Part 3. LangChain1.0 Agent智能体中间件应用实战/
│   ├── Part 4. LangChain1.0 搭建Agentic RAG知识库实战/
│   ├── Part 5. DeepAgents 框架介绍与应用实践/
│   └── Part 6. DeepAgents 实现网络爬虫自动化案例/
│
├── langgraph_learn/     # LangGraph Part 1-8 实战
│   ├── LangGraph底层原理解析与基础应用入门/
│   ├── LangGraph中State状态模式与LangSmith基础使用入门/
│   ├── 单代理架构在LangGraph中构建复杂图的应用/
│   ├── LangGraph实现自治循环代理ReAct及事件流的应用/
│   ├── LangGraph长短期记忆实现机制及检查点的使用/
│   ├── LangGraph中Human-in-the-loop应用实战/
│   ├── LangGraphMulti-AgentSystems开发实战/
│   └── LangGraphSupervisor多代理架构与GraphRAG综合应用实战/
│
├── requirements.txt     # Python 依赖列表
└── README.md
```

## 环境变量配置

部分功能需要配置 API 密钥，创建 `.env` 文件：

```bash
# LLM API Keys
OPENAI_API_KEY=your-openai-api-key

# LangSmith (可选，用于 Agent 追踪)
LANGSMITH_API_KEY=your-langsmith-api-key

# Tavily Search (可选)
TAVILY_API_KEY=your-tavily-api-key

# Neo4j (可选，GraphRAG 使用)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Milvus (可选，向量数据库)
MILVUS_URI=https://xxx.zillizcloud.com
MILVUS_TOKEN=your-token
```
