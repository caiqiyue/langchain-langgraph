# -*- coding: utf-8 -*-
"""
【案例 4】persist_session - 会话持久化中间件
=============================================

本案例展示如何使用 persist_session 中间件实现会话自动持久化，
将 Agent 的执行状态保存到本地存储。

核心特性：
1. 自动保存：在 after_model 钩子中自动保存
2. 简单易用：轻量级包装器
3. 可自定义路径：指定保存目录
4. 格式灵活：JSON 序列化

使用场景：
- 会话恢复：用户关闭浏览器后重新打开
- 审计追踪：记录所有对话历史
- 分析统计：分析用户对话模式

要点：
1. 理解会话持久化的重要性
2. 掌握 PersistSessionMiddleware 的实现
3. 理解 after_model 钩子的用法
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
from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import HumanMessage

print("=" * 60)
print("案例 4: persist_session 会话持久化")
print("=" * 60)

# ============================================================
# 3. PersistSessionMiddleware 实现
# ============================================================
print("\n【PersistSessionMiddleware 实现】")
print("-" * 50)

print("""
import os
import json
import time
from typing import Dict, Any

class PersistSessionMiddleware(AgentMiddleware):
    '''
    会话持久化中间件
    在 after_model 钩子中自动保存会话状态
    '''

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        os.makedirs(path, exist_ok=True)

    def after_model(self, state: AgentState, runtime) -> None:
        '''
        在模型调用后保存会话
        '''
        timestamp = int(time.time())
        messages = state.get("messages", [])
        if not messages:
            return

        # 序列化为 JSON
        serialized_msgs = []
        for msg in messages:
            msg_data = {
                "role": msg.type,
                "content": msg.content
            }
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg_data['tool_calls'] = msg.tool_calls
            serialized_msgs.append(msg_data)

        # 保存到文件
        filename = os.path.join(self.path, f"state_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(serialized_msgs, f, ensure_ascii=False, indent=2)

        print(f"会话已保存: {filename}")


def persist_session(path: str = "./sessions"):
    '''
    persist_session 轻量包装器
    '''
    return PersistSessionMiddleware(path)
""")

# ============================================================
# 4. AgentState 结构
# ============================================================
print("\n【AgentState 结构】")
print("-" * 50)

print("""
AgentState 是传递给 after_model 的状态对象，包含：

{
    'messages': [
        HumanMessage(content='用户输入...'),
        AIMessage(content='AI回答...', response_metadata={...}),
        ToolMessage(content='工具结果...')
    ],
    'user_info': {...},        # 可由 before_model 注入
    'permissions': [...],      # 可由 before_model 注入
    'checkpoint': 'xxx'       # 用于状态恢复
}

注意：
- after_model 中只能读取 state，不能修改
- 如果需要修改，应该在 before_model 或 wrap_model_call 中处理
""")

# ============================================================
# 5. 完整使用示例
# ============================================================
print("\n" + "=" * 60)
print("完整使用示例")
print("=" * 60)

print("""
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 1. 创建中间件
session_persister = persist_session(path="./my_agent_sessions")

# 2. 创建 Agent
agent = create_agent(
    model=ChatOpenAI(model="gpt-4o-mini"),
    tools=[],
    middleware=[session_persister]
)

# 3. 执行对话
print(">>> 开始对话...")

await agent.ainvoke({
    "messages": [HumanMessage(content="你好，请介绍一下自己")]
})

# 4. 检查保存的文件
# ls ./my_agent_sessions/
# state_1700000000.json
""")

# ============================================================
# 6. 保存的 JSON 结构
# ============================================================
print("\n【保存的 JSON 结构】")
print("-" * 50)

print("""
{
  "messages": [
    {
      "role": "human",
      "content": "你好，请介绍一下自己"
    },
    {
      "role": "ai",
      "content": "你好！我是...",
      "response_metadata": {
        "token_usage": {...},
        "model_name": "gpt-4o-mini"
      }
    }
  ]
}
""")

# ============================================================
# 7. 高级用法：自定义序列化
# ============================================================
print("\n【高级用法】")
print("-" * 50)

print("""
# 保存更多元数据
def after_model(self, state: AgentState, runtime) -> None:
    serialized = {
        "messages": self.serialize_messages(state["messages"]),
        "user_info": state.get("user_info", {}),
        "timestamp": int(time.time()),
        "runtime_context": dict(runtime.context) if runtime.context else {}
    }

    filename = os.path.join(self.path, f"session_{self.session_id}.json")
    with open(filename, "w") as f:
        json.dump(serialized, f, indent=2)

# 加载恢复会话
def load_session(filename: str):
    with open(filename, "r") as f:
        data = json.load(f)

    # 恢复消息
    messages = [deserialize(msg) for msg in data["messages"]]
    return messages
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)