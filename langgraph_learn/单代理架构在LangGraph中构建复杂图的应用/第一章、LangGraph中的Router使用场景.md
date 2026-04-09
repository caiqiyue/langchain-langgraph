&emsp;&emsp;在`LangGraph`中，我们可以利用“条件边”这一概念来指导或约束大模型在处理特定任务时的逻辑流程。这种机制允许大模型在达到某一环节并满足预设条件时，根据不同的条件输出或数据，选择性地执行不同的逻辑路径。如下图所示：

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/20241024002.png" width=60%></div>

&emsp;&emsp;为了管理这样复杂的图结构，`LangGraph`使用的是一个类似于 `if-else`语句的结构组件，称为`Router`（路由）。这个组件允许大模型从一组预设的选项中选择合适的步骤来进行执行。这个设计思路并不难理解，同时由于`LangGraph`的底层封装，实现起来也非常简单，我们看下面的代码：

&emsp;&emsp;首先，对于简单的直接从节点`A`到节点`B`，我们一直使用的是`add_edge`方法，即：

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

graph = builder.compile()```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;如果想选择性地路由到 1 个或多个边，则需要使用`add_conditional_edges`方法。该方法也在`Graph`的基类中进行了定义，如下所示：

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
        path: Union[    #  这是一个可调用对象，其返回值决定接下来执行的节点。这个函数可以是简单的 Python 函数，或者是任何可以被调用来决定分支路径的对象。
            Callable[..., Union[Hashable, list[Hashable]]],
            Callable[..., Awaitable[Union[Hashable, list[Hashable]]]],
            Runnable[Any, Union[Hashable, list[Hashable]]],
        ],
        path_map: Optional[Union[dict[Hashable, str], list[str]]] = None,  # 路径到节点名称的可选映射。如果省略， path返回的路径应该是节点名称。
        then: Optional[str] = None,  # 在path选择的节点之后执行的节点的名称。
    ) -> Self:
```

> add_conditional_edges 源码：https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.graph.Graph

&emsp;&emsp;根据源码的定义我们可以非常明确的分析出其调用过程。这里我们要关注`path`参数，它指的是一个函数调用对象，与普通的节点类似， 这个对象接受图的当前`state`并返回一个值，根据返回值的不同，来决定路由到哪个节点。比如想构建一个带有路由的图结构，这里我们定义一个 `routing_function` 作为路由函数，并添加一个新的节点`node_c`，代码如下所示：

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

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;默认情况下，`routing_function`路由函数的返回值用作将状态发送到下一个的节点（或节点列表）的名称。除此之外，还可以使用`path_map`参数，通过一个字典的数据结构将`routing_function`的输出映射到下一个节点的名称。这里改动如下：

```python
from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph

def node_a(state):
    return {"x": state["x"] + 1}

def node_b(state):
    return {"x": state["x"] - 2}

def node_c(state):
    return {"x": state["x"] + 1}

def routing_function():
    if state["x"] == 10:
        return True
    else:
        return False

builder = StateGraph(dict)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

builder.set_entry_point("node_a")

# 构建节点之间的边
builder.add_conditional_edges("node_a", routing_function, {True: "node_b", False: "node_c"})

builder.add_edge("node_b", END)
builder.add_edge("node_c", END)

graph = builder.compile()

from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;通过上述实践，大家也能体会到在`LangGraph`中去构建条件边并非难事，我们考虑这样一个现实意义的场景：一般来说，`Agent`是可以接收各种形式的输入，并通过预设的路由逻辑来确定执行的具体操作。如图所示，`Agent`的开始节点（Start）接收输入数据，这些输入可以是查询请求（例如“name: muyu, age: 18, phone: 123”或“Hello”）。根据输入的不同，流程通过`Router`函数进行决策，将不同的输入引导到正确的处理流程。

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/20241024003.png" width=80%></div>

&emsp;&emsp;这里的核心是`Router function` ，它根据输入数据的结构和内容，动态地决定下一步应该执行的节点。例如，对于具体的查询请求，`Router`决定需要访问数据库（Mysql节点），而对于简单的问候（如"Hello"），则直接返回一个响应（Response节点）。每个决策路径最终都指向一个结束节点（End）。所以我们要明确的是，**在构建实际的`Agent`时，`Router fuction`的定义才是最关键且最重要的。**我们需要在这个函数中，基于特定的一些格式或者标识来区分该执行哪一条分支的逻辑。而**对于消息的传递，大模型往往是通过结构化输出，引导其在响应的过程中应遵循哪种模式来工作，就类似于工具调用过程。`Router`就很好的利用到了这个特性，通过结构化输出的特性来控制接下来的分支路径。**

&emsp;&emsp;这里我们先来了解一下什么是结构化输出。在`LangGraph`中，实现结构化输出可以通过以下三种有效方式完成：
- 提示工程：指示大模型以特定格式做出回应。
- 输出解析器：采用后处理的方法从大模型的响应中提取结构化数据。
- 工具调用：利用一些内置工具调用功能来生成结构化输出。

- **提示工程**

```python
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")```

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json`",
        ),
        ("human", "{query}"),
    ]
)```

```python
chain = prompt | llm ```

```python
ans = chain.invoke({"query": "我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052"})```

```python
ans.content```

&emsp;&emsp;直接通过提示工程让大模型生成特定格式的输出虽然是可行的，但这种方法在复杂的`Agent`构建流程中非常并不稳定。一个进阶的**优化方法是：引入后处理步骤，通过输出解析器来格式化大模型生成的响应。**这种做法可以提高输出的准确性和一致性，这种形式的实现方法如下所示：

- **提示工程 + 输出解析器**

```python
from langchain_core.messages import AIMessage
import json
import re
from typing import List

def extract_json(message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text = message.content
    # 定义正则表达式模式来匹配JSON块
    pattern = r"\`\`\`json(.*?)\`\`\`"

    # 在字符串中查找模式的所有非重叠匹配
    matches = re.findall(pattern, text, re.DOTALL)

    # 返回匹配的JSON字符串列表，去掉任何开头或结尾的空格
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")```

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json`",
        ),
        ("human", "{query}"),
    ]
)```

```python
chain = prompt | llm | extract_json```

```python
ans = chain.invoke({"query": "我叫木羽，今年18岁，邮箱地址是snow@gmial.com，电话是1234567052"})```

```python
ans```

- **内置工具方法**

&emsp;&emsp;从结果可以明显看出，通过定制化的输出解析器得到的结果会更加的符合预期，而接下来我们要说的是，在`LangGraph`中我们更常用的，且效果更好的是，直接使用其内置的工具方法：`.with_structured_output()`。

&emsp;&emsp;这个方法通过接受一个定义了所需输出属性的名称、类型和描述的模式作为输入，进而生成一个类似模型的 `Runnable`。不同于常规模型输出字符串或消息，这个 `Runnable` 输出一个与输入模式相匹配的对象。可以通过几种方式指定这种架构，包括 `TypedDict` 类、`JSON Schema` 或 `Pydantic` 类。如果采用 `TypedDict` 或 `JSON Schema`，`Runnable` 将输出一个字典；若使用 `Pydantic` 类，则输出一个 `Pydantic` 对象。我们可以依次的来实践一下。

&emsp;&emsp;我们首先尝试和实践使用`Pydantic`类做格式化输出，应用的场景是：从文本中提取格式化的数据。

## 1.1 使用Pydantic做结构化输出

&emsp;&emsp;使用`Pydantic`去限定输出格式，可以确保所有通过此模型处理的数据都会符合指定的结构和数据类型，从而减少数据处理中的错误并增加代码的健壊性。此外，Pydantic的验证系统还会自动确保所有字段都符合预定义的格式，如果输入数据不符合预期，则会抛出错误。比如下面是一个用`Pydantic`定义用户信息模型的示例：

```python
from typing import Optional
from pydantic import BaseModel, Field

# 定义 Pydantic 模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")```

&emsp;&emsp;在这个`UserInfo`模型中：
- name（必需）: 存储用户的名字。
- age（可选）: 存储用户的年龄，这是一个可选字段。
- email（必需）: 存储用户的电子邮件地址。
- phone（可选）: 存储用户的电话号码，这也是一个可选字段。

&emsp;&emsp;对于`.with_structured_output()`方法，如果我们希望模型返回一个 `Pydantic` 对象，只需要传入所需的 `Pydantic` 类即可，即`UserInfo`，代码如下所示：

```python
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")```

```python
structured_llm = llm.with_structured_output(UserInfo)```

```python
structured_llm```

```python
# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

extracted_user_info```

```python
# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我是哈哈，3岁，邮箱为snow@gmial.com，电话是1234233052")

extracted_user_info```

&emsp;&emsp;它返回的是一个`UserInfo`的`Pytantic`对象，每个字段中则填充了在原始非结构化文本中提取出来的结构化信息。经过这样的格式化输出呢，对于`Router function`中，我们就可以通过类似这样的伪代码去继续路由分支的选择，比如：

```python
# isinstance 函数用于判断一个对象是否是一个已知的类型，或者是该类型的子类的实例
if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑")
else:
    print("执行节点B的逻辑")```

```python
extracted_user_info = "你好"

if isinstance(extracted_user_info, UserInfo):
    print("执行节点A的逻辑")
else:
    print("执行节点B的逻辑")```

&emsp;&emsp;这就是结构化输出对于`LangGraph`中路由函数逻辑判断的意义所在。除此之外，还有`TypedDict` 和 `JSON Schema`能够做到相同的效果，下面我们依次对这两种模式进行尝试。

## 1.2 使用TypedDict做结构化输出

&emsp;&emsp;如果不想使用 `Pydantic`去明确地验证输出参数，则可以使用 `TypedDict` 类定义结构化输出的模式。这就可以使用我们上节课详细介绍的特殊`Annotated`语法，添加对指定字段的默认值和描述。

```python
from typing import Optional
from typing_extensions import Annotated, TypedDict


# 定义 TypedDict 模型
class UserInfo(TypedDict):
    """Extracted user information from text"""
    name: Annotated[str, ..., "The user's name"]
    age: Annotated[Optional[int], None, "The user's age"]
    email: Annotated[str, ..., "The user's email address"]
    phone: Annotated[Optional[str], None, "The user's phone number"]```

```python
structured_llm = llm.with_structured_output(UserInfo)

# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

extracted_user_info```

&emsp;&emsp;使用 `TypedDict` 创建的“对象”实际上是一个字典。它没有`Pydantic`模型那样的方法和属性，因此功能相对简单。`TypedDict` 主要用于静态类型检查，但它不会在运行时进行类型检查，但搭配着`LangGraph`中已实现的基本验证机制，也是一种不错的方法。

## 1.3 Json Schema

&emsp;&emsp;对于`Json Schema`格式大家应该最为熟悉，不需要导入或类，可以直接通过字典的形式清楚地准确记录每个参数，但代价是代码会更加冗长。如下所示`user_info` 的 `JSON Schema`，用于描述用户信息的结构，包括姓名、年龄、邮箱地址和电话号码。

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
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")```

```python
extracted_user_info```

## 1.4 结合结构化输出构建路由图

&emsp;&emsp;三种不同的结构化输出方法，我们更常使用的是用`Pydantic`来处理路由决策。在这种策略下，我们可以通过定义一个包含`Union`类型属性的父模型来灵活地从多种模式中选择适当的路由分支。例如，如果我们想根据输出决定是查询数据库还是直接回答问题，可以创建一个统一的模型来封装可能的输出类型。代码如下所示：

```python
from typing import Union, Optional
from pydantic import BaseModel, Field

# 定义数据库插入的用户信息模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")


# 定义正常生成模型回复的模型
class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner. Be kind and helpful."""
    response: str = Field(description="A conversational response to the user's query")


# 定义最终响应模型，可以是用户信息或一般响应
class FinalResponse(BaseModel):
    final_output: Union[UserInfo, ConversationalResponse]```

&emsp;&emsp;这个扩展后的代码将用于提取和存储用户的基本信息，包括姓名、年龄、电子邮件地址和电话号码的`UserInfo`模型与用于生成面向用户的交流响应的`ConversationalResponse`模型统一的放在了`FinalResponse`模型中，使用`Union`类型来支持灵活的输出选项。`final_output`属性可以是`UserInfo`类型，也可以是`ConversationalResponse`类型，这使得系统可以根据不同的业务逻辑和用户输入决定输出的具体形式。例如，在用户请求个人数据时可以返回`UserInfo`，而在普通查询时则提供`ConversationalResponse`。

```python
structured_llm = llm.with_structured_output(FinalResponse)```

```python
# 从非结构化文本中提取用户信息或进行一般对话响应
extracted_user_info = structured_llm.invoke("你好")

extracted_user_info```

```python
extracted_user_info.final_output.response```

```python
# 从非结构化文本中提取用户信息
extracted_user_info = structured_llm.invoke("我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1234567052")

extracted_user_info```

```python
extracted_user_info.final_output```

&emsp;&emsp;掌握到这种程度，我们就可以利用这些判别条件作为`Router Function`来构建决策分支。通过使用`Pydantic`模型来提取结构化数据，能够在大语言模型（LLM）调用过程中将非结构化文本转换为结构化数据格式。这种转换使得我们构建的流程图能够根据用户的不同输入，智能判断是应当生成常规响应还是执行数据库操作。代码如下所示：

&emsp;&emsp;首先，还是定义`Pydantic`模型以及用于生成格式化输出的大模型实例。

```python
import getpass
import os
from typing import Union, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# 定义数据库插入的用户信息模型
class UserInfo(BaseModel):
    """Extracted user information, such as name, age, email, and phone number, if relevant."""
    name: str = Field(description="The name of the user")
    age: Optional[int] = Field(description="The age of the user")
    email: str = Field(description="The email address of the user")
    phone: Optional[str] = Field(description="The phone number of the user")


# 定义正常生成模型回复的模型
class ConversationalResponse(BaseModel):
    """Respond to the user's query in a conversational manner. Be kind and helpful."""
    response: str = Field(description="A conversational response to the user's query")



# 定义最终响应模型，可以是用户信息或一般响应
class FinalResponse(BaseModel):
    final_output: Union[UserInfo, ConversationalResponse]



if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# 生成模型实例
llm = ChatOpenAI(model="gpt-4o-mini")```

&emsp;&emsp;接下来，考虑到设计的场景中用户需要执行数据库操作，我们首先需要实现一个连接数据库的函数。在这个示例中，我们选择使用MySQL数据库。基于`UserInfo`模型的定义，构建一个相应的表结构，以便支持后续的数据插入和更新操作。

> 关于如何在Windows上安装Mysql，大家可以参考我们之前课程的内容，在《大模型技术实战课》的 Ch 16.2（上） 热门AI应用开发实战二：定制化SQL代码解释器第三小节课程中的内容。

```python
# pip install sqlalchemy pymysql```

```python
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker 
from sqlalchemy.orm import sessionmaker


# 创建基类
Base = declarative_base()

# 定义 UserInfo 模型
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    email = Column(String(100))
    phone = Column(String(15))

# 数据库连接 URI，这里要替换成自己的Mysql 连接信息，以下是各个字段的对应解释：
# root：MySQL 数据库的用户名。
# snowball950123：MySQL 数据库的密码。
# 192.168.110.131：MySQL 服务器的 IP 地址。
# langgraph_agent：要连接的数据库的名称。
# charset=utf8mb4：设置数据库的字符集为 utf8mb4，支持更广泛的 Unicode 字符
DATABASE_URI = 'mysql+pymysql://root:snowball950123@192.168.110.131/langgraph_agent?charset=utf8mb4'   
engine = create_engine(DATABASE_URI, echo=True)

# 如果表不存在，则创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()```

&emsp;&emsp;如果Mysql服务正常且连接信息填写正确，将会在`langgraph_agent`数据库中创建出一个`User`表，如下所示：（下图软件为`Navicate`，大家可自行下载，下载链接 👉 https://www.navicat.com/en/download/navicat-premium）

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241025103225895.png" width=80%></div>

&emsp;&emsp;接下来我们定义节点函数，其中`chat_with_model`作为路由节点将用户输入的文本转化成格式化输出，搭配`Router Function`构建分支。

```python
def chat_with_model(state):
    """generate structured output"""
    print(state)
    print("-----------------")
    messages = state['messages']
    structured_llm = llm.with_structured_output(FinalResponse)
    response = structured_llm.invoke(messages)
    return {"messages": [response]}```

&emsp;&emsp;然后分别定义两个分支节点，其中`final_answer`用于直接生成响应，而`insert_db`用于执行数据库插入操作。

```python
def final_answer(state):
    """generate natural language responses"""
    print(state)
    print("-----------------")
    messages = state['messages'][-1]
    response = messages.final_output.response
    return {"messages": [response]}

def insert_db(state):
    """Insert user information into the database"""
    session = Session()  # 确保为每次操作创建新的会话
    try:
        result = state['messages'][-1]
        output = result.final_output
        # 创建用户实例
        user = User(name=output.name, age=output.age, email=output.email, phone=output.phone)
        # 添加到会话
        session.add(user)
        # 提交事务
        session.commit()
        return {"messages": [f"数据已成功存储至Mysql数据库。"]}
    except Exception as e:
        session.rollback()  # 出错时回滚
        return {"messages": [f"数据存储失败，错误原因：{e}"]}
    finally:
        session.close()  # 关闭会话```

&emsp;&emsp;定义好了所有节点函数后，开始构建图。

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage```

```python
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]```

&emsp;&emsp;定义`generate_branch`函数作为`Router Function`，根据经过`chat_with_model`节点后产生的不同`Pydantic`对象，选择连接不同的节点，即`final_answer`或`insert_db`。

```python
def generate_branch(state: AgentState):
    result = state['messages'][-1]
    output = result.final_output

    if isinstance(output, UserInfo):
        return True
    elif isinstance(output, ConversationalResponse):
        return False```

&emsp;&emsp;构建图并使用条件边来生成`Router`。代码如下：

```python
graph = StateGraph(AgentState)

# 添加三个节点
graph.add_node("chat_with_model", chat_with_model)
graph.add_node("final_answer", final_answer)
graph.add_node("insert_db", insert_db)

# 设置图的启动节点
graph.set_entry_point("chat_with_model")

# 设置条件边
graph.add_conditional_edges(
    "chat_with_model",
    generate_branch,
    {True: "insert_db", False: "final_answer"}
    )

# 设置终止节点
graph.set_finish_point("final_answer")
graph.set_finish_point("insert_db")

# 编译图
graph = graph.compile()```

&emsp;&emsp;可视化图的完整结构，代码如下所示：

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))```

&emsp;&emsp;接下来进行测试，首先测试执行插入数据库的条件分支。

```python
query="我叫木羽，今年28岁，邮箱地址是snow@gmial.com，电话是1323521313"
input_message = {"messages": [HumanMessage(content=query)]}

result = graph.invoke(input_message)
result```

```python
result["messages"][-1]```

&emsp;&emsp;而如果正常的问答，则会经过`final_answer`直接生成响应。

```python
query="你好，请你介绍一下你自己"
input_message = {"messages": [HumanMessage(content=query)]}

result = graph.invoke(input_message)
result["messages"][-1]```

```python
result["messages"][-1]```

```python
query="请问什么是机器学习"
input_message = {"messages": [HumanMessage(content=query)]}

result = graph.invoke(input_message)
result["messages"][-1]```

```python
query="我叫哈哈哈，今年108岁，邮箱地址是haha@gmial.com"
input_message = {"messages": [HumanMessage(content=query)]}

result = graph.invoke(input_message)
result```

<div align=center><img src="https://muyu001.oss-cn-beijing.aliyuncs.com/img/image-20241025105107635.png" width=80%></div>

&emsp;&emsp;此时可以通过`Navicate`工具验证，数据已成功插入到本地的Mysql数据库中。

&emsp;&emsp;如上示例就是`LangGraph`中`Router`的常用使用形式，通过预定义的分支结构，可以根据用户的输入请求灵活适配不同的场景，在这个过程中，结构化输出对于路由至关重要，因为它们确保系统可以可靠地解释大模型的决定并采取行动。这种`Router Agent`（路由代理）的**优势就是可以精准的控制程序链路中的每一个细节，但同时也表现出来了这是一种相对有限的控制级别的代理架构，因为大模型通常只能控制单个决策。**想象一下上面的场景中，如果我们希望定义的`insert_db`不仅仅只是包含插入数据库，而是有一堆各式各样的工具，比如网络搜索，RAG等等，应该如何进一步的扩展呢？ 难道要做对每一个工具在`insert_db`节点下再通过`Router Function`做分支判断吗？虽然可行，但总归并不是高效的做法。

&emsp;&emsp;由此，我们接下来进一步给大家介绍`Tool Calling Agent`（工具调用代理）来高效的解决这一问题。

# 2. 工具调用代理
