# -*- coding: utf-8 -*-
"""
【案例 3】langchain 主包 - create_agent
==========================================

本案例展示 langchain 主包的核心 API
create_agent 是创建智能体的核心函数

要点：
1. create_agent 的用法
2. Agent 的调用方式
3. Agent 执行结果的结构
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / ".env"
load_dotenv(env_path, override=True)

# 设置环境变量
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY", "")
os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 3: langchain 主包 - create_agent")
print("=" * 50)

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi

# ============================================================
# 1. 定义工具
# ============================================================
@tool
def get_weather(city: str) -> str:
    """查询城市天气

    Args:
        city: 城市名称

    Returns:
        天气信息字符串
    """
    weather_db = {
        "北京": "多云转晴，25°C",
        "上海": "小雨，22°C",
        "深圳": "晴天，28°C"
    }
    return weather_db.get(city, "暂无数据")

@tool
def calculate(expression: str) -> str:
    """执行数学计算

    Args:
        expression: 数学表达式，如 "2+3*4"

    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算错误"

# ============================================================
# 2. 创建 Agent
# ============================================================
print("\n2. 创建 Agent")
print("-" * 30)

model = ChatTongyi(model="qwen3-max", temperature=0.7)

# create_agent 的核心参数：
# - model: 智力来源（大语言模型）
# - tools: 能力扩展（工具列表）
agent = create_agent(
    model=model,
    tools=[get_weather, calculate]
)

print(f"Agent 类型: {type(agent)}")
print(f"Agent 可调用方法: {[m for m in dir(agent) if not m.startswith('_')][:5]}...")

# ============================================================
# 3. 调用 Agent
# ============================================================
print("\n3. 调用 Agent")
print("-" * 30)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "北京今天天气怎么样？顺便帮我计算 123 * 456"
    }]
})

print(f"结果类型: {type(result)}")
print(f"结果键: {result.keys()}")

print("\n消息历史:")
for msg in result["messages"]:
    # 获取消息类型（role）
    if hasattr(msg, 'type'):
        role = msg.type
    elif hasattr(msg, 'role'):
        role = msg.role
    else:
        role = type(msg).__name__

    # 获取消息内容
    if hasattr(msg, 'content'):
        content = msg.content
    else:
        content = str(msg)

    if content:
        preview = content[:50] + "..." if len(str(content)) > 50 else content
        print(f"  [{role}]: {preview}")

# ============================================================
# 【补充】create_agent 底层原理
# ============================================================
print("\n" + "=" * 50)
print("create_agent 底层原理")
print("=" * 50)
print("""
【create_agent 内部实现】

1. 将模型和工具绑定
   - 调用 model.bind_tools(tools)
   - 模型获得调用工具的能力

2. 创建 LangGraph StateGraph
   - nodes: 处理各个步骤
   - edges: 定义流程
   - state: 在步骤间传递数据

3. 配置消息处理逻辑
   - 自动处理 Function Calling
   - 循环直到得到最终回复

【为什么基于 LangGraph？】

因为 Agent 需要：
- 循环：思考 → 工具调用 → 观察结果 → 再思考
- 条件分支：需要工具吗？调用哪个？
- 状态管理：在步骤间传递数据

简单的 Chain 无法满足这些需求。
""")


"""
一、一句话先定性
在现代 LangChain（尤其 v1 以后）里：

Agent 的底层运行框架，基本就是 LangGraph
可以理解成：

LangChain = 上层开发接口
LangGraph = 底层任务编排引擎
二、你现在要理解：
什么叫“任务编排”
这是核心。

以前的 Chain 是什么？
最早 LangChain：

核心是：

Chain（链）
例如：

Prompt
↓
LLM
↓
Parser
线性执行。

类似：

step1()
step2()
step3()
但 Agent 不一样
Agent：

不是：

固定流程
而是：

动态流程
比如你的案例
用户：

北京天气怎么样？
顺便计算 123 * 456
Agent 需要：

第一步：思考
这个问题需要工具
第二步：决定调用哪个工具
get_weather
calculate
第三步：执行工具
第四步：获取结果
第五步：再思考
现在信息够了吗？
第六步：组织最终回答
这已经不是：

固定链式调用
了。

而是：

动态流程控制
三、这时候就需要“图”
所以：

LangGraph 出现了。

Graph（图）是什么？
不是：

A → B → C
这种线性。

而是：

A → B
A → C
B → D
C → D
D → A
可以：

循环

分支

条件跳转

状态流转

四、为什么 Agent 天然适合 Graph？
因为 Agent 本质：

就是：

“状态机”
它永远在：

思考
↓
行动
↓
观察
↓
再思考
循环。

这其实就是：

Graph Loop
五、create_agent 底层真正发生了什么？
你这里：

agent = create_agent(
    model=model,
    tools=[...]
)
实际上：

LangChain 内部：

大概会：

1. bind_tools
model.bind_tools(tools)
让模型支持：

Function Calling
2. 创建 Graph
内部：

大概类似：

START
  ↓
LLM Node
  ↓
是否需要工具？
 ├─ 否 → END
 └─ 是 → Tool Node
             ↓
         回到 LLM Node
这就是：

LangGraph StateGraph
六、什么是 StateGraph？
这是：

LangGraph 最核心的概念。

State
就是：

整个运行状态
例如：

{
    "messages": [...],
    "tool_results": [...],
    "current_step": ...
}
Graph
表示：

状态如何流动
七、你案例里的 state 是什么？
最核心：

就是：

messages
因为：

Agent 整个过程：

都在不断往：

messages
里追加内容。

例如：

用户消息
北京天气？
AI Tool Call
调用 get_weather
Tool Result
多云 25℃
AI Final Answer
北京今天多云...
所以：

整个 Agent：

本质就是：

状态不断演化
八、为什么 Chain 不够？
这是关键。

Chain：
只能：

固定顺序
但 Agent 需要：

能力	Chain	Graph
循环	❌	✅
条件判断	很弱	✅
多工具路由	很弱	✅
状态管理	一般	✅
多 Agent 协作	几乎不行	✅
九、所以现在 LangChain 官方路线已经变了
以前：

LangChain = 主体
现在：

官方实际上：

已经逐渐变成：

LangGraph = 核心底层
LangChain = 上层封装
十、你现在可以这样理解生态
LangChain
负责：

开发体验
例如：

PromptTemplate

Tool

OutputParser

create_agent

属于：

高层 API
LangGraph
负责：

任务编排 + 状态流转
属于：

运行时引擎
十一、最关键的一句话
你现在这个理解：

“Agent 本质上是一个带状态的循环图”
而：

LangGraph
就是：

专门执行这种图的框架
十二、所以 create_agent 本质是什么？
本质上：

是：

“帮你自动生成一个 LangGraph”
你写：

create_agent(...)
实际上相当于：

自动生成：
- graph node
- edge
- state
- loop
- tool routing
十三、为什么很多高级 Agent 都直接用 LangGraph？
因为：

create_agent：

虽然方便。

但：

太自动化了。
复杂场景：

比如：

多 Agent 协同

Planner-Executor

Reflection

Memory

Human-in-the-loop

需要：

自己控制图结构
所以高级开发：

会直接：

from langgraph.graph import StateGraph
自己搭图。

十四、你现在最应该真正理解的一层
很多人误以为：

Agent = 大模型
其实完全不是。

Agent 真正的本质是：
LLM + 状态机 + 工具调度 + 流程控制
而：

LangGraph
负责的就是：

状态机 + 流程控制
十五、最后一句话总结整个关系
你可以直接记：

层级	作用
LLM	负责“思考”
Tool	负责“行动”
LangGraph	负责“任务编排”
LangChain	负责“开发封装”
create_agent	自动帮你生成 LangGraph Agent
所以：

现代 LangChain 的 Agent，本质上基本都跑在 LangGraph 之上。



"""