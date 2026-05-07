# <center>第四阶段、构建Agentic RAG系统

## 一、 Agentic RAG系统

&emsp;&emsp;LangChain 1.0引入了强大的中间件系统，允许在Agent执行的关键节点插入自定义逻辑。在创建Agentic RAG系统是将Tool与LLM智能体结合的核心环节。这个过程涉及提示词工程、Agent创建和执行器中间件配置三个关键步骤，每个步骤都对最终系统的表现有重要影响。在实现Agentic RAG系统时，需要注意以下几个方面：

* 提示词工程：精心设计的提示词能够引导LLM生成符合预期的输出。在Agentic RAG系统中，提示词应包含必要的上下文信息，以便LLM能够理解用户意图并生成相关内容。

* Agent创建：使用LangChain 1.0的Agent类创建智能体。在创建时，需要指定LLM模型、工具列表和中间件配置。

* 执行器中间件配置：在执行器中配置中间件，以便在Agent执行过程中插入自定义逻辑。例如，在RAG系统中，中间件可以用于检索相关文档、生成上下文信息等。

## 二、 定义中间件

&emsp;&emsp;本次实验将实现一个基于LangChain 1.0的Agentic RAG系统，该系统能够根据用户输入的问题，从知识库中检索相关信息，并使用LLM生成符合预期的回答。一共加入了以下几个组件：

* 知识库：用于存储和检索相关信息的文档集合。

* LLM模型：用于生成文本回答的语言模型。

* 智能体（Agent）：负责接收用户输入、调用工具（如检索知识库）、执行LLM生成回答的组件。

* 中间件（Middleware）：在智能体执行过程中插入自定义逻辑的组件，用于处理输入、输出、错误等情况。

    * before_model(SummarizationMiddleware上下文压缩)：在LLM模型调用之前执行的中间件，用于压缩上下文信息，减少输入 tokens 数量。

    * wrap_tool_model(ToolRetryMiddleware工具自动重试)：在调用工具（如知识库检索）时执行的中间件，用于自动重试工具调用，直到成功或达到最大重试次数。
    
    * after_model（ToolLoggingMiddleware 日志记录）：在LLM模型调用之后执行的中间件，用于记录模型输出和调用信息，方便调试和分析。

    * after_model（ToolCallLimitMiddleware 工具调用次数限制）：在LLM模型调用之后执行的中间件，用于限制工具调用次数，防止无限循环调用。

    * after_model（HumanInTheLoopMiddleware 人工干预）：在LLM模型调用之后执行的中间件，用于人工干预模型输出，如检查回答是否符合预期、修正错误等。


### 1. 上下文压缩中间件（before_model）

* 核心作用：在上下文信息中压缩和提取关键信息，减少输入 tokens 数量，提高模型生成效率。

```python
from langchain.agents.middleware import SummarizationMiddleware

# 定义摘要中间件
summarization_middleware = SummarizationMiddleware(
    model=ChatDeepSeek(model="deepseek-chat", temperature=0.1),    # 摘要模型
    max_tokens_before_summary=500,      # 触发摘要的最大 tokens 数量
    messages_to_keep=3,                 # 保留的对话历史消息数量
    summary_prompt="请将以下对话历史进行摘要，保留关键决策点和技术细节：\n\n{messages}\n\n摘要:"  # 摘要提示
)```

### 2. 自动工具重试中间件（wrap_tool_call）

* 核心作用：当调用工具失败或者出错时，可以自动重试调用，直到达到最大重试次数或者成功为止。

```python
from langchain.agents.middleware import ToolRetryMiddleware

# 定义重试中间件
retry_middleware = ToolRetryMiddleware(
    max_retries=3,    # 最大重试次数
    tools=["query_retrieval_knowledge", "tavily_search_results_json","query_sensitive_knowledge"],  # 要重试的工具列表
    retry_on=(ConnectionError, RuntimeError),              # 要重试的异常类型
    on_failure="return_message",                           # 失败时的处理方式，这里是返回失败信息
    backoff_factor=1.5                                     # 重试间隔因子，每次重试间隔会增加这个因子倍
)```

### 3. Tool 调用日志中间件（after_model）

* 核心作用：对Tool工具调用时收集调用信息，如调用次数、调用参数、调用结果等日志信息。

```python
"""
Tool 调用日志中间件

功能：
1. 记录所有工具调用的详细信息
2. 性能统计和分析
3. JSON 文件持久化
4. 异常检测和告警
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse,   AgentState

class ToolCallLogger:
    """工具调用日志记录器"""

    def __init__(self, log_dir: str = "LangChain_AgenticRAG/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_logs: List[Dict[str, Any]] = []
        self.session_start_time = datetime.now()
        self.tool_call_times: Dict[str, float] = {}  # 记录工具调用开始时间

        # Token 使用统计
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.cache_hit_tokens = 0

    def get_log_file_path(self) -> Path:
        """获取当前日志文件路径"""
        date_str = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"tool_calls_{date_str}.json"

    def log_tool_call(
        self,
        tool_name: str,
        tool_input: Any,
        tool_output: Any,
        success: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        token_usage: int = 0,
    ):
        """记录单次工具调用"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": str(tool_input)[:500],  # 限制长度
            "output": str(tool_output)[:1000] if success else None,
            "success": success,
            "error": error,
            "metadata": metadata or {},
            "token_usage": token_usage,
        }

        self.current_session_logs.append(log_entry)

        # 实时写入文件
        self._append_to_file(log_entry)

        # 打印日志
        status = "✅" if success else "❌"
        if not success and error:
            print(f"   Error: {error}")

    def accumulate_tokens(
        self,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        cache_hit: int = 0
    ):
        """累计 token 使用量"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens += total_tokens
        self.cache_hit_tokens += cache_hit

        print(f"📊 [Token Usage] 输入: {input_tokens}, 输出: {output_tokens}, 总计: {total_tokens}")
        if cache_hit > 0:
            print(f"   缓存命中: {cache_hit} tokens")

    def _append_to_file(self, log_entry: Dict[str, Any]):
        """追加日志到文件"""
        log_file = self.get_log_file_path()

        # 读取现有日志
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # 添加新日志
        logs.append(log_entry)

        # 写回文件
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.current_session_logs:
            return {"message": "No logs yet"}

        total_calls = len(self.current_session_logs)
        successful_calls = sum(1 for log in self.current_session_logs if log["success"])
        failed_calls = total_calls - successful_calls

        # 统计工具使用次数
        tool_counts = {}
        for log in self.current_session_logs:
            tool_name = log["tool_name"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": f"{(successful_calls/total_calls*100):.1f}%" if total_calls > 0 else "0%",
            "tool_usage": tool_counts,
            "token_usage": {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_tokens,
                "cache_hit_tokens": self.cache_hit_tokens
            },
            "session_duration": str(datetime.now() - self.session_start_time)
        }

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        print("\n" + "="*70)
        print("📊 Tool Call Statistics")
        print("="*70)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("="*70)


class ToolLoggingMiddleware(AgentMiddleware):
    """
    创建工具日志中间件
    使用 @wrap_model_call 装饰器从 ModelRequest 获取消息历史
    """
    def __init__(self, log_dir: str = "LangChain_AgenticRAG/logs"):
        super().__init__()
        self.logger = ToolCallLogger()


    def after_model(self,state: AgentState, runtime) -> None:
        """
        从 ModelRequest 中获取消息历史，记录工具调用信息

        Args:
            request: ModelRequest 包含 state (包括 messages)
            handler: 处理函数，执行实际的模型调用

        Returns:
            ModelResponse 模型响应
        """
        # 从 state 获取消息历史
        messages = state.get("messages", [])

        # print(f"🔍 [Tool Logging] 分析消息历史，{messages} 消息")

        # 检查消息历史中的工具调用和结果
        for msg in messages:
            # 检测 AI 消息并提取 token 使用信息
            if hasattr(msg, 'type') and msg.type == 'ai':
                # 优先从 usage_metadata 获取
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    input_tokens = msg.usage_metadata.get('input_tokens', 0)
                    output_tokens = msg.usage_metadata.get('output_tokens', 0)
                    total_tokens = msg.usage_metadata.get('total_tokens', 0)

                    # 获取缓存命中信息
                    cache_hit = 0
                    if 'input_token_details' in msg.usage_metadata:
                        cache_hit = msg.usage_metadata['input_token_details'].get('cache_read', 0)

                    # 累计 token
                    self.logger.accumulate_tokens(input_tokens, output_tokens, total_tokens, cache_hit)

                # 备选：从 response_metadata 获取
                elif hasattr(msg, 'response_metadata') and msg.response_metadata:
                    token_usage = msg.response_metadata.get('token_usage', {})
                    if token_usage:
                        input_tokens = token_usage.get('prompt_tokens', 0)
                        output_tokens = token_usage.get('completion_tokens', 0)
                        total_tokens = token_usage.get('total_tokens', 0)
                        cache_hit = token_usage.get('prompt_cache_hit_tokens', 0)

                        # 累计 token
                        self.logger.accumulate_tokens(input_tokens, output_tokens, total_tokens, cache_hit)

            # 检测 AI 消息中的工具调用请求
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    # tool_call 可能是字典或对象，需要兼容两种方式
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id', 'unknown_id')
                    else:
                        tool_name = getattr(tool_call, 'name', 'unknown')
                        tool_args = getattr(tool_call, 'args', {})
                        tool_id = getattr(tool_call, 'id', 'unknown_id')

                    # 记录工具调用开始时间
                    if tool_id not in self.logger.tool_call_times:
                        self.logger.tool_call_times[tool_id] = time.time()
                        print(f"\n🔧 [Tool Logging] 检测到工具调用: {tool_name}")
                        print(f"   工具ID: {tool_id}")
                        print(f"   参数: {str(tool_args)[:200]}...")

            # 检测工具返回消息
            if hasattr(msg, 'type') and msg.type == 'tool':
                tool_name = getattr(msg, 'name', 'unknown')
                tool_content = getattr(msg, 'content', '')
                tool_call_id = getattr(msg, 'tool_call_id', 'unknown_id')
                token_usage = getattr(msg, 'token_usage', 0)

                # 判断是否成功
                success = not tool_content.startswith('❌') and not tool_content.startswith('Error')
                error_msg = tool_content if not success else None

                # 记录日志
                self.logger.log_tool_call(
                    tool_name=tool_name,
                    tool_input="[从消息历史提取]",
                    tool_output=tool_content,
                    success=success,
                    error=error_msg,
                    metadata={
                        "tool_call_id": tool_call_id,
                        "timestamp": datetime.now().isoformat(),
                        "message_type": msg.type
                    },
                    token_usage=token_usage
                )
        # 打印当前统计信息
        self.logger.print_statistics()


# 实例化日志中间件
logging_middleware = ToolLoggingMiddleware(log_dir="./logs")```

### 4. 工具调用限制中间件（after_model）

* 核心作用：对工具调用设置最大次数限制，避免对工具的滥用。

* **注意**：一个ToolCallLimitMiddleware里面的tool_name只能限制一个工具，如果想要限制多个工具的话就需要定义多个中间件来实现！

```python
from langchain.agents.middleware import ToolCallLimitMiddleware

# 限制 query_retrieval_knowledge 工具调用次数
retrieval_limit_middleware = ToolCallLimitMiddleware(
    tool_name="query_retrieval_knowledge",
    run_limit=3,  # 每次运行最多调用 3 次
    exit_behavior="continue"  # 超限后继续执行，但阻止工具调用
)

# 限制 query_sensitive_knowledge 工具调用次数
sensitive_limit_middleware = ToolCallLimitMiddleware(
    tool_name="query_sensitive_knowledge",
    run_limit=3,  # 每次运行最多调用 3 次
    exit_behavior="continue"  # 超限后继续执行，但阻止工具调用
)```

### 5. HITL 人工干预中间件（after_model）

* 核心作用：监控敏感知识库查询时，可以通过人工干预进行审核，确保查询结果的准确性和安全性。

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

# 创建官方 HITL 中间件，监控敏感知识库查询工具
official_hitl_middleware = HumanInTheLoopMiddleware(
    interrupt_on={"query_sensitive_knowledge": True},  # 监控敏感知识库查询工具
    description_prefix="需要人工批准才能查询敏感知识库"    # 提示前缀
)```

### 6. 动态提示词中间件（wrap_model_call）

* 核心作用：能够根据检索次数来动态调整系统提示词，以提高检索效果。

* **注意**：这里使用的装饰器dynamic_prompt，其实是wrap_model_call类型的中间件，包裹在model运行的生命周期里！

* __执行时机__：在模型调用时动态修改 system prompt


```python
from langchain.agents.middleware import dynamic_prompt

@dynamic_prompt
def rag_optimized_prompt(request: ModelRequest) -> str:
    """
    根据检索状态动态生成提示词
    核心逻辑：通过分析消息历史中的工具调用次数，确定当前所处的 RAG 阶段
    """
    messages = request.messages if hasattr(request, 'messages') else []

    # 统计所有工具调用中的知识库查询次数（包括检索和敏感查询）
    retrieval_count = 0
    for msg in messages:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.name if hasattr(tool_call, 'name') else tool_call.get('name')
                # 统计知识库查询次数（包括检索和敏感查询）
                if name == 'query_retrieval_knowledge' or name == 'tavily_search_results_json' or name == 'query_sensitive_knowledge':
                    retrieval_count += 1

    print(f"DEBUG: 当前累计检索次数: {retrieval_count}")

    # 基础提示词
    base_prompt = """你是一个智能知识助手，能够自主检索信息并回答问题。

    🔧 可用工具说明：
    1. query_retrieval_knowledge: 专门用于 LangChain 技术问题（LangChain、LangGraph、Agent、RAG、Retriever 等）
    2. tavily_search_results_json: 用于通用问题的网络搜索（烹饪、历史、科学、新闻等）
    3. query_sensitive_knowledge: 🔴 高风险工具 - 查询敏感知识库（财务数据、战略规划、客户信息等机密资料）

    ⚠️ 工具选择原则：
    - 如果问题涉及 LangChain 相关技术 → 使用 query_retrieval_knowledge
    - 如果问题与 LangChain 无关（如烹饪、历史、科学等） → 直接使用 tavily_search_results_json
    - 如果问题涉及敏感数据查询（财务、战略、客户、人事等） → 使用 query_sensitive_knowledge
    - 不要对非 LangChain 问题调用知识库检索工具

    🔴 高风险工具使用注意事项：
    - query_sensitive_knowledge 需要人工审核批准才能执行
    - 仅在用户明确请求查询机密/敏感信息时使用
    - 调用此工具后，系统会暂停等待管理员批准
    - 适用场景：财务报告、战略规划、客户档案、人事薪资、技术文档等

    请遵循以下流程：
    1. 分析用户问题的类型和复杂度
    2. 判断问题是否与 LangChain 相关，或是否涉及敏感数据
    3. 选择合适的检索工具
    4. 评估检索结果的质量（覆盖率、完整性、相关性）
    5. 如果结果不足，主动进行补充检索
    6. 综合所有信息生成最终回答
    """

    # 初始状态：未进行任何知识库查询
    if retrieval_count == 0:
        return base_prompt + """

        【当前状态：初始阶段】
        ⚠️ 重要：你还没有进行任何检索！

        请先判断问题类型：
        - 如果是 LangChain 相关问题 → 使用 query_retrieval_knowledge
        - 如果是其他领域问题 → 使用 tavily_search_results_json
        - 如果涉及敏感数据查询 → 使用 query_sensitive_knowledge（需人工批准）

        ❌ 禁止在没有检索的情况下直接回答问题。
        """

    # 信息评估阶段：已进行 1-2 次知识库查询
    elif retrieval_count < 3:
        return base_prompt + f"""

        【当前状态：信息评估（已检索 {retrieval_count} 次）】
        请检查上一步工具返回的搜索结果：
        1. 信息是否覆盖了用户问题的全部维度？
        2. 多个来源的信息是否一致？

        👉 决策路径：
        - 如果信息不足或有歧义 -> 请换个关键词或角度进行补充检索。
        - 如果信息已经充分 -> 请根据上下文生成最终回答。
        """

    # 最终回答阶段：已进行 3 次及以上知识库查询
    else:
        return base_prompt + f"""

        【当前状态：最终回答（已检索 {retrieval_count} 次）】
        🛑 已达到最大检索次数限制，请停止检索！

        请必须基于当前已有的所有信息，生成最终的回答。
        如果检索到的信息仍不能完全回答问题，请诚实地说明信息的局限性或缺失部分。
        """```

## 三、 集成中间件到Agent

* **注意**：after_model的注册顺序与最终执行顺序相反，是逆序执行，所以需要注意注册顺序，HITL人工干预中间件能够中断程序的要放在执行的最后，注册顺序为第一位置，下面顺序和截图都做过了修改！

```python
# 中间件列表 (注意顺序)
middlewares = [
        
    # before_model: 准备阶段，上下文压缩中间件
    summarization_middleware,
    
    # wrap_model_call: 模型调用包裹，智能切换系统提示词
    rag_optimized_prompt,
    
    # after_model: 后处理（逆序执行，所以倒着写）
    official_hitl_middleware,        # 最后执行：人工审核（可能中断）
    logging_middleware,              # 倒数第二：记录日志
    sensitive_limit_middleware,      # 倒数第三：限制敏感工具
    retrieval_limit_middleware,      # 最先执行：限制检索工具
    
    # wrap_tool_call: 工具调用包裹
    retry_middleware,
]```

<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v1_简洁现代.html" width=50%></div>

```python
from typing import TypedDict
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 创建并运行 Agent
class Context(TypedDict):
    user_role: str

# 配置线程 ID
config = {"configurable": {"thread_id": "test-thread-final"}}

# 创建 Agent
agent = create_agent(
    tools=tools,
    model=model,
    middleware=middlewares,
    debug=False,                    # 关闭调试模式
    checkpointer=InMemorySaver(),   # 内存检查点，用于存储状态
    context_schema=Context         # 上下文模式，定义了状态的结构
)
```

* 通过`langgraph studio`可视化调试,观察Agent的运行状态和行为

<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v2_深色科技.html" width=80%></div>


### 1. 测试HITL中间件触发

```python
# 导入 Command 用于恢复执行
from langgraph.types import Command
# 导入 HITL 相关类
from langchain.agents.middleware.human_in_the_loop import (
    HITLResponse,
    ApproveDecision,
    EditDecision,
    RejectDecision
)

def run_hitl_interactive_test():
    """
    运行 HITL 人工干预交互式测试
    参考 HITL_demo.py 的完整流程
    """
    print("\n" + "="*70)
    print("🚀 开始执行 Agentic RAG 测试 (HITL 人工干预模式)")
    print("="*70)

    # 测试提示词：触发敏感知识库查询
    user_input = "帮我查询一下2024年Q4财务报告数据的详细内容。"
    print(f"\n[用户]: {user_input}")

    # === 第一步：初始执行 ===
    print("\n[系统]: 开始处理请求...")

    for event in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values",
        context={"user_role": "财务分析师"}
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]
            if last_msg.type == "ai" and hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                print(f"[AI 决策]: 准备调用工具 -> {last_msg.tool_calls[0]['name']}")

    # === 第二步：观察中断状态 ===
    snapshot = agent.get_state(config)

    print(f"\n--- 🛑 执行已暂停 (HITL Middleware 触发) ---")
    print(f"下一步骤: {snapshot.next}")
    print(f"任务数量: {len(snapshot.tasks) if snapshot.tasks else 0}")

    # 检查是否有待处理的任务（表示中断发生）
    if snapshot.tasks:
        last_message = snapshot.values["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]

            print(f"\n{'='*70}")
            print("🔴 检测到高风险操作：敏感知识库查询")
            print(f"{'='*70}")
            print(f"工具名称: {tool_call['name']}")
            print(f"查询内容: {tool_call['args'].get('query', 'N/A')}")
            print(f"数据类别: {tool_call['args'].get('data_category', 'confidential')}")
            print(f"{'='*70}")

            # === 第三步：人工决策 ===
            approval = input("\n[管理员]: 是否批准此操作? (y/n/e[编辑]): ").strip().lower()

            if approval == 'y':
                # === 批准操作 ===
                print("\n[系统]: ✅ 操作已批准，继续执行...")

                hitl_response = HITLResponse(
                    decisions=[ApproveDecision(type="approve")]
                )

                # 第四步：恢复执行
                for event in agent.stream(
                    Command(resume=hitl_response),
                    config=config,
                    stream_mode="values"
                ):
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if last_msg.type == "tool":
                            print(f"\n[工具输出]:\n{last_msg.content}")
                        elif last_msg.type == "ai" and last_msg.content:
                            print(f"\n[AI 最终回复]: {last_msg.content}")

            elif approval == 'e':
                # === 编辑操作 ===
                print("\n[系统]: ✏️  编辑模式...")
                print(f"当前参数: {tool_call['args']}")

                new_query = input(f"新查询内容 (当前: {tool_call['args'].get('query', '')}，留空保持不变): ").strip()
                new_category = input(f"新数据类别 (当前: {tool_call['args'].get('data_category', 'confidential')}，留空保持不变): ").strip()

                updated_args = tool_call['args'].copy()
                if new_query:
                    updated_args['query'] = new_query
                if new_category:
                    updated_args['data_category'] = new_category

                print(f"\n[系统]: 使用更新后的参数继续执行...")
                print(f"更新后的参数: {updated_args}")

                hitl_response = HITLResponse(
                    decisions=[EditDecision(
                        type="edit",
                        edited_action={
                            "name": tool_call['name'],
                            "args": updated_args
                        }
                    )]
                )

                for event in agent.stream(
                    Command(resume=hitl_response),
                    config=config,
                    stream_mode="values"
                ):
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if last_msg.type == "tool":
                            print(f"\n[工具输出]:\n{last_msg.content}")
                        elif last_msg.type == "ai" and last_msg.content:
                            print(f"\n[AI 最终回复]: {last_msg.content}")

            else:
                # === 拒绝操作 ===
                print("\n[系统]: ❌ 操作被拒绝")

                rejection_reason = input("拒绝原因 (可选): ").strip() or "操作被管理员拒绝，权限不足"

                hitl_response = HITLResponse(
                    decisions=[RejectDecision(
                        type="reject",
                        message=rejection_reason
                    )]
                )

                for event in agent.stream(
                    Command(resume=hitl_response),
                    config=config,
                    stream_mode="values"
                ):
                    if "messages" in event:
                        last_msg = event["messages"][-1]
                        if last_msg.type == "ai" and last_msg.content:
                            print(f"\n[AI 回复]: {last_msg.content}")
                        elif last_msg.type == "tool":
                            print(f"\n[工具消息]: {last_msg.content}")

                print("\n[系统]: 流程已终止")
        else:
            print("⚠️  没有检测到待处理的工具调用")
    else:
        print("ℹ️  流程已完成，没有触发中断")
        if snapshot.values.get("messages"):
            last_msg = snapshot.values["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                print(f"\n[最终回复]: {last_msg.content}")

    print("\n" + "="*70)
    print("✅ HITL 测试完成！")
    print("="*70)

    # 打印统计信息
    print("\n📊 中间件统计信息:")
    logging_middleware.logger.print_statistics()```

```python
run_hitl_interactive_test()```

* 在LangSmith页面中观察运行流程：
<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v1_简洁现代.html" width=80%></div>


### 2. 测试普通 RAG 检索测试


```python
def run_normal_rag_test():
    """
    运行普通 RAG 检索测试
    测试 query_retrieval_knowledge 工具的检索流程
    """
    print("\n" + "="*70)
    print("🚀 开始执行普通 RAG 检索测试")
    print("="*70)

    # 测试提示词：触发 LangChain 知识库检索
    test_queries = [
        "LangChain 中的 Agent 是什么？它有哪些核心组件？",
        "如何在 LangChain 中使用 RAG 进行问答？",
        "LangGraph 和 LangChain 有什么区别？"
    ]

    print("\n可用的测试问题：")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")

    choice = input("\n请选择测试问题 (1-3) 或输入自定义问题: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(test_queries):
        user_input = test_queries[int(choice) - 1]
    else:
        user_input = choice if choice else test_queries[0]

    print(f"\n[用户]: {user_input}")
    print("\n[系统]: 开始处理请求...\n")

    # 使用新的 thread_id 避免与 HITL 测试冲突
    rag_config = {"configurable": {"thread_id": "rag-test-thread"}}

    # 用于跟踪已打印的消息，避免重复
    printed_message_ids = set()

    # 执行 Agent 流程
    for event in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=rag_config,
        stream_mode="values",
        context={"user_role": "开发者"}
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]

            # 使用消息 ID 来避免重复打印
            msg_id = getattr(last_msg, 'id', None)
            if msg_id and msg_id in printed_message_ids:
                continue

            if msg_id:
                printed_message_ids.add(msg_id)

            # 显示 AI 的思考过程
            if last_msg.type == "ai":
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    tool_call = last_msg.tool_calls[0]
                    print(f"🤖 [AI 决策]: 调用工具 -> {tool_call['name']}")
                    print(f"   参数: {tool_call.get('args', {})}")
                elif last_msg.content:
                    print(f"\n💬 [AI 回复]:\n{last_msg.content}")

            # 显示工具执行结果
            elif last_msg.type == "tool":
                tool_name = getattr(last_msg, 'name', 'unknown')
                print(f"\n🔧 [工具执行]: {tool_name}")
                print(f"📄 [检索结果]:\n{'-'*70}")
                # 只显示前500个字符，避免输出过长
                content = last_msg.content
                if len(content) > 500:
                    print(f"{content[:500]}...\n(结果已截断，共 {len(content)} 字符)")
                else:
                    print(content)
                print(f"{'-'*70}\n")

    print("\n" + "="*70)
    print("✅ 普通 RAG 检索测试完成！")
    print("="*70)

    # 打印统计信息
    print("\n📊 中间件统计信息:")
    logging_middleware.logger.print_statistics()```

```python
run_normal_rag_test()```

* 下面是通过LangSmith可视化调试的截图，可以清晰地看到Agent的运行状态和行为，包括状态的变化、工具的使用、模型的调用等。


<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v2_深色科技.html" width=80%></div>


* 也可以通过LangSmith可视化调试的截图，可以清晰地看到能将RAG检索到的文本块信息查询出来！



<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v3_活力清新.html" width=80%></div>

* 智能切换提示词中间件日志打印

<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v1_简洁现代.html" width=70%></div>

* 上下文压缩中间件日志打印


<div align=center><img src="../assets/第五课_01_AgenticRAG系统架构_v2_深色科技.html" width=80%></div>
