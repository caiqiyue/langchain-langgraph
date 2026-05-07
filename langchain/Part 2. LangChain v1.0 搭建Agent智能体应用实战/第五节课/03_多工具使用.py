# -*- coding: utf-8 -*-
"""
【案例 3】多工具使用与工具分组
=================================

本案例展示如何组合使用多个工具，以及如何避免工具过多导致的上下文膨胀。

问题：
- 工具太多会导致 prompt 变长
- LLM 可能选错工具
- 需要智能路由机制

解决方案：
- 工具分组：按功能将工具分组
- 意图识别：根据用户问题先判断意图
- 动态加载：只加载需要的工具

要点：
1. 理解多工具场景下的挑战
2. 掌握工具分组策略
3. 理解意图识别路由机制
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
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

print("=" * 60)
print("案例 3: 多工具使用与智能路由")
print("=" * 60)

# ============================================================
# 3. 定义多组工具
# ============================================================

# --- 搜索工具组 ---
@tool
def search_news(query: str) -> str:
    """搜索新闻"""
    return f"新闻：关于'{query}'的最新报道..."

@tool
def search_wiki(query: str) -> str:
    """搜索维基百科"""
    return f"维基百科：'{query}'的条目内容..."

# --- 计算工具组 ---
@tool
def add(a: float, b: float) -> float:
    """加法计算"""
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """减法计算"""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """乘法计算"""
    return a * b

# --- 工具分组 ---
TOOL_GROUPS = {
    "search": [search_news, search_wiki],
    "calc": [add, subtract, multiply],
}

# ============================================================
# 4. 意图识别模型
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

INTENT_PROMPT = """你是一个意图分类器。

用户问题可能涉及：
- search：搜索新闻、百科等
- calc：数学计算
- none：闲聊或无需工具

请只返回类别名称：search / calc / none"""

def classify_intent(user_query: str) -> str:
    """识别用户意图"""
    result = model.invoke([
        ("system", INTENT_PROMPT),
        ("human", user_query)
    ])
    return result.content.strip()

# ============================================================
# 5. 意图路由函数
# ============================================================
def route_and_execute(user_query: str):
    """
    根据意图路由到对应的工具组
    """
    # 1. 识别意图
    intent = classify_intent(user_query)
    print(f"\n[路由] 识别意图: {intent}")

    # 2. 选择工具组
    if intent == "none":
        print(f"[路由] 无需工具，直接回答")
        response = model.invoke([
            ("human", user_query)
        ])
        return response.content

    if intent not in TOOL_GROUPS:
        return f"暂不支持处理 {intent} 类型的问题"

    tools = TOOL_GROUPS[intent]
    print(f"[路由] 加载工具: {[t.name for t in tools]}")

    # 3. 创建临时 Agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=f"你是一个{intent}助手，只使用提供的工具。"
    )

    # 4. 执行
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })

    return result["messages"][-1].content

# ============================================================
# 6. 测试路由
# ============================================================
print("\n" + "=" * 60)
print("测试意图路由")
print("=" * 60)

测试问题 = [
    ("搜索问题", "帮我搜索一下最新的AI新闻"),
    ("计算问题", "计算一下 25 加 30 等于多少"),
    ("闲聊问题", "今天天气真好"),
]

for qtype, question in 测试问题:
    print(f"\n{'='*50}")
    print(f"[{qtype}] {question}")
    answer = route_and_execute(question)
    print(f"回答: {answer}")

# ============================================================
# 7. 工具分组策略总结
# ============================================================
print("\n" + "=" * 60)
print("✅ 工具分组策略总结")
print("=" * 60)
print("""
问题场景：
• 工具太多 → prompt 膨胀 → 成本增加
• 选错工具 → 错误结果 → 用户不满

解决方案：工具分组 + 意图路由

┌─────────────────────────────────────────────────────────────┐
│                      用户问题                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
         ┌────────────────────────┐
         │     意图识别模型        │
         │  (判断需要哪类工具)      │
         └────────────────────────┬┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ↓                     ↓                     ↓
      [搜索组]              [计算组]              [无工具]
      search_news          add/subtract/mul        直接回答
      search_wiki
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 ↓
                      ┌────────────────────────┐
                      │    返回结果            │
                      └────────────────────────┘

优势：
1. 按需加载工具，减少 token 消耗
2. 降低选错工具的概率
3. 提高响应速度
""")