"""
第1阶段、LangGraph中的HIL
本文件演示如何初始化 LLM（大语言模型）
"""

import getpass
import os
from langchain_openai import ChatOpenAI


# ============================================================
# LLM 初始化
# ============================================================
# 在 LangGraph 中，LLM 是 Agent 的"大脑"，负责处理用户输入并生成响应


def initialize_llm(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    """
    初始化大语言模型

    Args:
        model_name: 模型名称，默认使用 gpt-4o-mini

    Returns:
        ChatOpenAI 实例
    """
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    llm = ChatOpenAI(model=model_name)
    return llm


def test_llm_connection():
    """测试 LLM 连接"""
    print("=" * 50)
    print("LLM 初始化测试")
    print("=" * 50)

    # 初始化 LLM
    llm = initialize_llm("gpt-4o-mini")

    # 测试连接
    response = llm.invoke("你好，请介绍一下你自己")
    print(f"\n模型响应: {response.content}")

    return llm


# 使用 ToolNode 需要绑定工具
def initialize_llm_with_tools(llm, tools):
    """
    初始化带工具的 LLM

    Args:
        llm: ChatOpenAI 实例
        tools: 工具列表

    Returns:
        绑定了工具的 LLM
    """
    return llm.bind_tools(tools)


if __name__ == "__main__":
    # 测试 LLM 初始化
    llm = test_llm_connection()

    print("\n" + "=" * 50)
    print("LLM 初始化完成")
    print("=" * 50)
    print("""
在 Human-in-the-loop (HIL) 应用中，LLM 用于：
1. 分析用户输入，判断是否需要人工介入
2. 生成需要人工确认的提示信息
3. 在人工确认后，继续执行后续流程

下一节我们将学习如何设置中断点来实现 HIL。
""")