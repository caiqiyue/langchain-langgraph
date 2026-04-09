## <center>第一阶段、 Agent核心概念与技术架构

&emsp;&emsp;Agent智能体是一种以大语言模型（LLM）为"大脑"，能够自主感知环境、进行推理规划，并调用外部工具执行复杂任务的系统。它不仅仅是简单的程序，而是具备一系列高级特征的复杂系统。根据LangChain框架的定义，Agent的核心是以大语言模型（LLM）作为其推理引擎，并依据LLM的推理结果来决定如何与外部工具进行交互以及采取何种具体行动。这种架构将LLM的强大语言理解与生成能力，与外部工具的实际执行能力相结合，从而突破了单一LLM的知识限制和功能边界。Agent的本质可以被理解为一种高级的提示工程（Prompt Engineering）应用范式，开发者通过精心设计的提示词模板，引导LLM模仿人类的思考与执行方式，使其能够自主地分解任务、选择工具、调用工具并整合结果，最终完成复杂的任务。

&emsp;&emsp;Agent（智能体）已超越传统AI模型，成为能够自主完成多步骤复杂任务的智能数字助手。其核心特征在于自主性增强、执行能力和持续学习。

<div align=center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251125212642459.png" width=80%></div>

### 1. 能力维度对比

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

| **对比维度** | **传统AI模型** | **Agent智能体** |
| :---: | :---: | :---: |
| **交互能力** | 被动响应用户输入 | 主动感知环境变化 |
| **决策模式** | 基于概率预测 | 基于目标导向的主动规划 |
| **执行能力** | 仅生成文本/内容 | 能够调用工具、访问外部系统 |
| **学习方式** | 静态知识更新 | 动态记忆积累和经验反思 |
| **任务处理** | 单次对话完成 | 支持多步骤、复杂任务序列 |
| **自主程度** | 高度依赖人类指导 | 具备一定程度的自主决策能力 |
