# -*- coding: utf-8 -*-
"""
【案例 6】LLMToolSelectorMiddleware - 智能工具选择中间件
==========================================================

本案例展示如何使用 LLMToolSelectorMiddleware 智能选择最相关的工具，
当 Agent 拥有大量工具时，自动筛选出最相关的工具子集。

核心特性：
1. 智能工具筛选：使用 LLM 分析查询并选择工具
2. 减少 Token 消耗：只传递相关工具描述
3. 提高准确性：帮助主模型聚焦正确工具
4. 灵活配置：支持限制数量、指定必选工具

要点：
1. 理解工具选择对性能的影响
2. 掌握 max_tools 和 always_include 配置
3. 理解 Token 节省的原理
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
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware
from langchain_core.tools import tool
from pydantic import BaseModel, Field

print("=" * 60)
print("案例 6: LLMToolSelectorMiddleware 智能工具选择")
print("=" * 60)

# ============================================================
# 3. 定义多个工具（模拟大量工具场景）
# ============================================================
@tool
def search_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    return f"{city}的天气：晴天，温度25°C，湿度60%"

@tool
def search_news(topic: str) -> str:
    """搜索指定主题的最新新闻"""
    return f"关于'{topic}'的最新新闻..."

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式的结果"""
    return f"计算结果: {expression}"

@tool
def translate_text(text: str, target_lang: str) -> str:
    """将文本翻译成目标语言"""
    return f"翻译结果: [模拟翻译到{target_lang}]"

@tool
def search_database(query: str) -> str:
    """在数据库中搜索信息"""
    return f"数据库搜索结果: 找到3条关于'{query}'的记录"

@tool
def send_email(recipient: str, subject: str) -> str:
    """发送电子邮件"""
    return f"邮件已发送给 {recipient}"

@tool
def get_stock_price(symbol: str) -> str:
    """获取股票价格"""
    return f"股票 {symbol} 当前价格: $150.25"

@tool
def book_meeting(date: str, time: str) -> str:
    """预订会议室"""
    return f"会议室已预订: {date} {time}"

# 所有工具列表（8个工具）
all_tools = [
    search_weather, search_news, calculate_math,
    translate_text, search_database, send_email,
    get_stock_price, book_meeting
]

# ============================================================
# 4. 定义上下文 Schema
# ============================================================
class UserContext(BaseModel):
    """用户上下文"""
    user_id: str = Field(..., description="用户唯一标识")

# ============================================================
# 5. 配置 LLMToolSelectorMiddleware
# ============================================================
print("\n【中间件配置】")
print("-" * 50)

tool_selector_middleware = LLMToolSelectorMiddleware(
    model=ChatDeepSeek(model="deepseek-chat", temperature=0.1),
    max_tools=3,  # 最多选择 3 个工具
    always_include=["calculate_math"],  # 始终包含计算工具
    system_prompt="分析用户查询，选择最相关的工具。"
)

print(f"总工具数: {len(all_tools)} 个")
print(f"最多选择: max_tools=3 个")
print(f"必选工具: always_include=['calculate_math']")
print(f"选择模型: deepseek-chat (用于分析查询)")

# ============================================================
# 6. 工作原理图示
# ============================================================
print("\n" + "=" * 60)
print("工作原理")
print("=" * 60)

print("""
【工具选择流程】

用户查询: "北京今天的天气怎么样？"
    │
    ▼
┌─────────────────────────────────┐
│  LLMToolSelectorMiddleware      │
│  (before_model 阶段)            │
│                                 │
│  1. 发送查询到选择模型           │
│  2. 选择模型分析:               │
│     - search_weather: 高相关    │
│     - calculate_math: 低相关    │
│     - 其他工具: 不相关          │
│  3. 返回工具列表:               │
│     [search_weather,           │
│      calculate_math(必选)]     │
└─────────────────────────────────┘
    │
    ▼
【主模型接收】（只看到选中的工具）
┌─────────────────────────────────┐
│ tools = [search_weather,       │
│          calculate_math]        │
│ (而不是全部 8 个工具)            │
└─────────────────────────────────┘
""")

# ============================================================
# 7. Token 节省效果
# ============================================================
print("\n【Token 节省效果】")
print("-" * 50)

节省效果 = """
| 指标         | 未使用中间件   | 使用中间件    | 节省     |
|-------------|--------------|-------------|---------|
| 工具数量     | 8 个         | 2-3 个      | 70%+    |
| 工具描述Tokens | ~2000      | ~500        | 75%     |
| API 成本     | $1.00        | $0.25       | 75%     |
"""
print(节省效果)

print("\n【适用场景】")
print("-" * 50)
print("""
LLMToolSelectorMiddleware 特别适合：
  1. 工具数量众多（>10个）的 Agent
  2. 成本敏感的应用
  3. 需要精确控制工具选择的场景
  4. 复杂多领域助手（如 IT 运维 + 客服）

不适用的场景：
  1. 工具数量少（<5个）- 额外选择开销不划算
  2. 需要每次都使用所有工具的场景
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)