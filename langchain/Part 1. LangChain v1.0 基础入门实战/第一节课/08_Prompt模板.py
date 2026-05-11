# -*- coding: utf-8 -*-
"""
【案例 8】Prompt 模板详解
==========================================

本案例展示 LangChain 的 Prompt 模板系统
Prompt 是与 LLM 交互的核心

要点：
1. PromptTemplate - 简单模板
2. ChatPromptTemplate - 消息模板
3. partial_variables - 预填充变量
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
print("案例 8: Prompt 模板详解")
print("=" * 50)

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# ============================================================
# 1. PromptTemplate - 简单模板
# ============================================================
print("\n1. PromptTemplate - 简单模板")
print("-" * 30)

# from_template 方式
template1 = PromptTemplate.from_template(
    "为{product}设计一个创意广告语，要求：{style}"
)
formatted1 = template1.format(product="智能手表", style="年轻时尚")
print(f"模板1: {formatted1}")

# 直接构造方式
template2 = PromptTemplate(
    input_variables=["name", "hobby"],
    template="{name}最喜欢的爱好是{hobby}。"
)
formatted2 = template2.format(name="张三", hobby="游泳")
print(f"模板2: {formatted2}")

# ============================================================
# 2. ChatPromptTemplate - 消息模板
# ============================================================
print("\n2. ChatPromptTemplate - 消息模板")
print("-" * 30)

chat_template = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的{profession}。
请用专业但易懂的语言回答问题。"""),
    ("human", "{user_question}")
])

# format_messages 返回消息列表
messages = chat_template.format_messages(
    profession="Python导师",
    user_question="什么是生成器？"
)

print(f"生成了 {len(messages)} 条消息:")
for i, msg in enumerate(messages):
    role = msg.type if hasattr(msg, 'type') else "unknown"
    preview = msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
    print(f"  {i+1}. [{role}]: {preview}")

# ============================================================
# 3. partial_variables - 预填充变量
# ============================================================
print("\n3. partial_variables - 预填充变量")
print("-" * 30)

"""
【应用场景】
系统提示词通常是不变的，只有用户输入是变的。
使用 partial_variables 可以预填充系统设定。
"""

system_template = """你是一个专业的{department}客服。
请遵循以下规则：
1. 礼貌、耐心地回答
2. 如无法解决，寻求上级帮助
3. 保持专业形象"""

template = PromptTemplate(
    input_variables=["user_question", "department"],
    template=system_template + "\n\n客户问题：{user_question}",
    partial_variables={
        "department": "技术支持"  # 预填充，调用时不需要提供
    }
)

# 使用时只需提供 user_question
formatted = template.format(user_question="密码忘记了怎么办？")
print(f"预填充后的提示:")
print(formatted)

# ============================================================
# 4. Few-shot 示例
# ============================================================
print("\n4. Few-shot 示例")
print("-" * 30)

few_shot_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译专家，将中文翻译成英文。"),
    ("human", "你好"),
    ("ai", "Hello"),
    ("human", "谢谢"),
    ("ai", "Thank you"),
    ("human", "{user_input}"),
])

messages = few_shot_template.format_messages(user_input="再见")
print(f"Few-shot 翻译示例:")
for msg in messages:
    role = msg.type if hasattr(msg, 'type') else msg.__class__.__name__
    print(f"  [{role}]: {msg.content}")

# ============================================================
# 【补充】模板变量语法
# ============================================================
print("\n" + "=" * 50)
print("PromptTemplate 变量语法")
print("=" * 50)
print("""
| 语法                  | 说明                      |
|-----------------------|--------------------------|
| {variable}            | 标准变量替换             |
| partial_variables     | 预填充变量（可选）        |

【注意】
- 变量名必须匹配 input_variables
- 预填充的变量在 format() 时可以省略
- 支持嵌套模板（模板中使用另一个模板）
""")

"""

一、{variable} 本质是什么？

它就是：

给 Prompt 留“空位”

类似 Python 的：

"你好，{}".format(name)

或者：

f"你好，{name}"
例子
template = "你好，{name}"

这里：

{name}

就是一个变量占位符。

后面：

template.format(name="张三")

会得到：

你好，张三
二、为什么 PromptTemplate 要这样设计？

因为：

AI 提示词里，很多内容是固定的，只有少部分内容会变化。

比如客服机器人：

固定部分：

你是专业客服
请礼貌回答

变化部分：

用户的问题

所以模板化就非常重要。

三、你代码里的意思（真正的人话版）

你这段：

system_template = ""
你是一个专业的{department}客服。
""

这里：

{department}

表示：

“客服部门”以后再决定。

可能是：

技术支持
财务
售后
法律咨询

都可以复用。

后面：

客户问题：{user_question}

表示：

用户每次提的问题不同。

所以整个 Prompt：

有两个变量：

department
user_question
四、partial_variables 到底有什么用？

这个才是你真正没理解的重点。

先看不用 partial 的情况

你每次都要写：

template.format(
    department="技术支持",
    user_question="密码忘记了"
)

即使：

department

永远都不会变。

这就很烦。

五、partial_variables 的核心意义

它相当于：

“先把一部分变量固定住”

类似：

先做一个“技术支持专用模板”

以后不用再传 department。

你的代码实际做了什么

这段：

partial_variables={
    "department": "技术支持"
}

相当于：

提前把：

{department}

替换成：

技术支持

所以后面：

template.format(user_question="密码忘记了怎么办？")

就够了。

因为：

department

已经提前固定好了。

六、本质上像什么？

特别像：

Python 的“函数偏函数”

比如：

def add(a, b):
    return a + b

现在固定：

a=10

得到：

add10(x)

以后只需要传：

b

partial_variables
本质也是：

提前固定一部分参数

七、真实 AI 项目里非常常用

比如：

场景1：固定系统角色
你是资深 Java 架构师

永远不变。

变化的是：

用户问题
场景2：固定输出格式
请用 JSON 输出

固定。

变化的是：

用户输入
场景3：多部门机器人

你可以：

技术客服模板
department="技术支持"
财务客服模板
department="财务"
法务机器人
department="法务"

但：

用户问题模板

完全复用。

八、你可以把它理解成：
普通变量
{user_question}

= “运行时动态传入”

partial_variables
department="技术支持"

= “提前写死”

九、最后给你一个最简单理解版本

你现在可以直接记：

功能	本质
{variable}	挖坑，等以后填
format()	真正填坑
partial_variables	提前填一部分坑
十、一个超级直观的小例子
模板
template = ""
你是{role}
用户：{question}
""
不用 partial

每次：

template.format(
    role="Python老师",
    question="什么是装饰器"
)
用 partial

先固定：

role="Python老师"

以后：

template.format(
    question="什么是装饰器"
)

即可。

这就是它的全部意义。

其实：

partial_variables 的本质就是“减少重复输入”。
"""