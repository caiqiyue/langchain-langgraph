# -*- coding: utf-8 -*-
"""
【案例 1】Agent 架构解析 - 理解 Agent 的五大核心模块
=====================================================

Agent 的技术架构由五个核心模块构成，形成完整的"感知-思考-行动"闭环。

┌─────────────────────────────────────────────────────────────────┐
│                         Agent 系统                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                               │
│  │ 感知模块     │ ← 接收用户输入、工具返回                        │
│  │ Perception  │   支持文本、图像、语音等多模态                   │
│  └──────┬──────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │ 认知中枢    │ ← LLM 推理引擎                                │
│  │ Brain      │   思考、规划、决策                             │
│  └──────┬──────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │ 记忆系统    │ ← 短期+长期记忆                                │
│  │ Memory     │   对话历史、知识库                             │
│  └──────┬──────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │ 工具生态    │ ← API调用、数据库、搜索                        │
│  │ Tools      │   扩展 Agent 能力                              │
│  └──────┬──────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │ 执行引擎    │ ← 任务执行、结果反馈                          │
│  │ Action     │   影响环境、返回结果                          │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

要点：
1. 理解每个模块的作用
2. 理解模块之间的协作关系
3. 理解 LangChain 中每个模块的代码实现
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# 2. 导入 LangChain 核心组件
# ============================================================
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

print("=" * 60)
print("案例 1: Agent 架构解析 - 五大核心模块")
print("=" * 60)

# ============================================================
# 3. 各模块的代码实现
# ============================================================

print("\n" + "=" * 60)
print("模块 1: 感知模块 (Perception)")
print("=" * 60)
print("""
感知模块负责接收和处理输入：
- 用户消息 (HumanMessage)
- 工具返回结果 (ToolMessage)
- 系统指令 (SystemMessage)

在 LangChain 中，消息是最基本的感知单元。
""")

# 定义感知模块：接收用户输入
感知模块 = HumanMessage(content="帮我查询北京的天气")
print(f"感知输入示例: {感知模块.content}")

print("\n" + "=" * 60)
print("模块 2: 认知中枢 (Brain)")
print("=" * 60)
print("""
认知中枢是 Agent 的"大脑"，基于 LLM 实现：
- 理解用户意图
- 制定执行计划
- 决策下一步行动

在 LangChain 中，通过 init_chat_model() 初始化 LLM。
""")

# 初始化认知中枢：大模型
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)
print(f"认知中枢已初始化: {type(model).__name__}")

# 模拟认知过程：LLM 分析问题
认知结果 = model.invoke([
    ("human", "用户问天气，AI应该如何回应？")
])
print(f"认知过程示例: {认知结果.content[:100]}...")

print("\n" + "=" * 60)
print("模块 3: 记忆系统 (Memory)")
print("=" * 60)
print("""
记忆系统存储历史信息和知识：
- 短期记忆：对话历史，维持上下文
- 长期记忆：向量数据库，跨会话持久化

在 LangChain 中，通过 checkpointer 和 store 实现。
""")

# 初始化记忆系统
memory = InMemorySaver()
print(f"短期记忆已配置: {type(memory).__name__}")

# 模拟存储记忆
工具结果示例 = {"weather": "北京：晴朗，25°C"}
print(f"工具结果存入记忆: {工具结果示例}")

print("\n" + "=" * 60)
print("模块 4: 工具生态 (Tools)")
print("=" * 60)
print("""
工具生态扩展 Agent 的执行能力：
- 搜索工具：获取实时信息
- 计算工具：执行数学运算
- API工具：调用外部系统

在 LangChain 中，通过 @tool 装饰器定义工具。
""")

# 定义工具
@tool
def search_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city}：晴朗，25°C"

@tool
def calculator(expression: str) -> str:
    """执行计算"""
    return f"结果：{eval(expression)}"

工具列表 = [search_weather, calculator]
print(f"工具生态已配置: {[t.name for t in 工具列表]}")

print("\n" + "=" * 60)
print("模块 5: 执行引擎 (Action)")
print("=" * 60)
print("""
执行引擎负责：
- 调用工具
- 处理返回结果
- 生成最终响应

在 LangChain 中，create_agent() 整合所有模块。
""")

# 创建完整的 Agent（整合所有模块）
agent = create_agent(
    model=model,
    tools=工具列表,
    checkpointer=memory,
    system_prompt="你是智能助手，可以查询天气和计算。"
)

print(f"执行引擎已配置: Agent with {len(工具列表)} tools")

# ============================================================
# 4. 完整流程演示
# ============================================================
print("\n" + "=" * 60)
print("完整流程演示：用户问天气")
print("=" * 60)

config = {"configurable": {"thread_id": "architecture_demo"}}

流程 = """
用户输入"北京天气怎么样？"

Step 1: 感知模块接收 → HumanMessage("北京天气怎么样？")
Step 2: 认知中枢分析 → LLM 判断：需要调用天气工具
Step 3: 记忆系统查询 → 检查对话历史
Step 4: 工具生态执行 → 调用 search_weather(city="北京")
Step 5: 执行引擎反馈 → 工具返回："北京：晴朗，25°C"
Step 6: 认知中枢整合 → LLM 生成自然语言回答
Step 7: 感知模块输出 → AIMessage("北京今天天气晴朗，气温25°C")
"""
print(流程)

# 实际执行
result = agent.invoke({
    "messages": [{"role": "user", "content": "北京天气怎么样？"}]
}, config=config)

print(f"\n实际执行结果: {result['messages'][-1].content}")

# ============================================================
# 5. 架构总结
# ============================================================
print("\n" + "=" * 60)
print("✅ Agent 五大模块总结")
print("=" * 60)
print("""
┌─────────────────────────────────────────────────────────────┐
│                    LangChain 中的对应实现                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  感知模块 → HumanMessage / ToolMessage / SystemMessage      │
│  认知中枢 → init_chat_model() / LLM                       │
│  记忆系统 → InMemorySaver / PostgresSaver / VectorStore    │
│  工具生态 → @tool / StructuredTool / ToolNode             │
│  执行引擎 → create_agent() / LangGraph                    │
│                                                             │
│  感知 ← 输入   认知 ← 思考   记忆 ← 存储                    │
│  工具 ← 执行   引擎 ← 协调                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
""")