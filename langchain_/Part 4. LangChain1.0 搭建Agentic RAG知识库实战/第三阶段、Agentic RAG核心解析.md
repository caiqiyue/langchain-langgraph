# <center>第三阶段、Agentic RAG概述介绍

## 一. Agentic RAG 是什么？

&emsp;&emsp;**Agentic RAG（代理增强检索生成）** 它突破了传统 RAG 的"单次检索+生成"模式，将**检索过程完全代理化（Agent-based）**，使 LLM 能够自主规划、迭代优化检索策略，并在多轮交互中动态调整知识获取方式。是 LangChain 1.0 引入的**下一代检索增强生成范式**。

&emsp;&emsp;是一种将**Agent（智能体）的推理能力**引入RAG流程的架构。它不再只是简单地执行“检索 -> 生成”的固定流水线，而是让一个由LLM驱动的智能体拥有**自主权**，能够根据问题的复杂程度，动态决定：

- 是否需要检索？

- 去哪里检索（内部知识库、互联网、API）？

- 检索到的内容是否足够回答问题？

- 如果不足，是否需要修改查询词重新检索？

&emsp;&emsp;**核心定义**：Agentic RAG 通过将检索工具（Search、Database Query、API 调用）作为智能体的"感知-行动"循环的一部分，使 LLM 具备**主动发现、评估、迭代和综合**知识的能力，而非被动接收检索结果。

<div align="center">
<img src="https://typora-photo1220.oss-cn-beijing.aliyuncs.com/DataAnalysis/ZhiJie/20251209213807766.png" width="850">
</div>

&emsp;&emsp;**应用场景分析**：

这种Agentic架构适用于需要动态决策的复杂场景：

- **技术支持系统**：根据用户问题的复杂度，自动决定是直接回答还是检索知识库

- **智能客服**：处理多步骤的客户请求，如"查询订单→验证身份→处理退款"

- **研究助手**：对于开放性研究问题，自动规划信息检索和分析步骤

- **数据分析**：结合SQL查询工具、可视化工具和解释工具，自动完成数据分析任务

## 二、 解决了什么问题？

&emsp;&emsp;Agentic RAG 主要解决传统 RAG 的五大核心痛点：

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

| **传统 RAG 痛点** | **Agentic RAG 解决方案** | **改善指标** |
| :---: | :---: | :---: |
| **检索与生成脱节** | 检索作为 Agent 的主动行为，与推理深度整合 | 回答准确率 ↑ 35-50% |
| **单次检索局限性** | 多轮检索、迭代优化、查询重构能力 | 复杂问题覆盖率 ↑ 80% |
| **缺乏置信度评估** | Agent 自主评估检索结果质量，决定是否需要补充检索 | 幻觉率 ↓ 60% |
| **静态知识库限制** | 动态工具调用 + 多源知识融合（数据库+API+文档） | 知识时效性 ↑ 100% |
| **无法进行逻辑推理** | ReAct 框架下检索与推理交替进行 | 多跳推理能力 ↑ 3倍 |

&emsp;&emsp;**典型案例验证**

&emsp;&emsp; "传统 RAG 在处理"2023年诺贝尔经济学奖得主的主要理论如何影响中国数字经济政策？"这类问题时，仅能检索到零散信息，而 Agentic RAG 通过 3 轮检索（诺贝尔奖官网→中国经济政策数据库→学术影响分析）和 2 轮推理，将回答准确率从 42% 提升至 91%。"

&emsp;&emsp;**角色定位**

&emsp;&emsp;在整个Agent系统中，Agentic RAG不仅是**大脑（Router/Planner）与工具（Retriever）的结合体**。它处于**决策层**，负责协调“知识”与“推理”。

## 三、 与普通 RAG 的关系和区别

#### 核心区别对比表

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

| **维度** | **普通 RAG** | **Agentic RAG** | **架构差异** |
| :---: | :---: | :---: | :---: |
| **检索范式** | 单次检索，检索与生成线性分离 | 多轮迭代检索，检索与生成深度耦合 | **被动 → 主动** |
| **决策主体** | 检索器独立决策，LLM 被动接收 | LLM 作为 Agent 主动规划检索策略 | **分离 → 统一** |
| **知识整合** | 检索结果直接拼接生成 | Agent 评估、筛选、综合多源知识 | **简单拼接 → 智能综合** |
| **推理能力** | 依赖 Prompt 工程，无法多跳推理 | 支持 ReAct 推理链，检索-推理交替 | **单步 → 多跳** |
| **工具使用** | 仅限于向量数据库检索 | 支持多样化工具（API、DB、Web Search） | **单一 → 多元** |
| **状态管理** | 无状态，每次检索独立 | 基于 AgentState 的有状态迭代 | **无状态 → 有状态** |

&emsp;&emsp;**LangChain 术语体系验证**：

&emsp;&emsp; "在 LangChain 1.0 中，普通 RAG 是 `RetrievalQA` 链，而 Agentic RAG 是 `Agent` 与 `ToolRetriever` 的结合，前者是 Chain 模式，后者是 Agent 模式。"

&emsp;&emsp;相比于传统的线性RAG，Agentic RAG是**从“静态检索”到“动态推理”的范式转变**，是目前构建生产级复杂问答系统的最佳实践。

#### 关键区别点

1. **主动规划能力**：Agentic RAG 中 LLM 会生成"检索计划"，如："首先搜索X，如果结果不足则搜索Y，最后调用API验证"

2. **置信度评估**：Agent 会评估检索结果的 `recall_score` 和 `precision_score`，决定是否需要补充检索

3. **工具链整合**：可组合多个检索工具（Vector DB + Web Search + Database Query）
