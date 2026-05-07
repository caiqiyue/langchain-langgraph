## <center>第二阶段、LangChain中间件(Middleware)入门</center>

### 1. 中间件架构原理

中间件 = 拦截、修改、控制和增强 Agent 执行流程的机制

![中间件洋葱模型](../assets/第一课_01_中间件洋葱模型.html)

**图解说明**：中间件六大 Hook 点 — before_agent → before_model → wrap_model_call → wrap_tool_call → after_model → after_agent

### 2. 六大 Hook 执行点

| Hook 点 | 作用 |
|---------|------|
| before_agent | Agent 执行前最后机会修改输入 |
| before_model | 模型调用前修改 prompt / 选择模型 |
| wrap_model_call | 包裹模型调用（异常处理、重试） |
| wrap_tool_call | 包裹工具调用（异常处理、重试） |
| after_model | 模型调用后修改输出 |
| after_agent | Agent 执行完成后的最终处理 |

### 3. 中间件四大分类

![中间件四大分类](../assets/第二课_01_中间件四大分类.html)

**图解说明**：Monitor（监控）、Modify（修改）、Control（控制）、Enforce（强制）四类中间件

| 分类 | 核心功能 | 解决问题 | 性能影响 |
|------|---------|---------|---------|
| Monitor | 观察执行状态 | 调试困难 | < 1ms |
| Modify | 修改输入/输出 | 上下文溢出 | 1-50ms |
| Control | 流程阻断 | AI幻觉 | 5-20ms |
| Enforce | 安全过滤 | 数据泄露 | 1-5ms |

### 4. 课程案例

| 文件 | 内容说明 |
|------|---------|
| `01_中间件架构原理.py` | 中间件设计原理与六大 Hook |
| `02_中间件四大分类.py` | 四类中间件详解 |

**运行示例**：

```bash
python "Part 3. LangChain1.0 Agent智能体中间件应用实战/第二节课/01_中间件架构原理.py"
```