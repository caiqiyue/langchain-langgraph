## <center>第2阶段、工具调用代理Tool Calling Agent</center>

### 1. Tool Calling Agent 的完整实现

&nbsp;&nbsp;&nbsp;&nbsp;Tool Calling Agent 的本质原理是：让大模型根据用户的输入，自动的去判断应该使用哪个函数，并实际的执行，最后结合工具的响应结果 + 用户的原始问题作为完整的`Prompt`生成最终的问题。

&nbsp;&nbsp;&nbsp;&nbsp;完整的 Tool Calling Agent 链路是：
1. 用户输入 -> chat_with_model（结构化输出判断是否需要工具）
2. 如果需要工具 -> execute_function（调用 ToolNode 执行工具）
3. 如果不需要工具 -> final_answer（直接生成响应）
4. 最后 -> natural_response（生成最终的自然语言响应）

### 2. 手动构建 Tool Calling Agent

&nbsp;&nbsp;&nbsp;&nbsp;工具调用的过程也可以手动进行实现。我们只需要：
1. 定义`exists_function_calling`函数判断是否存在函数调用
2. 手动实现`execute_function`节点来执行工具
3. 通过`llm.bind_tools(tools)`将工具绑定到模型

### 3. 拓展思考

&nbsp;&nbsp;&nbsp;&nbsp;无论是对于图结构，还是工具的接入，可扩展性都非常高。使用这个代理架构需要注意的是`Router Function`的分支判断。因为调用工具的参数是由大模型根据用户输入的自然语言生成的，所以一定会存在尝试调用不存在的工具，或者无法返回与请求的参数的问题。