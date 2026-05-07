# -*- coding: utf-8 -*-
"""
【案例 6】完整可运行的 Gradio 对话机器人
==========================================

本案例是一个完整的、可运行的 Gradio 对话机器人
可以直接保存为 app.py 运行

运行方式：
    conda activate langchain_learning
    python "第四阶段_代码案例/06_完整Gradio机器人.py"

访问：
    http://localhost:7860
"""

# ============================================================
# 完整可运行的 Gradio 对话机器人
# ============================================================

import os
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)

# 设置 DashScope 配置
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ──────────────────────────────────────────────
# 1. 初始化模型
# ──────────────────────────────────────────────
model = ChatTongyi(
    model="qwen3-max",
    temperature=0.7,
)

SYSTEM_PROMPT = """你叫小智，是一名乐于助人的智能助手。

请在对话中：
- 保持友好、有耐心、温和的语气
- 回答问题专业且易懂
- 适当使用 emoji 增添趣味"""

system_message = SystemMessage(content=SYSTEM_PROMPT)

# ──────────────────────────────────────────────
# 2. 响应函数
# ──────────────────────────────────────────────
def respond(user_msg: str, chat_hist: list, messages_list: list):
    """处理用户消息，返回流式响应"""

    # 初始化
    if not messages_list:
        messages_list = [system_message]

    # 添加用户消息
    messages_list.append(HumanMessage(content=user_msg))

    # 更新聊天历史（用户侧）
    chat_hist = chat_hist + [(user_msg, "")]

    # 流式生成
    partial = ""
    try:
        for chunk in model.stream(messages_list):
            if chunk.content:
                partial += chunk.content
                chat_hist[-1] = (user_msg, partial)
                yield "", chat_hist, messages_list
    except Exception as e:
        chat_hist[-1] = (user_msg, f"错误：{str(e)}")
        yield "", chat_hist, messages_list
        return

    # 保存完整回复
    messages_list.append(AIMessage(content=partial))

    # 限制历史长度
    MAX_HISTORY = 50
    if len(messages_list) > MAX_HISTORY:
        messages_list = [system_message] + messages_list[-(MAX_HISTORY-1):]

    yield "", chat_hist, messages_list


def clear_history():
    """清空对话历史"""
    return "", [], []


# ──────────────────────────────────────────────
# 3. 构建界面
# ──────────────────────────────────────────────
with gr.Blocks(title="🤖 小智对话机器人") as demo:
    gr.Markdown("# 🤖 小智对话机器人")
    gr.Markdown("基于 LangChain 1.0 × 通义千问 的流式对话")

    chatbot = gr.Chatbot(
        height=500,
        show_copy_button=True,
        avatar_images=("👤", "🤖")
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="请输入您的问题...",
            container=False,
            scale=7,
            autofocus=True
        )
        submit = gr.Button("发送 🚀", scale=1, variant="primary")
        clear = gr.Button("清空 🗑️", scale=1)

    # 示例问题
    gr.Examples([
        ["你好，请介绍一下你自己"],
        ["什么是 LangChain？"],
        ["给我讲一个笑话"]
    ], inputs=msg)

    state = gr.State([])

    # 事件绑定
    msg.submit(respond, [msg, chatbot, state], [msg, chatbot, state])
    submit.click(respond, [msg, chatbot, state], [msg, chatbot, state])
    clear.click(clear_history, outputs=[msg, chatbot, state])


# ──────────────────────────────────────────────
# 4. 启动应用
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 启动 Gradio 应用...")
    print("📍 本地访问：http://localhost:7860")
    print("🌐 公共访问：设置 share=True")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 设为 True 可获得公共链接
    )
