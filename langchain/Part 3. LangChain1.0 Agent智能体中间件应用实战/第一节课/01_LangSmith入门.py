# -*- coding: utf-8 -*-
"""
【案例 1】LangSmith 入门 - Agent 可观测性平台
================================================

LangSmith 是 LangChain 的监控平台，提供：
- Trace：端到端追踪
- Run：单次执行节点
- Feedback：质量评估

要点：
1. 配置 LangSmith 环境变量
2. 创建第一个追踪项目
3. 查看 Trace 和 Run 数据
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ============================================================
# 2. 配置 LangSmith
# ============================================================
# 设置 LangSmith API Key
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "your-api-key")
os.environ["LANGSMITH_PROJECT"] = "agent-middleware-demo"

print("=" * 60)
print("案例 1: LangSmith 入门")
print("=" * 60)

# ============================================================
# 3. LangSmith 核心概念
# ============================================================
print("""
LangSmith 核心概念：

┌─────────────────────────────────────────────────────────────┐
│                      LangSmith 层级                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Project (项目)                                             │
│  ├── Trace (追踪)：端到端的完整请求链路                      │
│  │   └── Run (运行)：单个节点/步骤的执行记录                 │
│  │       ├── metadata：执行元数据                           │
│  │       ├── logs：日志                                    │
│  │       └── feedback：质量反馈                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

层级关系：Project > Trace > Run > Feedback
""")

# ============================================================
# 4. 简单示例：追踪 Agent 执行
# ============================================================
print("\n" + "=" * 60)
print("追踪示例：Agent 执行")
print("=" * 60)

# 由于没有实际 API Key，这里演示代码结构
示例代码 = """
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    '''查询天气'''
    return f"{city}：晴天，25°C"

# 创建 Agent（自动被 LangSmith 追踪）
agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    system_prompt="你是天气助手"
)

# 执行（所有操作都会被追踪）
result = agent.invoke({
    "messages": [{"role": "user", "content": "北京天气怎么样？"}]
})

# 查看追踪结果
# 访问 https://smith.langchain.com/projects 查看 Traces
"""

print(示例代码)

# ============================================================
# 5. Feedback 使用
# ============================================================
print("\n" + "=" * 60)
print("Feedback 使用：质量评估")
print("=" * 60)

feedback_示例 = """
# 为 Run 添加 Feedback
from langchain.smith import feedback

# 方式1：基于分数
feedback.log(
    run_id="run_id_here",
    score=0.9,
    comment="回答质量不错"
)

# 方式2：基于标签
feedback.tag(
    run_id="run_id_here",
    tags=["准确", "完整"]
)
"""

print(feedback_示例)

# ============================================================
# 6. 总结
# ============================================================
print("""
✅ LangSmith 使用总结

配置步骤：
1. 注册 LangSmith (smith.langchain.com)
2. 创建 API Key
3. 设置环境变量：
   LANGCHAIN_TRACING_V2=true
   LANGSMITH_API_KEY=your-api-key
   LANGSMITH_PROJECT=your-project

用途：
- 调试 Agent 执行流程
- 分析性能瓶颈
- 评估输出质量
- 优化提示词
""")