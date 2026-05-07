# -*- coding: utf-8 -*-
"""
【案例 2】StructuredTool.from_function() - 生产级工具定义
==========================================================

本案例展示如何使用 StructuredTool.from_function() 创建生产级工具。

与 @tool 装饰器相比，StructuredTool 提供了：
- Pydantic 模型进行参数验证
- 更完整的元数据配置
- 异步执行支持
- 更好的错误处理

适用场景：
- 生产环境工具开发
- 需要严格参数校验
- 异步操作需求
- 企业级应用

要点：
1. 理解 Pydantic 参数校验
2. 掌握 StructuredTool 的配置
3. 理解 return_direct 参数的作用
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
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

print("=" * 60)
print("案例 2: StructuredTool.from_function() - 生产级工具")
print("=" * 60)

# ============================================================
# 3. 定义 Pydantic 输入模型（参数校验）
# ============================================================

class DivideInput(BaseModel):
    """除法工具输入参数"""
    dividend: float = Field(description="被除数")
    divisor: float = Field(description="除数，不能为零")

class SearchInput(BaseModel):
    """搜索工具输入参数"""
    query: str = Field(description="搜索关键词，至少2个字符")
    max_results: int = Field(default=5, description="最大返回结果数，1-10之间")

# ============================================================
# 4. 定义工具函数
# ============================================================

def divide(dividend: float, divisor: float) -> float:
    """
    执行除法运算，支持浮点数。

    参数:
        dividend: 被除数
        divisor: 除数，不能为零

    返回:
        除法结果
    """
    if divisor == 0:
        raise ValueError("除数不能为零")
    return dividend / divisor

def web_search(query: str, max_results: int = 5) -> str:
    """
    执行网络搜索。

    参数:
        query: 搜索关键词
        max_results: 最大结果数

    返回:
        搜索结果列表
    """
    # 模拟搜索结果
    results = [
        f"结果{i+1}: 关于'{query}'的第{i+1}条相关信息..."
        for i in range(min(max_results, 5))
    ]
    return "\n".join(results)

# ============================================================
# 5. 创建 StructuredTool
# ============================================================

# 除法工具
divide_tool = StructuredTool.from_function(
    func=divide,
    name="divide",
    description="安全执行除法运算，自动处理除零错误",
    args_schema=DivideInput,  # 使用 Pydantic 模型
    return_direct=False,       # 结果经过 LLM 处理后返回
)

# 搜索工具
search_tool = StructuredTool.from_function(
    func=web_search,
    name="web_search",
    description="执行网络搜索，返回相关结果",
    args_schema=SearchInput,
    return_direct=True,        # 直接返回工具结果，不经过 LLM
)

# ============================================================
# 6. 查看工具信息
# ============================================================
print("\n" + "=" * 60)
print("工具信息")
print("=" * 60)

print(f"\n除法工具名称: {divide_tool.name}")
print(f"除法工具描述: {divide_tool.description}")
print(f"除法参数 Schema: {divide_tool.args_schema}")

print(f"\n搜索工具名称: {search_tool.name}")
print(f"搜索工具描述: {search_tool.description}")
print(f"搜索参数 Schema: {search_tool.args_schema}")

# ============================================================
# 7. 初始化模型并创建 Agent
# ============================================================
model = init_chat_model(
    model="qwen3-max",
    model_provider="qwen",
    temperature=0.7
)

agent = create_agent(
    model=model,
    tools=[divide_tool, search_tool],
    system_prompt="""你是一个精确的助手，善于处理数学计算和信息搜索。

使用指南：
1. 当用户要求计算时，使用 divide 工具
2. 当用户要求搜索时，使用 web_search 工具
3. 注意：除数不能为零
"""
)

# ============================================================
# 8. 测试参数校验
# ============================================================
print("\n" + "=" * 60)
print("测试参数校验")
print("=" * 60)

# 正确调用
print("\n1. 正确参数调用:")
结果 = divide_tool.invoke({"dividend": 10, "divisor": 2})
print(f"   divide(10, 2) = {结果}")

# 错误调用（参数校验）
print("\n2. 错误参数测试:")
try:
    # 尝试传入错误参数名（会触发校验）
    divide_tool.invoke({"a": 10, "b": 2})
except Exception as e:
    print(f"   参数校验生效: {type(e).__name__}")
    print(f"   错误信息: {str(e)[:80]}...")

# ============================================================
# 9. 测试 Agent 调用
# ============================================================
print("\n" + "=" * 60)
print("Agent 调用测试")
print("=" * 60)

问题1 = "请帮我计算 100 除以 5"
print(f"\n问题: {问题1}")
result1 = agent.invoke({"messages": [{"role": "user", "content": 问题1}]})
print(f"回答: {result1['messages'][-1].content}")

# ============================================================
# 10. return_direct 对比
# ============================================================
print("\n" + "=" * 60)
print("return_direct 参数对比")
print("=" * 60)
print("""
return_direct=False（默认）：
• 工具结果 → LLM 处理 → 自然语言回答
• 适用：需要 LLM 整合或润色的结果
• 示例：搜索结果 → LLM 总结成段落

return_direct=True：
• 工具结果 → 直接返回
• 适用：确定性格式数据（计算结果、ID等）
• 示例：计算结果 → 直接显示数字
""")

# ============================================================
# 11. StructuredTool 总结
# ============================================================
print("\n" + "=" * 60)
print("✅ StructuredTool 总结")
print("=" * 60)
print("""
与 @tool 装饰器对比：

┌─────────────┬──────────────────┬──────────────────┐
│  特性        │  @tool           │  StructuredTool  │
├─────────────┼──────────────────┼──────────────────┤
│  参数校验    │  弱（自动推断）   │  强（Pydantic）  │
│  异步支持    │  需单独定义       │  通过 coroutine  │
│  元数据      │  有限            │  完整            │
│  代码量      │  少              │  中等            │
│  适用场景    │  原型、测试      │  生产环境        │
└─────────────┴──────────────────┴──────────────────┘

生产环境建议：
1. 使用 Pydantic 模型明确定义参数
2. 合理设置 Field 的 description（LLM 靠它理解）
3. 善用 return_direct 控制返回方式
4. 考虑异步实现提升性能
""")