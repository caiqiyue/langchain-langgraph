# <center>第二阶段、 与 LangChain 及 LangGraph 的区别

&emsp;&emsp;从技术定位看，LangChain 适用于需要自定义提示与工具的基础智能体搭建；LangGraph 更适合构建复杂的多智能体系统与工作流；而 DeepAgents 面向希望省去底层开发、直接采用深度自主机制的用户，可快速实现 AutoGPT 类应用。因此，DeepAgents 本质上是基于 LangChain 的深度模式封装——它并非替代 LangChain 或 LangGraph，而是将其常用抽象与运行时封装为开箱即用的组件，可视为一层“开发加速器”。

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

| 特性 | LangChain | LangGraph | DeepAgents |
| :---: | :---: | :---: | :---: |
| **层级** | 基础组件库 (Foundation) | 编排引擎 (Orchestration) | **应用框架 (Application Framework)** |
| **核心抽象** | Chain, Runnable, Tool | StateGraph, Node, Edge | **DeepAgent, Middleware, Backend** |
| **灵活性** | 极高 (积木块) | 高 (自定义图结构) | **中 (Opinionated / 约定优于配置)** |
| **开箱即用** | 低 (需自行组装) | 中 (需定义图逻辑) | **高 (内置规划、文件系统、子代理)** |
| **适用对象** | 库开发者/底层构建 | 复杂流程序列化开发者 | **应用开发者/企业级解决方案** |

<div align=center><img src="https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202512021438587.png" width=70%></div>


- **LangChain**：提供 Prompt, Models, Tools 等积木。

- **LangGraph**：提供 State, Nodes, Edges 等地基和连接逻辑。

- **DeepAgents**：**LangGraph 的一种“最佳实践实现”**。它底层使用 LangGraph 来管理状态和循环，但向上提供了更高级的 API (`create_deep_agent`)，隐藏了底层的图构建细节。
