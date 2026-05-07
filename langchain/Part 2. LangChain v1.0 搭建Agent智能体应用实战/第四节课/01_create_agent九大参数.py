# -*- coding: utf-8 -*-
"""
【案例 1】create_agent 九大参数详解
=====================================

本案例详细介绍 create_agent 的所有参数，帮助你掌握 Agent 的配置方法。

参数分类：
┌─────────────────────────────────────────────────────────────┐
│                     create_agent 参数                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【必填参数】                                                │
│  ──────────                                                │
│  model   - 推理引擎，决定 Agent 的"智力水平"                 │
│  tools   - 工具列表，决定 Agent 的"能力范围"                │
│                                                             │
│  【行为控制】                                                │
│  ──────────                                                │
│  system_prompt   - Agent 的"人格说明书"                     │
│  middleware      - 功能扩展（日志、安全、压缩）              │
│  response_format - 结构化输出格式                           │
│                                                             │
│  【状态管理】                                                │
│  ──────────                                                │
│  checkpointer    - 短期记忆（会话级）                       │
│  store           - 长期记忆（跨会话）                       │
│  state_schema    - 自定义状态结构                          │
│  context_schema  - 动态上下文结构                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

要点：
1. 理解每个参数的用途
2. 掌握参数的最佳实践
3. 学会根据场景配置 Agent
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# 2. 导入核心组件
# ============================================================
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field
from typing import TypedDict

print("=" * 60)
print("案例 1: create_agent 九大参数详解")
print("=" * 60)

# ============================================================
# 3. 准备工具和数据
# ============================================================
@tool
def get_weather(city: str) -> str:
    """查询城市天气"""
    weather = {"北京": "晴天，25°C", "上海": "多云，28°C"}
    return weather.get(city, f"{city}：天气未知")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        return f"结果：{eval(expression)}"
    except:
        return "计算错误"

tools = [get_weather, calculate]

# 初始化模型
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# ============================================================
# 4. 参数 1-2: model 和 tools（必填）
# ============================================================
print("\n" + "=" * 60)
print("参数 1-2: model 和 tools（必填）")
print("=" * 60)
print("""
【model】推理引擎
──────────────────
• 类型：str 或 LLM 实例
• 作用：Agent 的"大脑"，负责思考、推理、决策
• 建议：生产环境使用实例化配置

【tools】工具列表
──────────────────
• 类型：list[BaseTool]
• 作用：Agent 的"能力装备"，决定能做什么
• 注意：工具描述（description）是 LLM 选择工具的依据
""")

# 基础配置
agent_basic = create_agent(
    model=model,      # 指定模型
    tools=tools      # 工具列表
)
print("✅ 基础 Agent 创建成功")

# ============================================================
# 5. 参数 3: system_prompt（行为准则）
# ============================================================
print("\n" + "=" * 60)
print("参数 3: system_prompt（系统提示词）")
print("=" * 60)
print("""
【system_prompt】Agent 的人格说明书
──────────────────────────────────────
• 类型：str
• 作用：定义 Agent 的角色、行为准则、输出格式
• 最佳实践：
  - 明确角色（如"你是客服助手"）
  - 规定行为（如"回答不超过50字"）
  - 说明约束（如"不知道就说不知道"）
""")

agent_with_prompt = create_agent(
    model=model,
    tools=tools,
    system_prompt="""你是一个简洁的天气和计算助手。

行为准则：
1. 回答要简洁，不超过30字
2. 如果不知道答案，说"暂不支持"
3. 使用工具时，说明你在做什么
"""
)
print("✅ 带系统提示词的 Agent 创建成功")

# ============================================================
# 6. 参数 4: middleware（功能扩展）
# ============================================================
print("\n" + "=" * 60)
print("参数 4: middleware（中间件）")
print("=" * 60)
print("""
【middleware】功能扩展
──────────────────────
• 类型：list[Middleware]
• 作用：在 Agent 执行过程中插入额外功能
• 常见用途：
  - 日志记录（LangChainTracingMiddleware）
  - 安全检查（PIIDetectionMiddleware）
  - 人工介入（HumanApprovalMiddleware）
  - 上下文压缩（ContextCompressionMiddleware）
""")

# 创建一个简单的日志中间件示例
def log_middleware(request, response):
    """日志中间件示例"""
    print(f"[日志] 请求: {request.messages[-1].content[:50]}...")
    print(f"[日志] 响应: {response.messages[-1].content[:50]}...")

# agent_with_middleware = create_agent(
#     model=model,
#     tools=tools,
#     middleware=[log_middleware]
# )
print("⚠️ 中间件功能需要额外配置（详见第五阶段中间件课程）")

# ============================================================
# 7. 参数 5: checkpointer（短期记忆）
# ============================================================
print("\n" + "=" * 60)
print("参数 5: checkpointer（短期记忆）")
print("=" * 60)
print("""
【checkpointer】短期记忆
──────────────────────────
• 类型：MemorySaver / PostgresSaver
• 作用：保存对话历史，实现多轮对话连贯
• 特点：
  - InMemorySaver：内存存储，重启丢失
  - PostgresSaver：数据库存储，持久化
• 关键：需要配合 thread_id 使用
""")

memory = InMemorySaver()
agent_with_memory = create_agent(
    model=model,
    tools=tools,
    checkpointer=memory
)
print("✅ 带短期记忆的 Agent 创建成功")

# 演示记忆效果
config = {"configurable": {"thread_id": "test_001"}}
result1 = agent_with_memory.invoke({
    "messages": [{"role": "user", "content": "我叫李明"}]
}, config=config)
result2 = agent_with_memory.invoke({
    "messages": [{"role": "user", "content": "你还记得我叫什么吗？"}]
}, config=config)
print(f"第二轮回答: {result2['messages'][-1].content}")

# ============================================================
# 8. 参数 6: store（长期记忆）
# ============================================================
print("\n" + "=" * 60)
print("参数 6: store（长期记忆）")
print("=" * 60)
print("""
【store】长期记忆
──────────────────
• 类型：BaseStore 实现（如 PostgresStore）
• 作用：跨会话持久化存储
• 与 checkpointer 的区别：
  - checkpointer：保存对话历史
  - store：保存用户信息、偏好等结构化数据
• 适用场景：需要跨会话记住用户信息的应用
""")

print("⚠️ 长期记忆需要数据库配置（详见第六节课）")

# ============================================================
# 9. 参数 7: state_schema（自定义状态）
# ============================================================
print("\n" + "=" * 60)
print("参数 7: state_schema（自定义状态）")
print("=" * 60)
print("""
【state_schema】自定义状态
────────────────────────────
• 类型：TypedDict 或 Pydantic BaseModel
• 作用：扩展 Agent 的状态结构
• 用途：
  - 传递用户 ID、偏好等业务数据
  - 实现复杂的状态流转
• 推荐：使用 TypedDict（性能更高）
""")

class CustomState(TypedDict):
    messages: list
    user_id: str
    preferences: dict

agent_with_state = create_agent(
    model=model,
    tools=tools,
    state_schema=CustomState
)
print("✅ 带自定义状态的 Agent 创建成功")

# ============================================================
# 10. 参数 8: context_schema（动态上下文）
# ============================================================
print("\n" + "=" * 60)
print("参数 8: context_schema（动态上下文）")
print("=" * 60)
print("""
【context_schema】动态上下文
─────────────────────────────
• 类型：TypedDict
• 作用：在运行时传入动态数据
• 与 state_schema 的区别：
  - state_schema：定义状态结构
  - context_schema：传入具体值
• 典型用途：传入用户角色、权限等信息
""")

class Context(TypedDict):
    user_role: str
    department: str

# agent_with_context = create_agent(
#     model=model,
#     tools=tools,
#     context_schema=Context
# )
print("⚠️ 动态上下文需要配合 middleware 使用")

# ============================================================
# 11. 参数 9: response_format（结构化输出）
# ============================================================
print("\n" + "=" * 60)
print("参数 9: response_format（结构化输出）")
print("=" * 60)
print("""
【response_format】结构化输出
───────────────────────────────
• 类型：Pydantic BaseModel
• 作用：指定 Agent 输出的格式
• 适用场景：
  - API 返回标准化格式
  - 需要程序化处理响应
  - 多 Agent 系统协作
""")

class ResponseModel(BaseModel):
    """标准化响应格式"""
    status: str = Field(description="状态：success 或 error")
    data: str = Field(description="返回数据")
    message: str = Field(description="说明信息")

agent_with_format = create_agent(
    model=model,
    tools=tools,
    response_format=ResponseModel
)
print("✅ 带结构化输出的 Agent 创建成功")

# ============================================================
# 12. 完整配置示例
# ============================================================
print("\n" + "=" * 60)
print("完整配置示例")
print("=" * 60)
print("""
create_agent(
    model=model,                    # 必填：推理引擎
    tools=[search_tool, calc],      # 必填：工具列表
    system_prompt="你是客服助手",   # 行为准则
    middleware=[log_mw],            # 功能扩展
    checkpointer=memory,            # 短期记忆
    store=store,                    # 长期记忆
    state_schema=CustomState,       # 自定义状态
    context_schema=Context,         # 动态上下文
    response_format=ResponseModel   # 结构化输出
)
""")

# ============================================================
# 13. 参数配置最佳实践
# ============================================================
print("\n" + "=" * 60)
print("✅ create_agent 参数配置最佳实践")
print("=" * 60)
print("""
1. 【必填参数】
   • model：生产环境使用实例化配置
   • tools：工具描述要清晰、准确

2. 【行为控制】
   • system_prompt：简洁明了，具体化
   • middleware：按需添加，不要过度封装

3. 【状态管理】
   • checkpointer：必须配置，实现多轮对话
   • store：需要跨会话记忆时配置

4. 【性能优化】
   • state_schema：优先使用 TypedDict
   • context_schema：只在需要时使用

5. 【常见错误】
   • 不配置 checkpointer：每次都是新对话
   • 工具描述模糊：LLM 无法正确选择工具
   • system_prompt 太长：影响推理质量
""")