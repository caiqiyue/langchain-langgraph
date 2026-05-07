# -*- coding: utf-8 -*-
"""
【案例 1】多 Agent 协作 - 层次化 Agent 架构
==============================================

本案例展示如何构建多 Agent 协作系统。

多 Agent 架构适用于：
- 复杂任务需要多种能力
- 需要专业化分工
- 单一 Agent 工具过多导致选错

架构示例：
┌─────────────────────────────────────────────────────┐
│                  Router Agent (路由)                  │
│   负责：理解用户意图，分发到子 Agent                   │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ↓             ↓             ↓             ↓
   [搜索Agent]  [计算Agent]  [天气Agent]  [邮件Agent]
   专门搜索     专门计算    专门查天气   专门发邮件

要点：
1. 理解多 Agent 架构的适用场景
2. 掌握路由 Agent 的设计
3. 理解专业化分工的优势
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

print("=" * 60)
print("案例 1: 多 Agent 协作 - 层次化架构")
print("=" * 60)

# ============================================================
# 3. 定义子 Agent 的工具
# ============================================================

# --- 搜索 Agent 工具 ---
@tool
def search_info(query: str) -> str:
    """搜索信息"""
    return f"搜索结果：关于'{query}'的信息已找到..."

# --- 计算 Agent 工具 ---
@tool
def calculate_expr(expr: str) -> str:
    """执行计算"""
    try:
        return f"计算结果：{expr} = {eval(expr)}"
    except:
        return "计算表达式无效"

# --- 天气 Agent 工具 ---
@tool
def get_weather(city: str) -> str:
    """查询天气"""
    weather = {"北京": "晴天25°C", "上海": "多云28°C"}
    return weather.get(city, f"{city}：天气未知")

# ============================================================
# 4. 初始化模型
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

# ============================================================
# 5. 创建专业化子 Agent
# ============================================================

# 搜索 Agent
search_agent = create_agent(
    model=model,
    tools=[search_info],
    system_prompt="你是一个专业的搜索助手，只负责搜索信息。"
)

# 计算 Agent
calc_agent = create_agent(
    model=model,
    tools=[calculate_expr],
    system_prompt="你是一个专业的计算助手，只负责数学计算。"
)

# 天气 Agent
weather_agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="你是一个专业的天气助手，只负责查询天气。"
)

# ============================================================
# 6. 创建路由 Agent（主控）
# ============================================================

# 路由 Agent 的工具：调用子 Agent
@tool
def call_search_agent(query: str) -> str:
    """调用搜索 Agent"""
    result = search_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content

@tool
def call_calc_agent(expr: str) -> str:
    """调用计算 Agent"""
    result = calc_agent.invoke({
        "messages": [{"role": "user", "content": f"计算：{expr}"}]
    })
    return result["messages"][-1].content

@tool
def call_weather_agent(city: str) -> str:
    """调用天气 Agent"""
    result = weather_agent.invoke({
        "messages": [{"role": "user", "content": f"查询{city}的天气"}]
    })
    return result["messages"][-1].content

# 路由 Agent
router_agent = create_agent(
    model=model,
    tools=[call_search_agent, call_calc_agent, call_weather_agent],
    system_prompt="""你是一个智能路由助手，负责将用户请求分发到专业 Agent。

能力：
- search_agent：搜索信息
- calc_agent：执行计算
- weather_agent：查询天气

根据用户问题，选择合适的 Agent 来处理。"""
)

# ============================================================
# 7. 测试多 Agent 协作
# ============================================================
print("\n" + "=" * 60)
print("测试多 Agent 协作")
print("=" * 60)

问题 = "帮我搜索一下最新的AI新闻，然后计算一下 25 加 30，再查一下北京天气"
print(f"\n用户问题: {问题}")

result = router_agent.invoke({
    "messages": [{"role": "user", "content": 问题}]
})

print(f"\n回答: {result['messages'][-1].content}")

# ============================================================
# 8. 多 Agent 架构总结
# ============================================================
print("\n" + "=" * 60)
print("✅ 多 Agent 协作架构总结")
print("=" * 60)
print("""
多 Agent 架构优势：

1. 【专业化分工】
   • 每个子 Agent 专注于特定领域
   • 工具描述更清晰，调用更准确

2. 【降低复杂度】
   • 单个 Agent 工具数量减少
   • 降低选错工具的概率

3. 【可扩展性】
   • 新增能力只需添加子 Agent
   • 路由 Agent 不需要修改

架构建议：
┌─────────────────────────────────────────────────────────────┐
│                    Router Agent                              │
│   只负责理解意图和路由，不直接执行                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │搜索Agent│  │计算Agent│  │天气Agent│
   │ 只搜索  │  │ 只计算  │  │ 只查天气│
   └─────────┘  └─────────┘  └─────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
              返回结果给用户
""")