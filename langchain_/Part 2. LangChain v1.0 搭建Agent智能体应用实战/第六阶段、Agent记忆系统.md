## <center>第五阶段、 Agent记忆管理

&emsp;&emsp;LangChain 1.0的记忆管理与LangGraph的状态机制深度绑定，在 LangGraph 中，**记忆就是"持久化的状态（Persisted State）"**。

你需要掌握三个核心要素：

- **State (状态)**: 定义用来存储消息的结构（通常是 `MessagesState`）。

- **Checkpointer (检查点保存器)**: 负责在每一步结束后把状态保存下来（短期记忆通常用 `MemorySaver`）。

- **Thread ID (线程ID)**: 在调用时通过 `config` 传入，用来隔离不同用户的对话上下文。

**短期 vs 长期记忆的分界标准**

  * 误区：存储介质 = 记忆类型？

**错误认知：**

  * "内存 = 短期记忆"

  * "数据库 = 长期记忆"

**正确标准：**

  * 短期记忆：数据与会话（thread进程）生命周期绑定，随会话结束而被清理或遗忘

  * 长期记忆：数据与用户/业务实体生命周期绑定，跨会话持久保留并可主动检索


### 5.1 短期记忆管理

&emsp;&emsp;短期记忆通过LangGraph的`AgentState`（一个TypedDict）来管理。对话历史、中间步骤等信息被保存在状态中，并通过检查点（Checkpoints）机制在每次迭代后持久化。这使得长对话和失败恢复成为可能。

#### 1. Checkpointer机制

&emsp;&emsp;这是 LangGraph 记忆的灵魂。

- **不加这一行**：Agent 是无状态的。每次 `invoke` 都是全新的开始。

- **加上这一行**：LangGraph 会在每一步执行后，把 `state` 序列化并存入 `MemorySaver`。

- **原理**：当你再次 invoke 并传入 `thread_id` 时，LangGraph 会先去内存里查"这个 ID 上次停在哪里？状态是什么？"，然后加载状态，把你的新消息 `append` 进去，再继续运行。

#### 2 Thread ID配置

&emsp;&emsp;这是**短期记忆的"钥匙"**。

- 在 Web 开发中，这就是 Session ID。

- 你需要为每个用户或每个会话生成一个唯一的 ID。

- 不同的 ID 之间内存是完全隔离的（如代码中 `session_user_123` 和 `session_user_999` 的区别）。

#### InMemorySaver() 内存记忆管理

```python
import os
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, trim_messages

# ============ 初始化 LLM ============
model = load_chat_model(model="gpt-4o-mini",provider="openai")

# ============ 定义工具函数 ============
@tool
def get_user_info(name: str) -> str:
    """查询用户信息，返回姓名、年龄、爱好"""
    user_db = {
        "陈明": {"age": 28, "hobby": "旅游、滑雪、喝茶"},
        "张三": {"age": 32, "hobby": "编程、阅读、电影"}
    }
    info = user_db.get(name, {"age": "未知", "hobby": "未知"})
    return f"姓名: {name}, 年龄: {info['age']}岁, 爱好: {info['hobby']}"

# ============ 1. 基础短期记忆：InMemorySaver ============
"""
开发环境使用内存存储，重启后记忆丢失。
关键参数：
- checkpointer: 记忆存储对象
- thread_id: 会话唯一标识（用户级隔离）
"""
def demo_inmemory_memory():
    print("=" * 60)
    print("场景 1: 内存记忆（开发环境）")
    print("=" * 60)

    # 创建内存检查点
    memory = InMemorySaver()

    # 创建 Agent（自动继承对话记忆能力）
    agent = create_agent(
        model=model,
        tools=[get_user_info],
        checkpointer=memory  # 启用短期记忆
    )

    # 配置：thread_id 作为会话 ID
    config = {"configurable": {"thread_id": "user_123"}}

    # 第一轮对话：自我介绍
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "你好，我叫陈明，好久不见！"}]},
        config=config
    )
    print(f"用户：你好，我叫陈明，好久不见！")
    print(f"AI: {response1['messages'][-1].content}")
    print("-" * 40)

    # 第二轮对话：测试记忆
    response2 = agent.invoke(
        {"messages": [{"role": "user", "content": "请问你还记得我叫什么名字吗？"}]},
        config=config  # 使用相同 thread_id，自动携带上下文
    )
    print(f"用户：请问你还记得我叫什么名字吗？")
    print(f"AI: {response2['messages'][-1].content}")
    print("-" * 40)

    # 验证记忆状态
    state = agent.get_state(config)
    print(f"当前记忆轮次: {len(state.values['messages'])} 条消息")

    # 新开一个会话（不同 thread_id）
    config2 = {"configurable": {"thread_id": "user_456"}}
    response3 = agent.invoke(
        {"messages": [{"role": "user", "content": "我们之前聊过吗？"}]},
        config=config2
    )
    print(f"新会话 AI: {response3['messages'][-1].content}")  # 应无记忆

demo_inmemory_memory()```

#### PostgresSaver() 数据库持久化记忆

* PostgresSaver 即使存储到数据库，仍然属于短期记忆。仍然属于短期记忆的原因：

* 作用域限制：它只检索和加载当前 thread_id 的数据

* 生命周期管理：默认不会主动清理，但数据语义上属于"本次会话"

* 无跨会话检索能力：无法在新会话中自动访问旧会话数据（除非手动指定旧 thread_id）

```python
#系统安装postgresql
#brew install postgresql```

```python
#!pip install langgraph-checkpoint-postgres  # 生产环境使用```

```python
# 测试数据库是否连接正常
!psql -U myuser -d mydatabase -c "SELECT version();"```

<div align=center><img src="https://zrj18330672592.oss-cn-beijing.aliyuncs.com/20251125212642742.png" width=80%></div>


```python
from langgraph.checkpoint.postgres import PostgresSaver

"""
生产环境使用数据库存储，支持：
- 持久化（重启不丢失）
- 多实例共享（分布式部署）
- 大规模并发
"""

print("\n" + "=" * 60)
print("场景 2: Postgres 持久化记忆（生产环境）")
print("=" * 60)

# 定义工具函数：查询用户信息
@tool
def get_user_info(name: str) -> str:
    """查询用户信息，返回姓名、年龄、爱好"""
    user_db = {
        "陈明": {"age": 28, "hobby": "旅游、滑雪、喝茶"},
        "张三": {"age": 32, "hobby": "编程、阅读、电影"}
    }
    info = user_db.get(name, {"age": "未知", "hobby": "未知"})
    return f"姓名: {name}, 年龄: {info['age']}岁, 爱好: {info['hobby']}"

# 创建模型
model = load_chat_model(model="gpt-4o-mini",provider="openai")

# 数据库连接字符串
DB_URI = "postgresql://myuser:123456@localhost:5432/mydatabase"

# 使用上下文管理器确保连接正确关闭
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # 自动创建表结构（仅首次运行）
    checkpointer.setup()

    # 创建智能体
    agent = create_agent(
        model=model,
        tools=[get_user_info],
        checkpointer=checkpointer
    )

    # 配置线程 ID（用于区分不同用户）
    config = {"configurable": {"thread_id": "production_user_001"}}

    # 模拟用户注册流程
    agent.invoke(
        {"messages": [{"role": "user", "content": "我是新用户张三，请记录我的信息"}]},
        config=config
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "我是谁？"}]},
        config=config
    )
    print(f"AI: {response['messages'][-1].content}")```

```python
!psql -U myuser -d mydatabase -c "SELECT * FROM checkpoints WHERE thread_id = 'production_user_001' LIMIT 3;"```

| 特性维度     | **InMemorySaver**                 | **PostgresSaver**                 |
| ------------ | --------------------------------- | --------------------------------- |
| **存储位置** | 内存（Python dict）               | PostgreSQL 数据库                 |
| **生命周期** | **会话级**（与 `thread_id` 绑定） | **会话级**（与 `thread_id` 绑定） |
| **作用域**   | 单一会话（无法跨线程）            | 单一会话（无法跨线程）            |
| **持久化**   | 进程重启后丢失                    | 进程重启后保留                    |
| **数据隔离** | `thread_id`                       | `thread_id`                       |
| **适用环境** | 开发、测试                        | 生产、分布式部署                  |
| **性能**     | 极高（纳秒级）                    | 较高（毫秒级）                    |
| **扩展性**   | 单进程限制                        | 支持多实例、高并发                |
| **核心定位** | **短期记忆**                      | **短期记忆（持久化版）**          |

### 5.2 上下文裁剪

&emsp;&emsp;此外，真正的**记忆管理**还涉及"上下文窗口控制"（防止对话太长撑爆 Token），这需要配合 `trim_messages` 使用。

- **问题**：如果不处理，随着对话进行，`state["messages"]` 会包含几千条消息。直接全部传给 LLM 会导致：1. 烧钱；2. 超过 128k/8k 限制报错。

- **解决**：我们在 `call_model` 内部使用了 trimmer。

  - **State 中**：依然保存了 100% 的完整历史（为了审计或回溯）。

  - **传给 LLM 时**：只传最近的 N 个 Token（或 N 条消息）。

- **start_on="human"**: 这是一个很细节的最佳实践。如果截断导致第一条消息是 AI 的回复（没有对应的 User 问题），某些模型会感到困惑。这个参数确保截断后的对话总是以 User 开始。

```python
# ============ 核心模块导入 ============
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver  # 短期记忆存储
from langchain_core.messages import trim_messages  # 消息裁剪工具
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ============ 初始化 LLM 与工具 ============
model = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    temperature=0.7
)

# 1. 定义天气查询工具
@tool
def search_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city}天气：晴，25°C"

# ============ 配置裁剪参数 ============
MAX_TOKENS = 100  # 根据模型上下文长度调整，上下文128K的话，一般设置为4000左右
TRIM_STRATEGY = "last"  # 保留最新消息
INCLUDE_SYSTEM = True  # 系统消息不参与裁剪

"""
tiktoken 是 OpenAI 官方 token 编码库，支持精确计数。
不同模型需使用不同编码：
- gpt-4o, gpt-4o-mini: o200k_base
- gpt-4-turbo: cl100k_base
- text-davinci-003: p50k_base
"""
import tiktoken

# 2. 定义 Token 编码器获取函数
def get_token_encoder(model_name: str = "gpt-4o-mini"):
    """获取 tiktoken 编码器实例"""
    try:
        # 自动映射模型到编码器
        encoding = tiktoken.encoding_for_model(model_name)
        print(f"✅ 已加载模型 '{model_name}' 的 tiktoken 编码器")
        return encoding
    except KeyError:
        # 如果模型不在官方列表，使用默认编码
        print(f"⚠️  模型 '{model_name}' 未在映射表中，使用默认编码 'o200k_base'")
        return tiktoken.get_encoding("o200k_base")

# 3. 初始化编码器（全局复用提升性能）
TOKEN_ENCODER = get_token_encoder("gpt-4o-mini")

# ============ 2. 精确 Token 计数函数 ============
def count_tokens_tiktoken(messages):
    """
    使用 tiktoken 精确计算消息列表的 token 总数

    参数:
        messages: List[BaseMessage] - 消息对象列表

    返回:
        int: 总 token 数

    说明:
        - 每个消息包含角色、内容和元数据，需完整编码
        - 不同消息格式（Human/AI/System）的 token 开销不同
        - 此函数模拟真实 API 调用的 token 计数逻辑
    """
    total_tokens = 0

    # 遍历每条消息，累加 token 数
    for message in messages:
        # 消息格式：role + content + 特殊标记
        # 典型格式：<|im_start|>role<|im_end|>content<|im_end|>

        # 角色 token（如 "user", "assistant", "system"）
        role_tokens = len(TOKEN_ENCODER.encode(message.type))

        # 内容 token（消息正文）
        content_tokens = len(TOKEN_ENCODER.encode(message.content))

        # 格式开销（OpenAI 消息边界标记）
        # 每条约 4 个特殊 token（开始、角色、结束、内容结束）
        format_overhead = 4

        total_tokens += role_tokens + content_tokens + format_overhead

    return total_tokens

# ============ 创建Agent ============
def create_trimmed_agent():
    """创建 Agent 并配置 InMemorySaver"""
    memory = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=[search_weather],
        system_prompt="你是一个简洁的助手，记住用户提到的城市名称",
        checkpointer=memory  # 启用短期记忆
    )

    return agent

# ============ 手动裁剪并调用 Agent ============
def invoke_with_trim(agent, user_input: str, config: dict):
    """
    在调用 Agent 前手动裁剪上下文

    流程：
    1. 获取当前状态（所有历史消息）
    2. 使用 trim_messages 裁剪
    3. 构建新输入（裁剪后的消息 + 新消息）
    4. 调用 Agent
    """
    # 1. 获取当前记忆状态
    state = agent.get_state(config)
    existing_messages = state.values.get("messages", []) if state else []

    # 精确计算当前 token 数
    current_tokens = count_tokens_tiktoken(existing_messages)

    # 2. 如果有历史消息，先裁剪
    if existing_messages:
        print(f"裁剪前消息数: {len(existing_messages)}")

        # 核心：调用 trim_messages 进行裁剪
        trimmed_messages = trim_messages(
            existing_messages,                    # 待裁剪的消息列表
            max_tokens=MAX_TOKENS,                # 允许的最大 token 数，超过则触发裁剪
            token_counter=count_tokens_tiktoken,  # token 计数函数
            strategy=TRIM_STRATEGY,               # 裁剪策略，"last" 保留最新消息，"first" 保留最早消息
            include_system=INCLUDE_SYSTEM,        # 是否保留系统消息（通常必须保留）
            allow_partial=False,                  # False不允许部分消息，会尝试保留消息的完整性。如果无法在保持消息完整性的前提下将总token数裁剪到参数 max_tokens 以内，就会返回 空列表
            start_on="human"                      # 从 human 消息开始裁剪
        )

        # 计算裁剪后的 token 数
        new_tokens = count_tokens_tiktoken(trimmed_messages)

        print(f"裁剪后 token: {new_tokens}，裁剪后消息数: {len(trimmed_messages)}")
    else:
        trimmed_messages = []

    # 3. 添加新消息
    new_messages = trimmed_messages + [HumanMessage(content=user_input)]

    # 4. 调用 Agent（checkpointer 会自动保存新状态）
    response = agent.invoke(
        {"messages": new_messages},
        config=config
    )

    return response

# ============ 演示多轮对话与裁剪 ============
def demo_manual_trim():
    """演示手动裁剪上下文的多轮对话"""
    print("=" * 60)
    print("场景：手动 trim_messages + InMemorySaver")
    print("=" * 60)

    agent = create_trimmed_agent()
    config = {"configurable": {"thread_id": "trim_user_001"}}

    # 模拟多轮对话
    conversations = [
        "你好，我叫陈明",
        "查询北京天气",
        "上海呢？",
        "明天北京天气如何？",  # 此时会触发裁剪
        "我是谁？",  # 测试记忆是否保留
    ]

    for i, query in enumerate(conversations, 1):
        print(f"\n--- 第 {i} 轮 ---")
        print(f"用户: {query}")

        # 每次调用前自动裁剪
        response = invoke_with_trim(agent, query, config)

        print(f"AI: {response['messages'][-1].content}")
        print("-" * 40)

# ============ 运行演示 ============
if __name__ == "__main__":
    demo_manual_trim()```

### 5.3 自定义 State 扩展

在 LangGraph 中，AgentState 是一个 TypedDict，定义了 Agent 执行过程中流转的数据结构。扩展 State = 在基础结构上增加自定义字段，用于携带更多上下文和业务数据。
* 扩展 State 的本质：在 LangGraph 中，State 是 Agent 的  "内存"  和 "消息总线" ，扩展它就像给程序增加新的全局变量，但这些变量随执行流自动流转、隔离、持久化，是实现复杂 Agent 逻辑的基础。

**扩展 State 核心目的**

* 跨步骤持久化上下文：Agent 执行是多步骤的（LLM调用 → 工具调用 → 结果解析），扩展的 State 字段能在所有步骤间共享。

* 实现条件分支与动态路由：根据 State 中的字段值，决定 Agent 的下一步走向。

* 支持多模态与复杂输入：现代 Agent 需要处理图片、文件等非文本数据，扩展到 State 中。

* 实现记忆与持久化：扩展字段用于存储长期记忆，跨会话保持。

* 性能监控与调试：扩展字段用于记录性能指标，便于分析优化。

```python
class ExtendedState(TypedDict):
    messages: list[BaseMessage]
    user_id: str           # 扩展：用户身份，用于权限控制和个性化
    session_id: str        # 扩展：会话标识，用于对话历史管理
    retry_count: int       # 扩展：重试次数，用于错误处理策略
    original_query: str    # 扩展：原始查询，用于日志和审计
```

**使用 TypedDict 当且仅当：**

* 性能极度敏感（如高频API响应，避免Pydantic序列化开销）

* 数据结构简单（无嵌套或浅层嵌套）

* 仅需类型提示（团队强制使用mypy，且信任数据输入）

* 外部库要求（如某些ORM返回TypedDict）


```python
# ============ 自定义 State 扩展 ============
"""
通过 TypedDict 扩展 AgentState，添加业务字段（用户ID、偏好等）。
LangChain 1.0 推荐使用 TypedDict 而非 Pydantic。
"""
from typing import TypedDict, Optional
from langchain.agents import AgentState, create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 定义自定义 State 结构
class CustomAgentState(AgentState):
    """扩展的 Agent 状态，包含业务上下文"""
    user_id: str  # 用户唯一标识
    preferences: dict  # 用户偏好（主题、语言等）
    visit_count: int  # 访问次数

# ============ 定义带状态访问的工具 ============
from langchain.tools import ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage

# 定义工具函数：更新用户偏好
@tool
def update_user_preference(runtime: ToolRuntime, theme: str) -> Command:
    """
    更新用户主题偏好，写入短期记忆

    ToolRuntime 提供对 state 和 context 的访问能力：
    - runtime.state: 当前状态（含自定义字段）
    - runtime.context: 调用上下文
    - runtime.tool_call_id: 工具调用ID
    """
    # 从当前状态获取偏好（如果不存在则初始化）
    current_prefs = runtime.state.get("preferences", {})
    current_prefs["theme"] = theme

    # 返回 Command 对象，指示状态更新
    return Command(update={
        "preferences": current_prefs,
        "messages": [
            ToolMessage(
                content=f"成功更新主题为: {theme}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

# 定义工具函数：根据用户偏好生成问候
@tool
def greet_user(runtime: ToolRuntime) -> str:
    """根据用户偏好生成个性化问候"""
    user_name = runtime.state.get("user_id", "访客")
    prefs = runtime.state.get("preferences", {})
    theme = prefs.get("theme", "默认")

    return f"欢迎回来，{user_name}！当前主题: {theme}"

# ============ 创建带自定义状态的 Agent ============
def demo_custom_state():
    print("\n" + "=" * 60)
    print("场景 3: 自定义 State 扩展记忆维度")
    print("=" * 60)

    # 使用内存存储
    checkpointer = InMemorySaver()

    # 创建 Agent，指定自定义 state_schema
    agent = create_agent(
        model=model,
        tools=[update_user_preference, greet_user],
        state_schema=CustomAgentState,  # 关键：传入自定义状态类型
        checkpointer=checkpointer
    )

    # 配置线程 ID（用于区分不同用户）
    config = {"configurable": {"thread_id": "custom_state_user"}}

    # 第一轮：初始化用户信息
    result1 = agent.invoke(
        {
            "messages": [{"role": "user", "content": "设置主题为暗黑模式"}],
            "user_id": "user_789",  # 自定义字段
            "preferences": {"language": "zh-CN"},  # 初始偏好
            "visit_count": 1
        },
        config=config
    )
    print(f"第一轮: {result1['messages'][-1].content}")
    print("-" * 40)

    # 第二轮：读取记忆
    result2 = agent.invoke(
        {"messages": [{"role": "user", "content": "打个招呼"}]},
        config=config
    )
    print(f"第二轮: {result2['messages'][-1].content}")
    print("-" * 40)

    # 查看完整状态
    state = agent.get_state(config)
    print("当前记忆状态:")
    print(f"  用户ID: {state.values.get('user_id')}")
    print(f"  偏好: {state.values.get('preferences')}")
    print(f"  消息数: {len(state.values['messages'])}")

# ============ 运行自定义状态示例 ============
if __name__ == "__main__":
    demo_custom_state()```

| 场景               | TypedDict              | Pydantic                   |
| ------------------ | ---------------------- | -------------------------- |
| **FastAPI请求体**  | ❌ 不推荐（需手动验证） | ✅ **最佳选择**（原生集成） |
| **GraphQL响应**    | ✅ 适合（结构固定）     | ⚠️ 可但较重                 |
| **内部函数参数**   | ✅ 轻量且有效           | ❌ 过度设计                 |
| **CLI工具配置**    | ⚠️ 需手动校验           | ✅ 自动验证友好             |
| **数据处理流水线** | ✅ 零开销传递           | ⚠️ 频繁转换有成本           |
| **机器学习特征**   | ✅ 快速定义结构         | ❌ 不必要                   |
| **微服务DTO**      | ⚠️ 需结合mypy           | ✅ 天然支持序列化           |
| **测试Mock数据**   | ✅ 快速创建             | ⚠️ 验证可能碍事             |

**记忆核心原则**

* 隔离性：每个用户必须分配唯一 thread_id，避免串话

* 持久化：生产环境必须使用数据库检查点，支持服务重启和高可用

* 可控性：自定义 State 和中间件实现业务逻辑与记忆管理的分离

* 性能：长对话必须启用摘要机制，防止 token 超限和响应延迟

### 5.4 长期记忆

&emsp;&emsp;长期记忆通过与外部向量数据库或键值存储集成来实现。可以在Agent执行的关键节点（如对话结束时）提取关键信息、用户偏好等，并存入长期记忆库，供未来的对话使用。

#### 1. 语义检索与向量数据库

&emsp;&emsp;向量数据库是实现长期记忆的核心技术，通过语义相似度搜索实现知识的长期存储和检索。

**技术实现：**

- **向量化存储**：将对话内容、用户偏好等转换为向量表示

- **语义检索**：基于向量相似度实现智能搜索

- **多模态支持**：支持文本、图像、音频等多种数据类型

- **高性能查询**：支持大规模数据的快速检索

**典型实现：**

- Milvus：开源向量数据库，支持大规模向量检索

- Qdrant：高性能向量搜索引擎

- Pinecone：云原生向量数据库服务

- Chroma: 轻量级向量数据库，可本地持久化

```python
#!pip install langchain-chroma```

```python
import os
import uuid
from typing import List

# --- 1. 导入组件 ---
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_chroma import Chroma # 向量数据库
from langchain_core.documents import Document
from langchain.agents import AgentState, create_agent
from langgraph.checkpoint.memory import MemorySaver

# 确保配置了 OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = "sk-..."

# ==========================================
# 2. 初始化向量数据库 (长期记忆的物理载体)
# ==========================================
# 在生产环境中，这里应该是连接到 Pinecone, Milvus 或本地持久化的 Chroma
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma(
    collection_name="agent_long_term_memory",
    embedding_function=embeddings,
    #persist_directory="./chroma_db" # 如果想存到硬盘，取消注释这一行
)

# ==========================================
# 3. 定义记忆工具 (Agent 的手)
# ==========================================
# 3.1 定义记忆保存工具
# ==========================================
@tool
def save_memory(content: str):
    """
    将重要信息保存到长期记忆中。
    当你获知用户的喜好、职业、计划或其他长期有效的事实时，调用此工具。
    参数:
        content (str): 要保存的记忆内容。
    """
    print(f"\n[记忆操作] 正在保存记忆: '{content}'")
    # 将文本封装为 Document
    doc = Document(
        page_content=content,
        metadata={"source": "user_interaction", "timestamp": "simulated_time"}
    )
    # 写入向量库
    vector_store.add_documents([doc])
    return "记忆已成功保存。"

# 3.2 定义记忆搜索工具
# ==========================================
@tool
def search_memory(query: str):
    """
    从长期记忆中搜索相关信息。
    当你被问及关于用户过去的问题，或者你不确定答案时，使用此工具进行查找。
    参数:
        query (str): 要搜索的查询语句。
    """
    print(f"\n[记忆操作] 正在搜索记忆: '{query}'")

    # 执行语义搜索 (k=2 表示只取最相关的2条)
    results = vector_store.similarity_search(query, k=2)

    if not results:
        return "没有找到相关的记忆。"

    # 将搜索结果拼接成字符串返回给 Agent
    memory_content = "\n".join([f"- {doc.page_content}" for doc in results])
    return f"找到以下相关记忆:\n{memory_content}"

# 将工具放入列表
tools = [save_memory, search_memory]

# ==========================================
# 4. 创建 Agent
# ==========================================

# 定义系统提示词：教会 Agent 何时使用记忆工具
SYSTEM_PROMPT = """你是一个拥有长期记忆的私人助手。
你的目标是记住用户的喜好和重要信息，以便提供个性化服务。

1. 如果用户告诉你任何关于他们自己的事实（如名字、喜好、居住地），请务必调用 'save_memory' 工具保存。
2. 如果用户问你一个问题，而答案可能在你之前的记忆中，请先调用 'search_memory' 工具查找。
3. 如果只是闲聊，不需要调用工具。
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0) # 建议使用 GPT-4 或更强的模型以保证工具调用准确率

# 使用 checkpointer 依然是必要的，用于维持当前这一轮对话的上下文
checkpointer = MemorySaver()

# 创建 Agent 应用
agent_app = create_agent(
    llm,
    tools,
    system_prompt=SYSTEM_PROMPT, # 注入系统提示词
    checkpointer=checkpointer
)

# ==========================================
# 5. 运行演示
# ==========================================

def run_demo():
    # === 场景 A：存入记忆 ===
    # 使用一个 thread_id，代表这是今天的对话
    config_a = {"configurable": {"thread_id": "session_today"}}

    print("--- 场景 A：用户告诉 Agent 喜好 ---")
    user_input_1 = "你好，记住我最喜欢的水果是草莓，而且我对花生过敏。"

    # 运行 Agent，stream_mode="values"参数，返回每个时间步的中间结果
    for chunk in agent_app.stream({"messages": [HumanMessage(content=user_input_1)]}, config=config_a, stream_mode="values"):
        # 只打印最后一条机器人的回复
        pass
    print(f"Agent: {chunk['messages'][-1].content}")

    # === 场景 B：模拟遗忘 (开启新线程) ===
    # 我们换一个 thread_id，这意味着 Agent 失去了“短期记忆” (MemorySaver 里的东西访问不到了)
    # 但是，长期记忆在 VectorStore 里，是可以跨 thread 访问的！
    config_b = {"configurable": {"thread_id": "session_tomorrow"}}

    print("\n--- 场景 B：第二天 (新的 Session，短期记忆已清空) ---")
    user_input_2 = "我想吃点零食，但我忘了我有什么忌口，你能帮我查查吗？"

    print(f"User: {user_input_2}")

    # 观察控制台输出，你会看到 Agent 自动调用 search_memory
    final_response = None
    for chunk in agent_app.stream({"messages": [HumanMessage(content=user_input_2)]}, config=config_b, stream_mode="values"):
        final_response = chunk['messages'][-1]

    print(f"Agent: {final_response.content}")

if __name__ == "__main__":
    run_demo()```

### 5.5 跨线程记忆

&emsp;&emsp;针对"跨线程记忆（Cross-Thread Memory）"的管理，在 LangChain 1.0 / LangGraph 体系中，这通常被称为"用户级状态（User-Level State）" 或"全局记忆"。

它与前两个问题的区别在于：

- **短期记忆 (`Checkpointer`)**：只在 `thread_id`（一次会话）内有效。

- **长期记忆 (`VectorStore`)**：存的是模糊的知识片段。

- **跨线程记忆 (BaseStore)**：存的是**结构化的用户档案（User Profile）**，例如用户的姓名、VIP等级、偏好设置等。无论用户开多少个新聊天窗口（Thread），这些信息都必须存在。

### BaseStore结构化存储

`BaseStore` 是 LangGraph 提供的**通用键值存储抽象接口**，专为**结构化长期记忆**设计，核心特性包括：

   * 命名空间（Namespace）机制

   * 采用**层次化元组路径**组织数据，类似文件系统目录结构：

```python
namespace = ("users", "user_123", "preferences")
# 对应逻辑路径：users/user_123/preferences
```

**核心操作**

- `put(namespace, key, value)`：存储键值对（支持TTL过期）

- `get(namespace, key)`：精确检索单个记忆

- `search(namespace, query)`：语义搜索（需子类支持）

- `delete(namespace, key)`：删除记忆

```python
import os
from dotenv import load_dotenv
import time
import uuid
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent, AgentState
from typing import Annotated
from pydantic import BaseModel, Field

# --- 核心组件：Postgres 持久化检查点 ---
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.store.base import BaseStore
from langgraph.prebuilt import InjectedStore,InjectedState
from psycopg_pool import ConnectionPool
#from langchain_community.storage import MongoDBStore

# 配置 API KEY
load_dotenv(override=True)

# ==========================================
# 1. 数据库配置
# ==========================================
# 对应上面 Docker 启动命令的配置
DB_URI = "postgresql://myuser:123456@localhost:5432/mydatabase"
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ==========================================
# 2. 定义工具 (Tools)
# ==========================================
@tool
def magic_calculation(a: int, b: int) -> int:
    """进行一次特殊的加法计算"""
    return (a + b) * 10

"""
跨线程记忆需要传递 user_id，通过自定义 State 实现
"""
class CrossThreadState(AgentState):
    user_id: str  # 跨线程记忆的唯一标识

# ============ 定义 Pydantic 模型用于提取用户信息 ===========
class UserInfo(BaseModel):
    """从文本中提取的用户信息"""
    user_name: str = Field(description="用户的名字，例如：Alice、Bob、张三等")
    additional_info: str = Field(description="关于用户的其他信息，例如职业、兴趣爱好等")

class QueryInfo(BaseModel):
    """从查询文本中提取的信息"""
    user_name: str = Field(
        description="要查询的用户名字。如果查询中包含'我的'、'我是'等第一人称，请从对话历史中提取用户名；如果没有明确的用户名，返回'all_users'"
    )
    query_content: str = Field(description="查询的具体内容，例如：职业、兴趣爱好等")

# ============ 定义记忆管理工具（使用 BaseStore）===========
# 注意：store 参数使用 InjectedStore 注解，由 LangGraph 自动注入
# InjectedStore() 标记会让 Pydantic 在生成 JSON Schema 时跳过这个参数
# LLM 不会看到 store 参数，只会看到 user_id 和 info
@tool
def remember_user_info(
    info: str,
    state: Annotated[dict, InjectedState()],
    store: Annotated[BaseStore, InjectedStore()]
) -> str:
    """
    将用户信息存入跨线程记忆

    重要：此工具会自动从 state 中获取 user_id，并使用 Pydantic 提取用户信息

    参数说明：
        info: 要记忆的信息（例如：用户的名字、职业、偏好等）

    示例：
        - remember_user_info("用户名叫 Alice，是一名工程师")
        - remember_user_info("我是 Bob，喜欢深度学习")
    """
    # 使用 Pydantic 提取用户信息
    structured_llm = llm.with_structured_output(UserInfo)

    try:
        # 从文本中提取结构化信息
        extracted_info = structured_llm.invoke(
            f"从以下文本中提取用户名和其他信息：{info}"
        )

        # 优先使用提取的用户名，如果提取失败则使用 state 中的 user_id
        extracted_user_name = extracted_info.user_name.lower()
        state_user_id = state.get("user_id", "unknown_user")

        # 如果提取到的用户名不是 unknown，则使用提取的用户名
        if extracted_user_name and extracted_user_name != "unknown":
            user_id = extracted_user_name
        else:
            user_id = state_user_id

        full_info = f"{extracted_info.user_name}: {extracted_info.additional_info}"

    except Exception as e:
        # 如果提取失败，使用 state 中的 user_id
        user_id = state.get("user_id", "unknown_user")
        full_info = info

    # 命名空间设计：(用户ID, 信息类别)
    namespace = (user_id, "profile")

    # 生成唯一记忆ID
    memory_id = str(uuid.uuid4())

    # 存储到 BaseStore（自动持久化）
    store.put(
        namespace,
        memory_id,
        {
            "info": full_info,
            "timestamp": "2025-11-25",
            "source": "user_input"
        }
    )

    return f"✅ 已将信息存入长期记忆 (用户: {user_id}): {full_info}"

@tool
def recall_user_info(
    query: str,
    state: Annotated[dict, InjectedState()],
    store: Annotated[BaseStore, InjectedStore()]
) -> str:
    """
    从跨线程记忆中检索用户信息

    重要：此工具会自动从 state 中获取 user_id

    参数说明：
        query: 查询关键词（用于描述要查找的信息，例如"我的职业"、"我的兴趣"等）

    返回：用户的历史信息
    """
    # 优先从 state 中获取 user_id
    state_user_id = state.get("user_id", None)

    # 如果 state 中没有 user_id，尝试使用 Pydantic 从查询中提取
    if not state_user_id:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        structured_llm = llm.with_structured_output(QueryInfo)

        try:
            # 从查询文本中提取结构化信息
            prompt = f"""从以下查询中提取用户名和查询内容。

                    查询文本：{query}
                    
                    注意：
                    1. 如果查询中包含"我的"、"我是"等第一人称词汇，说明用户在询问自己的信息
                    2. 如果能从查询中推断出具体的用户名（如 Alice、Bob），请提取该用户名
                    3. 如果无法确定具体用户，返回 'all_users'
            """
            extracted_query = structured_llm.invoke(prompt)

            # 如果提取到的是 'all_users'，则搜索所有用户
            if extracted_query.user_name.lower() in ['all_users', 'current_user', 'unknown']:
                user_id = None
            else:
                user_id = extracted_query.user_name.lower()

        except Exception as e:
            # 如果提取失败，搜索所有用户
            user_id = None
    else:
        # 使用 state 中的 user_id
        user_id = state_user_id

    try:
        if user_id:
            # 使用 namespace_prefix 搜索该用户的所有记忆
            namespace_prefix = (user_id,)
            memories = store.search(namespace_prefix, limit=20)
        else:
            # 搜索所有已知用户的记忆
            memories = []
            # 先尝试获取所有可能的用户
            for uid in ['alice', 'bob', 'unknown_user']:
                namespace_prefix = (uid,)
                user_memories = store.search(namespace_prefix, limit=20)
                memories.extend(user_memories)

        if not memories:
            return f"未找到相关记忆。请先告诉我一些信息，我会记住它们。"

        # 格式化返回
        results = []
        for item in memories:
            info = item.value.get('info', '未知信息')
            timestamp = item.value.get('timestamp', '未知时间')
            results.append(f"- {info} (记录时间: {timestamp})")

        return f"找到 {len(results)} 条记忆:\n" + "\n".join(results)

    except Exception as e:
        return f"检索记忆时出错: {str(e)}"
```

```python
# ==========================================
# 3. 主程序逻辑
# ==========================================
def run_postgres_agent():
    print("--- 正在连接 PostgreSQL 数据库 ---")

    # 使用 ConnectionPool 管理数据库连接
    # PostgresSaver 需要在这个上下文管理器中运行
    with ConnectionPool(conninfo=DB_URI, max_size=20, kwargs={"autocommit": True}) as pool:

        # --- A. 初始化 Checkpointer 和 Store ---
        checkpointer = PostgresSaver(pool)
        store = PostgresStore(pool)

        # 注意：第一次运行时需要创建表结构，会检测数据库，如果不存在，会自动创建所需的表结构。
        # 生产环境只需运行一次，但在脚本中加上是安全的（幂等操作）。
        # checkpointer 会创建 'checkpoints', 'checkpoint_blobs' 等表
        # store 会创建 'store' 表
        print("🔧 初始化 Checkpointer 表结构...")
        checkpointer.setup()
        print("✅ Checkpointer 表结构初始化完成")

        print("🔧 初始化 Store 表结构...")
        store.setup()
        print("✅ Store 表结构初始化完成")

        # --- B. 创建 Agent ---

        # 包含所有工具：计算工具 + 跨线程记忆工具
        tools = [magic_calculation, remember_user_info, recall_user_info]

        agent = create_agent(
            model=llm,
            tools=tools,
            state_schema=CrossThreadState,  # 自定义状态传递 user_id
            system_prompt="""
            你是一个具备跨线程记忆的智能助手。

            你的能力：
            1. 使用 remember_user_info 工具将用户的重要信息存入长期记忆（跨会话持久化）
            2. 使用 recall_user_info 工具从长期记忆中检索用户信息
            3. 使用 magic_calculation 工具进行特殊计算
            
            工作流程：
            - 当用户告诉你他的名字、职业、偏好等信息时，主动调用 remember_user_info 存储
            - 当用户询问"你还记得我吗"或类似问题时，调用 recall_user_info 检索
            - 记忆是跨会话的，即使在新的对话中也能记住用户信息
            
            注意：调用 remember_user_info 和 recall_user_info 时，必须传入 user_id 参数（从 state 中获取）。
            """,
            store=store,  # ✅ 注入 BaseStore 实现跨线程记忆
            checkpointer=checkpointer  # 注入数据库检查点（单会话记忆）
        )

        # ==========================================
        # 4. 测试场景：跨线程记忆功能
        # ==========================================

        print("\n" + "="*70)
        print("场景 1：用户 Alice 第一次对话（会话 1）")
        print("="*70)

        # 1. Alice 的第一个会话
        thread1_config = {"configurable": {"thread_id": "session_alice_001"}}

        print("\n👤 用户 Alice: 你好，我是 Alice，一名 Python 开发工程师，我喜欢深度学习。")

        for chunk in agent.stream(
            {
                "messages": [HumanMessage(content="你好，我是 Alice，一名 Python 开发工程师，我喜欢深度学习。")],
                "user_id": "alice"  # 传入 user_id
            },
            config=thread1_config,
            stream_mode="values"
        ):
            last_msg = chunk["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                print(f"🤖 Agent: {last_msg.content}")
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    print(f"   🔧 [调用工具]: {tool_call['name']}")

        print("\n" + "="*70)
        print("场景 2：用户 Alice 第二次对话（会话 2 - 不同 thread_id）")
        print("="*70)
        print("💡 模拟：Alice 关闭浏览器，第二天重新打开，开始新会话")
        time.sleep(1)

        # 2. Alice 的第二个会话（不同的 thread_id）
        thread2_config = {"configurable": {"thread_id": "session_alice_002"}}

        print("\n👤 用户 Alice: 你还记得我是谁吗？我的职业是什么？")

        for chunk in agent.stream(
            {
                "messages": [HumanMessage(content="你还记得我是谁吗？我的职业是什么？")],
                "user_id": "alice"  # ✅ 同样的 user_id
            },
            config=thread2_config,
            stream_mode="values"
        ):
            last_msg = chunk["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                print(f"🤖 Agent: {last_msg.content}")
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    print(f"   🔧 [调用工具]: {tool_call['name']}")

        print("\n" + "="*70)
        print("场景 3：用户 Bob 的对话（不同用户）")
        print("="*70)

        # 3. Bob 的会话
        thread3_config = {"configurable": {"thread_id": "session_bob_001"}}

        print("\n👤 用户 Bob: 你好，我是 Bob，一名产品经理，帮我算一下 10 + 20 的特殊结果。")

        for chunk in agent.stream(
            {
                "messages": [HumanMessage(content="你好，我是 Bob，一名产品经理，帮我算一下 10 + 20 的特殊结果。")],
                "user_id": "bob"  # ✅ 不同的 user_id
            },
            config=thread3_config,
            stream_mode="values"
        ):
            last_msg = chunk["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                print(f"🤖 Agent: {last_msg.content}")
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    print(f"   🔧 [调用工具]: {tool_call['name']}")

        print("\n" + "="*70)
        print("场景 4：Alice 第三次对话（验证记忆隔离）")
        print("="*70)
        print("💡 验证：Alice 的记忆不会被 Bob 的信息污染")

        # 4. Alice 的第三个会话
        thread4_config = {"configurable": {"thread_id": "session_alice_003"}}

        print("\n👤 用户 Alice: 我的兴趣爱好是什么？")

        for chunk in agent.stream(
            {
                "messages": [HumanMessage(content="我的兴趣爱好是什么？")],
                "user_id": "alice"
            },
            config=thread4_config,
            stream_mode="values"
        ):
            last_msg = chunk["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                print(f"🤖 Agent: {last_msg.content}")
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    print(f"   🔧 [调用工具]: {tool_call['name']}")

        print("\n" + "="*70)
        print("✅ 跨线程记忆测试完成！")
        print("="*70)
        print("\n 测试总结:")
        print("  ✅ 场景 1: Alice 首次对话，Agent 自动存储用户信息到 Store")
        print("  ✅ 场景 2: Alice 新会话（不同 thread_id），Agent 成功从 Store 检索记忆")
        print("  ✅ 场景 3: Bob 的对话，Agent 为 Bob 创建独立的记忆空间")
        print("  ✅ 场景 4: Alice 再次对话，记忆未被 Bob 的信息污染")
        print("\n💡 关键特性:")
        print("  - Checkpointer: 管理单个会话的对话历史（基于 thread_id）")
        print("  - Store: 管理跨会话的长期记忆（基于 user_id）")
        print("  - 记忆隔离: 不同用户的记忆完全隔离（通过 namespace）")
        print("  - 持久化: 所有数据存储在 PostgreSQL，重启程序后依然可用")
        print("="*70)```

```python
run_postgres_agent()```

```python
run_postgres_agent()```

```python
!psql -U myuser -d mydatabase -c "SELECT prefix, LEFT(key, 8) as key_prefix, value->>'info' as info FROM store ORDER BY created_at;"```

```python
# 测试过程中，如果数据错乱有问题，可以先清空再尝试；但在生成环境中慎重做此操作！！！
!psql -U myuser -d mydatabase -c "TRUNCATE TABLE checkpoints, checkpoint_blobs, checkpoint_writes, store CASCADE;"```

| 维度           | BaseStore方案                                      | 向量数据库方案                              |
| -------------- | -------------------------------------------------- | ------------------------------------------- |
| **依赖导入**   | `from langgraph.store.memory import InMemoryStore` | `from langchain.vectorstores import Chroma` |
| **存储内容**   | **结构化字典/列表**（JSON序列化）                  | **非结构化文本**（自动Embedding）           |
| **检索方式**   | **`get()`精确匹配** + `search()`简单搜索           | **`similarity_search()`语义相似**           |
| **创建Agent**  | `create_agent(llm, tools, system_message)`         | `create_agent(llm, tools, system_message)`  |
| **工具定义**   | 直接操作Python对象                                 | 需先转为Document再存储                      |
| **查询灵活性** | ❌ 必须精确key或有限搜索                            | ✅ 自然语言模糊查询                          |
| **写入速度**   | **< 1ms**（内存）                                  | **50-200ms**（含Embedding）                 |
| **更新成本**   | **O(1)** 直接覆盖                                  | **O(n)** 需重新计算向量                     |
