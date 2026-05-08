"""
01_LangSmith环境配置
演示如何配置LangSmith环境变量
"""
import os

# 设置LangSmith环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key-here"  # 替换为你的API密钥

# 验证环境变量是否设置成功
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY"))

"""
LangSmith配置步骤：

1. 创建LangSmith账户
   - 访问 https://smith.langchain.com/
   - 支持Google、GitHub、Discord和电子邮件登录

2. 创建API密钥
   - 单击仪表板左侧菜单中的"设置"图标
   - 导航至"API密钥"部分
   - 单击"创建API密钥"
   - 选择"密钥类型令牌的个人访问"
   - 复制并保存API密钥

3. 设置环境变量
   - LANGCHAIN_TRACING_V2 = "true"
   - LANGCHAIN_API_KEY = "your-api-key"

设置环境变量后，代码不需要做任何改变，即可构建LangSmith的消息跟踪
"""