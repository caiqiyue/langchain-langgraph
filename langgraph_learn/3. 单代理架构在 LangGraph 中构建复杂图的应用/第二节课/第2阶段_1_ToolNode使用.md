## <center>第2阶段、工具调用代理Tool Calling Agent</center>

### 1. ToolNode的使用

&nbsp;&nbsp;&nbsp;&nbsp;`Tool Calling Agent`是`LangGraph`支持的第二种`AI Agent`代理架构。这个代理架构是在`Router Agent`的基础上，大模型可以自主选择并使用多种工具来完成某个条件分支中的任务。

&nbsp;&nbsp;&nbsp;&nbsp;在`LangGraph`框架中，可以直接使用预构建`ToolNode`进行工具调用。`ToolNode`使用消息列表对图状态进行操作，将图形状态（带有消息列表）作为输入并输出状态更新以及工具调用的结果。

&nbsp;&nbsp;&nbsp;&nbsp;使用`@tool`装饰器可以将普通函数转换为可被`ToolNode`使用的工具函数：

```python
from langchain_core.tools import tool

@tool
def fetch_real_time_info(query):
    """Get real-time Internet information"""
    # 工具实现
    return result

@tool
def get_weather(location):
    """Call to get the current weather."""
    # 工具实现
    return weather_info
```

### 2. 拓展思考

&nbsp;&nbsp;&nbsp;&nbsp;通过`ToolNode(tools)`可以根据参数来执行函数，并返回结果。而其前一步，根据自然语言生成执行具体某个函数必要参数的过程，则由大模型决定。这个过程可以通过`bind_tools`函数来实现，将工具绑定到大模型上。