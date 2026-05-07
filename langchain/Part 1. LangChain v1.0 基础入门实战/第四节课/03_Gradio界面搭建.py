# -*- coding: utf-8 -*-
"""
【案例 3】Gradio 网页界面
==========================================

本案例展示如何使用 Gradio 构建网页对话界面

要点：
1. Gradio Blocks 构建方式
2. Chatbot 组件
3. 事件绑定
4. State 状态管理

注意：需要安装 gradio
    pip install gradio
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)
# API Key 从环境变量读取
# os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# os.environ["DASHSCOPE_BASE_URL"] = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

print("=" * 50)
print("案例 3: Gradio 网页界面")
print("=" * 50)

import gradio as gr
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ============================================================
# 1. Gradio 组件介绍
# ============================================================
print("\n1. Gradio 组件")
print("-" * 30)

print("""
Gradio 两大构建方式：

1. Interface（简单接口）
   输入 → 函数 → 输出

2. Blocks（自定义布局）- 我们用这个
   可以精确控制 UI

核心组件：

布局：
- Column / Row: 行列布局
- Tab: 选项卡

输入：
- Textbox: 文本框
- Number: 数字
- Slider: 滑块

输出：
- Textbox: 文本输出
- Chatbot: 对话机器人
- Image: 图片

交互：
- Button: 按钮
""")

# ============================================================
# 2. Chatbot 组件详解
# ============================================================
print("\n2. Chatbot 组件")
print("-" * 30)

print("""
Chatbot 数据格式：
[(user_msg, bot_msg), (user_msg, bot_msg), ...]

示例：
chatbot.value = [
    ("你好", "你好！有什么帮助？"),
    ("我叫张三", "很高兴认识你，张三！"),
]

头像设置：
- emoji: avatar_images=("👤", "🤖")
- 图片: avatar_images=("user.png", "bot.png")
""")

# ============================================================
# 3. 完整 Gradio 对话机器人代码
# ============================================================
print("\n3. 完整 Gradio 对话机器人")
print("-" * 30)

# 初始化模型
model = ChatTongyi(model="qwen3-max")
SYSTEM_PROMPT = """你叫小智，是一名乐于助人的智能助手。
请在对话中保持友好、有耐心、温和的语气。"""
system_message = SystemMessage(content=SYSTEM_PROMPT)

def respond(user_msg, chat_hist, messages_list):
    """处理用户消息"""
    if not messages_list:
        messages_list = [system_message]

    messages_list.append(HumanMessage(content=user_msg))
    chat_hist = chat_hist + [(user_msg, "")]

    partial = ""
    for chunk in model.stream(messages_list):
        if chunk.content:
            partial += chunk.content
            chat_hist[-1] = (user_msg, partial)
            yield "", chat_hist, messages_list

    messages_list.append(AIMessage(content=partial))
    yield "", chat_hist, messages_list

def clear_history():
    return "", [], []

# 构建界面
with gr.Blocks(title="🤖 小智对话机器人") as demo:
    gr.Markdown("# 🤖 小智对话机器人")
    gr.Markdown("基于 LangChain × 通义千问 的流式对话")

    chatbot = gr.Chatbot(height=500)

    with gr.Row():
        msg = gr.Textbox(placeholder="请输入...", scale=7)
        submit = gr.Button("发送 🚀", scale=1, variant="primary")
        clear = gr.Button("清空 🗑️", scale=1)

    state = gr.State([])

    msg.submit(respond, [msg, chatbot, state], [msg, chatbot, state])
    submit.click(respond, [msg, chatbot, state], [msg, chatbot, state])
    clear.click(clear_history, outputs=[msg, chatbot, state])

print("Gradio 对话机器人代码已定义")
print("\n运行方式：")
print("  demo.launch()  # 本地访问 http://localhost:7860")
print("  demo.launch(share=True)  # 获得公共链接")

# ============================================================
# 【补充】事件绑定机制
# ============================================================
print("\n" + "=" * 50)
print("事件绑定机制")
print("=" * 50)
print("""
Gradio 事件遵循"触发器 → 函数 → 更新"模式：

component.event(
    fn=处理函数,
    inputs=[组件列表],
    outputs=[组件列表]
)

示例：
msg.submit(
    fn=respond,
    inputs=[msg, chatbot, state],
    outputs=[msg, chatbot, state]
)

- msg 是输入：获取用户输入
- respond 是处理函数
- 返回值更新 chatbot 和 state
""")
