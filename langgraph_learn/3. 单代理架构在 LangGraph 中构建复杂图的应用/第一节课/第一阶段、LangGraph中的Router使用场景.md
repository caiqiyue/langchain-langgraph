## <center>第一阶段、LangGraph中的Router使用场景</center>

### 1. Router与条件边基础

&emsp;&emsp;在`LangGraph`中，我们可以利用"条件边"这一概念来指导或约束大模型在处理特定任务时的逻辑流程。这种机制允许大模型在达到某一环节并满足预设条件时，根据不同的条件输出或数据，选择性地执行不同的逻辑路径。

&emsp;&emsp;为了管理这样复杂的图结构，`LangGraph`使用的是一个类似于 `if-else`语句的结构组件，称为`Router`（路由）。这个组件允许大模型从一组预设的选项中选择合适的步骤来进行执行。

#### 1.1 基础图结构与add_edge方法

&emsp;&emsp;首先，对于简单的直接从节点`A`到节点`B`，我们一直使用的是`add_edge`方法。

```python
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph

def node_a(state):
    return {"x": state["x"] + 1}

def node_b(state):
    return {"x": state["x"] - 2}

builder = StateGraph(dict)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

# 构建节点之间的边
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile()
```

#### 1.2 条件边与add_conditional_edges方法

&emsp;&emsp;如果想选择性地路由到 1 个或多个边，则需要使用`add_conditional_edges`方法。

```python
class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, NodeSpec] = {}
        self.edges = set[tuple[str, str]]()
        self.branches: defaultdict[str, dict[str, Branch]] = defaultdict(dict)
        self.support_multiple_edges = False
        self.compiled = False

    def add_conditional_edges(
        self,
        source: str,    # 起始节点
        path: Union[    # 这是一个可调用对象，其返回值决定接下来执行的节点
            Callable[..., Union[Hashable, list[Hashable]]],
            Callable[..., Awaitable[Union[Hashable, list[Hashable]]]],
            Runnable[Any, Union[Hashable, list[Hashable]]],
        ],
        path_map: Optional[Union[dict[Hashable, str], list[str]]] = None,  # 路径到节点名称的可选映射
        then: Optional[str] = None,  # 在path选择的节点之后执行的节点的名称
    ) -> Self:
```

&emsp;&emsp;根据源码的定义我们可以非常明确的分析出其调用过程。这里我们要关注`path`参数，它指的是一个函数调用对象，与普通的节点类似，这个对象接受图的当前`state`并返回一个值，根据返回值的不同，来决定路由到哪个节点。

```python
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph
from IPython.display import Image, display

def node_a(state):
    return {"x": state["x"] + 1}

def node_b(state):
    return {"x": state["x"] - 2}

def node_c(state):
    return {"x": state["x"] + 1}

def routing_function():
    if state["x"] == 10:
        return "node_b"
    else:
        return "node_c"


builder = StateGraph(dict)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

builder.set_entry_point("node_a")

# 构建节点之间的边
builder.add_conditional_edges("node_a", routing_function)

graph = builder.compile()

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

&emsp;&emsp;默认情况下，`routing_function`路由函数的返回值用作将状态发送到下一个的节点（或节点列表）的名称。除此之外，还可以使用`path_map`参数，通过一个字典的数据结构将`routing_function`的输出映射到下一个节点的名称。

### 2. Router Function的核心作用

&emsp;&emsp;通过上述实践，大家也能体会到在`LangGraph`中去构建条件边并非难事，我们考虑这样一个现实意义的场景：一般来说，`Agent`是可以接收各种形式的输入，并通过预设的路由逻辑来确定执行的具体操作。

&emsp;&emsp;这里的核心是`Router function` ，它根据输入数据的结构和内容，动态地决定下一步应该执行的节点。例如，对于具体的查询请求，`Router`决定需要访问数据库（Mysql节点），而对于简单的问候（如"Hello"），则直接返回一个响应（Response节点）。每个决策路径最终都指向一个结束节点（End）。

&emsp;&emsp;**在构建实际的`Agent`时，`Router function`的定义才是最关键且最重要的。**我们需要在这个函数中，基于特定的一些格式或者标识来区分该执行哪一条分支的逻辑。而对于消息的传递，大模型往往是通过结构化输出，引导其在响应的过程中应遵循哪种模式来工作。

### 3. 结构化输出的三种方式

&emsp;&emsp;在`LangGraph`中，实现结构化输出可以通过以下三种有效方式完成：
- 提示工程：指示大模型以特定格式做出回应。
- 输出解析器：采用后处理的方法从大模型的响应中提取结构化数据。
- 工具调用：利用一些内置工具调用功能来生成结构化输出。

#### 3.1 使用Pydantic做结构化输出

&emsp;&emsp;使用`Pydantic`去限定输出格式，可以确保所有通过此模型处理的数据都会符合指定的结构和数据类型，从而减少数据处理中的错误并增加代码的健壮性。此外，Pydantic的验证系统还会自动确保所有字段都符合预定义的格式。

```python
from typing import Optional
from pydantic import BaseModel, Field

# 定义 Pydantic 模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")
```

&emsp;&emsp;对于`.with_structured_output()`方法，如果我们希望模型返回一个 `Pydantic` 对象，只需要传入所需的 `Pydantic` 类即可：

```python
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

structured_llm = llm.with_structured_output(UserInfo)

# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

extracted_user_info
```

&emsp;&emsp;它返回的是一个`UserInfo`的`Pytantic`对象，每个字段中则填充了在原始非结构化文本中提取出来的结构化信息。经过这样的格式化输出后，对于`Router function`中，我们就可以通过类似这样的伪代码去继续路由分支的选择：

```python
# isinstance 函数用于判断一个对象是否是一个已知的类型
if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑")
else:
    print("执行节点B的逻辑")
```

#### 3.2 使用TypedDict做结构化输出

&emsp;&emsp;如果不想使用 `Pydantic`去明确地验证输出参数，则可以使用 `TypedDict` 类定义结构化输出的模式。这就可以使用`Annotated`语法，添加对指定字段的默认值和描述。

```python
from typing import Optional
from typing_extensions import Annotated, TypedDict


# 定义 TypedDict 模型
class UserInfo(TypedDict):
    """Extracted user information from text"""
    name: Annotated[str, ..., "The user's name"]
    age: Annotated[Optional[int], None, "The user's age"]
    email: Annotated[str, ..., "The user's email address"]
    phone: Annotated[Optional[str], None, "The user's phone number"]

structured_llm = llm.with_structured_output(UserInfo)

# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

extracted_user_info
```

&emsp;&emsp;使用 `TypedDict` 创建的"对象"实际上是一个字典。它没有`Pydantic`模型那样的方法和属性，因此功能相对简单。`TypedDict` 主要用于静态类型检查。

#### 3.3 Json Schema方式

&emsp;&emsp;对于`Json Schema`格式大家应该最为熟悉，不需要导入或类，可以直接通过字典的形式清楚地准确记录每个参数。

```python
# 定义 JSON Schema
json_schema = {
    "title": "user_info",
    "description": "Extracted user information",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The user's name",
        },
        "age": {
            "type": "integer",
            "description": "The user's age",
            "default": None,
        },
        "email": {
            "type": "string",
            "description": "The user's email address",
        },
        "phone": {
            "type": "string",
            "description": "The user's phone number",
            "default": None,
        },
    },
    "required": ["name", "email"],
}

structured_llm = llm.with_structured_output(json_schema)

# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")
```

### 4. 拓展思考

#### 4.1 深度概念：结构化输出与Router的协同工作原理

&emsp;&emsp;在LangGraph中，Router Agent的核心在于利用结构化输出来实现智能路由。当用户输入非结构化文本时，大模型通过`.with_structured_output()`方法将其转换为结构化的Pydantic对象，这个对象包含了模型对输入内容的分类结果。

&emsp;&emsp;Router Function则根据这个结构化对象的类型（如`UserInfo`表示需要数据库操作，`ConversationalResponse`表示普通对话）来决定下一步应该执行哪个节点。这种设计的优势在于：

1. **类型安全**：Pydantic在运行时进行数据验证，确保输出符合预期格式
2. **可扩展性**：可以通过添加新的Pydantic类来支持更多的路由分支
3. **清晰的业务逻辑**：路由决策基于明确的类型判断，而非复杂的条件逻辑

#### 4.2 Router Agent与后续代理架构的关系

&emsp;&emsp;Router Agent是LangGraph中四种代理架构的基础。它的局限性在于每次只能控制一个决策点，当某个分支中需要执行多个工具时，就需要过渡到Tool Calling Agent。这种递进关系体现了LangGraph设计中的模块化思想：基础的路由能力作为更复杂代理架构的构建块。

&emsp;&emsp;在后续的Tool Calling Agent中，Router的路由逻辑依然存在，只不过路由的对象从固定的节点变成了动态选择的工具。这种设计使得我们可以在不改变整体架构的情况下，通过添加或修改工具来扩展代理的能力。