# <center>第三阶段、检索Retrieval逻辑封装

## 一、 Tool与Middleware的区别

&emsp;&emsp;在 LangChain 1.0 的 Agent 体系中，「Tool」与「Middleware」虽然都可扩展 Agent 的能力，但它们适用的场景完全不同，当我们需要对一些业务逻辑进行扩展和封装时，那么就需要判断是封装在Tool工具里还是封装在Middleware中间件里。判断标准核心在于：
是否需要让 LLM 通过决策（reasoning → act）来显式调用这段逻辑？

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

|    维度    | **Tool（工具）** | **Middleware（中间件）** |
|:--------:| :---: | :---: |
| **作用对象** | 封装**具体业务功能**（RAG检索、API调用） | 封装**执行流程控制**（日志、重试、限流） |
| **调用方式** | 由**LLM自主决策**调用（通过function calling） | 在Agent执行**固定节点自动触发**（before/after模型调用） |
| **设计目的** | 扩展Agent的**能力边界** | 增强Agent的**可靠性、安全性、可观测性** |
| **状态访问** | 接收参数，返回结果 | 可直接读写**AgentState**，控制执行流（如jump_to="end"） |
| **执行概率** | 0% ~ 100% (不确定) | 100% (确定) |

请在设计功能判断封装场景时，问自己以下三个问题：
1. 谁来决定“做不做”？(Who decides?)
* 需要 LLM 根据上下文判断是否执行
→
 Tool
    * 例子：搜索互联网、查询天气、计算器。因为用户可能只是打招呼，不需要搜索。
* 业务流程规定必须执行
→
 Middleware / Node
    * 例子：权限校验、敏感词过滤、日志记录、固定的知识库召回（如客服系统）。
2. 参数从哪里来？(Where do args come from?)
* 参数需要从用户的自然语言中提取
→
 Tool
    * 例子：用户说“帮我查下特斯拉的股价”，Tool 需要提取“特斯拉”作为参数。
* 参数是系统上下文或环境变量
→
 Middleware / Node
    * 例子：用户的 UserID、当前的 SessionID、数据库连接配置。这些不需要 LLM 去“猜”。
3. 失败了怎么办？(Error Handling)
* 失败了需要 LLM 换个方式重试
→
 Tool
    * 例子：搜索不到结果，LLM 可以尝试换个关键词再次调用 Tool。
* 失败了直接抛异常或走系统降级
→
 Middleware / Node
    * 例子：数据库连接断开、API 鉴权失败。

&emsp;&emsp;所以在Agentic RAG中，我们需要将检索逻辑封装在Tool工具里，而不是封装在Middleware中间件里。这样做的原因是，检索逻辑是一种需要显式调用的业务逻辑，而不是一种需要在每个请求中都执行的中间件逻辑。而Middleware中间件更多地关注于在请求处理过程中的一些通用操作，如日志记录、性能监控等。

## 二、 将RAG封装为Tool

&emsp;&emsp;将RAG检索功能封装为Tool是构建Agentic RAG系统的关键步骤。这个过程的本质是将原本独立的RAG链转换为Agent可以理解和调用的标准化工具。下面我们详细分析这个过程的逻辑和实现细节。

**封装逻辑说明**：

1. **功能抽象**：将复杂的RAG检索逻辑抽象为一个简单的函数接口`rag_search(query: str) -> str`。这个函数接收用户查询作为输入，返回检索结果作为输出，屏蔽了内部文档加载、向量检索、答案生成等复杂细节。

2. **标准化描述**：通过Tool的`description`参数提供详细的功能说明。这个描述至关重要，因为它直接决定了LLM是否能正确理解Tool的用途并在合适的场景下调用它。一个好的Tool描述应该包含：

  - Tool的核心功能

  - 适用的查询类型

  - 返回结果的格式

  - 使用限制和注意事项

3. **命名规范**：Tool的`name`应该具有明确的业务含义，使用小写字母和下划线，便于LLM理解和调用。例如`internal_knowledge_base`比`rag_tool_1`更具描述性。

### 1. 定义网络搜索工具

```python
#!pip install langchain-tavily```

```python
from langchain_tavily import TavilySearch

# 定义网络搜索工具tool，默认name为tavily_search
web_search = TavilySearch(max_results=2)

web_search.invoke("介绍一下LangChain这个框架")```

### 2. 定义基础数据知识库工具

```python
from pydantic import BaseModel, Field
# 定义工具输入参数
from langchain_core.tools import StructuredTool

# 定义工具输入参数
class QAWithRetrievalArgs(BaseModel):
    query: str = Field(description="用户的问题")

def query_retrieval_knowledge(query: str) -> str:
    """
    一个基于LangChain知识库检索的问答工具。
    专门用于回答与 LangChain 相关的技术问题。

    ⚠️ 重要：此工具仅适用于 LangChain 相关问题！
    如果问题与 LangChain 无关，请使用网络搜索工具。
    """
    # 定义 LangChain 相关关键词
    langchain_keywords = [
        'langchain', 'langgraph', 'langsmith', 'lcel',
        'chain', 'agent', 'retriever', 'embedding', 'vector',
        'rag', 'prompt', 'llm', 'chatmodel', 'runnable',
        '链', '代理', '检索器', '向量', '提示词', '模型'
    ]

    # 检查查询是否包含 LangChain 相关关键词
    query_lower = query.lower()
    is_langchain_related = any(keyword in query_lower for keyword in langchain_keywords)

    # 如果查询与 LangChain 无关，返回提示
    if not is_langchain_related:
        return (
            "❌ 检测到此问题与 LangChain 知识库无关。\n"
            "建议：请使用网络搜索工具 (tavily_search_results_json) 来查找答案。\n"
            f"原始问题：{query}"
        )

    # 如果相关，则进行检索，返回检索文档内容
    retrieval_chain = ensemble_retriever | format_docs
    docs = retrieval_chain.invoke(query)

    # 检查检索结果质量
    if not docs or len(docs.strip()) < 50:
        return (
            f"⚠️ 知识库中未找到关于 '{query}' 的充分信息。\n"
            "建议：可以尝试使用网络搜索工具获取更多信息。"
        )

    return docs

# 定义工具StructuredTool
qa_tool = StructuredTool.from_function(
    func=query_retrieval_knowledge,        # 工具函数
    name="query_retrieval_knowledge",      # 工具名称
    description=(
        "🎯 专用于回答 LangChain 技术相关问题的知识库检索工具。\n"
        "适用范围：LangChain、LangGraph、LangSmith、LCEL、Agent、RAG、Retriever、Embedding、Prompt 等相关技术。\n"
        "⚠️ 限制：仅包含 LangChain 相关文档，不适用于其他领域问题（如烹饪、历史、科学等）。\n"
        "如果问题与 LangChain 无关，请使用网络搜索工具 tavily_search_results_json。"
    ),                                      # 工具描述
    args_schema=QAWithRetrievalArgs,        # 工具输入参数
    return_direct=False                     # 是否直接返回工具输出，而不是作为消息内容
)

result = qa_tool.invoke("LangChain这个框架是什么？")
print(result)```

### 3. 定义敏感数据知识库工具


```python
# 定义高风险知识库敏感数据查询工具
class SensitiveKnowledgeQueryArgs(BaseModel):
    query: str = Field(description="查询的敏感主题或关键词")
    data_category: str = Field(
        description="数据类别：confidential(机密), internal(内部), sensitive(敏感)",
        default="confidential"
    )

def query_sensitive_knowledge(query: str, data_category: str = "confidential") -> str:
    """
    ⚠️ 高风险操作：基于 RAG 的敏感知识库检索

    使用向量检索 + BM25 混合检索敏感文档。
    包含机密文档、内部资料、敏感信息等。

    风险等级：🔴 高风险
    - 访问机密文档和敏感信息
    - 可能涉及商业机密、个人隐私
    - 需要权限验证和人工审核批准
    """
    print(f"\n🔴 [高风险操作] 敏感知识库 RAG 检索")
    print(f"   数据类别: {data_category}")
    print(f"   查询内容: {query}")

    # 1.定义敏感数据类别标签
    sensitive_categories = {
        "confidential": "🔴 机密级",
        "internal": "🟡 内部级",
        "sensitive": "🟠 敏感级"
    }

    # 2.获取类别标签
    category_label = sensitive_categories.get(data_category, "未知级别")

    # 3.使用敏感数据混合检索器进行 RAG 检索
    print(f"   正在检索敏感知识库...")
    retrieval_chain = sensitive_ensemble_retriever | format_docs
    docs = retrieval_chain.invoke(query)

    # 检查检索结果质量
    if not docs or len(docs.strip()) < 50:
        return (
            f"⚠️ 敏感知识库中未找到关于 '{query}' 的相关信息。\n"
            f"数据类别：{category_label}\n"
            f"提示：请确认查询关键词是否准确，或尝试使用不同的关键词。\n"
            f"可查询的类别：机密(confidential)、内部(internal)、敏感(sensitive)"
        )

    # 根据数据类别过滤结果（可选：基于文档内容中的密级标记）
    # 这里简单处理，返回所有检索结果

    # 格式化输出
    output = f"{category_label} 检索结果\n"
    output += "="*70 + "\n\n"
    output += "📋 检索到的敏感信息：\n\n"
    output += docs
    output += "\n\n" + "="*70
    output += f"\n\n⚠️ 安全警告：\n"
    output += f"- 以上为{category_label}信息，请妥善保管，不得外泄！\n"
    output += f"- 访问已记录，将用于安全审计\n"
    output += f"- 如需分享，请确保接收方具有相应权限\n"
    output += f"- 查询时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return output

# 定义工具StructuredTool.from_function
sensitive_knowledge_tool = StructuredTool.from_function(
    func=query_sensitive_knowledge,         # 工具函数
    name="query_sensitive_knowledge",       # 工具名称
    description=(
        "🔴 高风险操作：敏感知识库查询工具\n"
        "用于查询知识库中的机密文档、内部资料、敏感信息等受限数据。\n"
        "⚠️ 警告：此操作需要人工审核批准！\n"
        "适用场景：\n"
        "- 查询财务数据、战略规划等机密信息\n"
        "- 访问技术文档、人事信息等内部资料\n"
        "- 获取用户数据、客户信息等敏感数据\n"
        "安全提示：仅在必要时使用，确保有相应权限。"
    ),                                      # 工具描述
    args_schema=SensitiveKnowledgeQueryArgs,        # 工具输入参数
    return_direct=False                     # 是否直接返回工具输出，而不是作为消息内容
)

result = sensitive_knowledge_tool.invoke("查询一下2024年Q4财务报告数据")
print(result)```

```python
# 定义工具列表，将工具添加到列表中
tools = [qa_tool, web_search, sensitive_knowledge_tool]```

### 4. Agent执行工具

```python
from typing import TypedDict
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 创建并运行 Agent
class Context(TypedDict):
    user_role: str

# 创建线程ID
config = {"configurable": {"thread_id": "test-thread-final"}}

# 创建Agent
agent = create_agent(
    tools=tools,                  # 工具列表
    model=model,                  # 模型
    debug=False,                  # 是否开启调试模式，开启后会打印详细信息
    checkpointer=InMemorySaver(),  # 检查点保存器，用于保存和恢复Agent状态
    context_schema=Context       # 上下文模式，定义了Agent在运行时的上下文信息
)

# 执行Agent，使用流式输出模式
for event in agent.stream(
        {"messages": [{"role": "user", "content": "LangChain支持哪些模型？"}]},
        config=config,
        stream_mode="values",
        context={"user_role": "大模型工程师"}
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]
            if last_msg.type == "ai":
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    tool_call = last_msg.tool_calls[0]
                    print(f"🤖 [AI 决策]: 调用工具 -> {tool_call['name']}")
                    print(f"   参数: {tool_call.get('args', {})}")
                elif last_msg.content:
                    print(f"\n💬 [AI 回复]:\n{last_msg.content}")```

### 5. 询问复杂问题，需要多个工具协作完成

```python
# 执行Agent，使用流式输出模式
for event in agent.stream(
        {"messages": [{"role": "user", "content": "比较RAG和Agentic RAG的区别，并推荐使用场景"}]},
        config=config,
        stream_mode="values",
        context={"user_role": "大模型工程师"}
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]
            if last_msg.type == "ai":
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    tool_call = last_msg.tool_calls[0]
                    print(f"🤖 [AI 决策]: 调用工具 -> {tool_call['name']}")
                    print(f"   参数: {tool_call.get('args', {})}")
                elif last_msg.content:
                    print(f"\n💬 [AI 回复]:\n{last_msg.content}")```

当Agent执行时，我们可以观察到以下效果：

1. **智能路由**：对于"LangChain支持哪些模型？"这类知识性问题，Agent会自动选择`query_retrieval_knowledge`工具

2. **多工具协作**：对于复杂问题如"比较RAG和Agentic RAG的区别，并推荐使用场景"，Agent可能会：

  - 首先调用知识库工具获取技术细节

  - 然后基于检索到的信息进行分析和推理，是否符合预期，是否需要调用其他工具

  - 所有检索到的信息都符合预期，最后给出综合性的回答和建议

3. **错误处理**：如果Tool调用失败（如知识库中无相关内容），Agent会根据错误信息调整策略，可能尝试重新表述查询或告知用户限制


