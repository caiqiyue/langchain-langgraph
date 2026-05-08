## <center>第2阶段、ReAct案例实战</center>

### 1. LangSmith 环境配置

&emsp;&emsp;LangSmith 是 LangChain 的追踪和监控平台，可以追踪和可视化 Agent 的执行过程。需要配置 `LANGCHAIN_TRACING_V2`、`LANGCHAIN_API_KEY` 和 `LANGCHAIN_PROJECT` 环境变量。

### 2. 天气查询工具实现

&emsp;&emsp;使用 OpenWeather API 实现天气查询功能，包括：
- 实时天气数据查询
- 温度、湿度、风速等详细信息
- 支持全球城市查询

### 3. 数据库存储设计

&emsp;&emsp;使用 SQLAlchemy ORM 定义天气数据模型，实现：
- 天气信息的持久化存储
- 数据查询和更新操作
- MySQL 数据库集成

### 4. LangChain Tool 装饰器

&emsp;&emsp;使用 `@tool` 装饰器将函数封装为 LangGraph 支持的工具格式，支持：
- Pydantic 模型进行参数验证
- 自动生成工具描述
- 与 LangGraph 无缝集成

### 5. 创建 ReAct Agent

&emsp;&emsp;使用 `create_react_agent` 方法创建 ReAct Agent，封装了完整的 ReAct 循环：
- 模型调用
- 工具选择和执行
- 循环判断

### 6. 拓展思考

&emsp;&emsp;思考：ReAct Agent 在实际应用中如何处理工具调用失败的情况？如何设计重试机制和错误处理？

![ReAct 案例实战图](./assets/第四课_02_ReAct案例实战图.html)

**图解说明**：ReAct Agent 案例实战架构图