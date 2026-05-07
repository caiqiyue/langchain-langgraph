## <center>第五阶段、Multi-Agent实现混合多知识库检索</center>

&emsp;&emsp;在本案例中，我们将探讨和实践如何使用 `Neo4j` 和 `LangChain` 来实现 GraphRAG。 `Neo4j` 是一种流行的图形数据库，用于以类似图形的结构表示数据，其中实体是节点，实体之间的关系是边。当与 `LangChain` 集成时，`Neo4j` 就变成了使用结构化图数据执行`RAG` 的强大工具。`Neo4j`的使用主要有两种方式，一种是本地安装，另一种则是可以使用云服务，这里我们选择使用`Neo4j Aura`，它提供了一个免费的实例可以供我们使用。

### 1. 配置 Neo4j 图数据库实例

&emsp;&emsp;首先，登录该地址注册免费账户：https://console.neo4j.io/?product=aura-db&tenant=2afe251b-59ae-5517-9598-84fc5d57b0b5

![Neo4j注册图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526255.png)

&emsp;&emsp;创建`Neo4j`实例。

![创建实例图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526256.png)

&emsp;&emsp;这里可以选择一个免费的实例。

![选择免费实例图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526257.png)

&emsp;&emsp;创建的时候记得保存密码，将用于后续的连接。

![保存密码图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526258.png)

&emsp;&emsp;等待创建完成。

![等待创建图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526259.png)

&emsp;&emsp;创建完成后，将会生成一个远程连接的`Uri`。

![连接URI图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221530776.png)

### 2. 创建图索引及构建 GraphRAG Agent

&emsp;&emsp;在将数据 引入`Neo4j`图数据库之前，一般来说我们会将数据（例如 .txt 或 .csv 文件）拆分为可管理的块。可以使用`LangChain`框架的 `TextLoader` 和 `RecursiveCharacterTextSplitter` 来完成。用于演示目的，我们此处不进行分块，将完整的文档作为一个 `TextUnit`进行图属性的提取。

```python
# 打开文件，并赋予读取模式 'r'
with open('./company.txt', 'r', encoding="utf-8") as file:
    # 读取文件的全部内容
    content = file.read()
    print(content)
```

&emsp;&emsp;转化成`Document`对象。

```python
from langchain_core.documents import Document

documents = [Document(page_content=content)]
```

```python
documents
```

&emsp;&emsp;准备好数据后，我们可以使用 `langchain_experimental.graph_transformers` 中的 `LLMGraphTransformer` 将其摄取到 `Neo4j` 中。该工具会自动将文档转换为图格式。`LLMGraphTransformer` 能够以两种完全独立的模式运行：
- Tool-Based 模式（默认）：当使用的大模型支持结构化输出或函数调用时，该模式利用内置的`with_structured_output`来使用工具。工具规范定义了输出格式，确保以结构化、预定义的方式提取实体和关系。
- 基于提示的模式（回退）：在使用的大模型不支持工具或函数调用的情况下， 该转换器回退到纯粹提示驱动的方法。该模式使用`few-shot`提示来定义输出格式，指导大模型以基于文本的方式提取实体和关系。然后通过自定义函数解析结果，该函数将大模型的输出转换为 `JSON` 格式。该 `JSON` 用于填充节点和关系。

```python
# GraphRAG Setup
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# 创建图数据库示例
graph = Neo4jGraph(url='neo4j+s://e2f16b1a.databases.neo4j.io',  # 替换为自己的
                  username="neo4j",  # 替换为自己的
                  password="WvNNfKFQHwZurjccM0MFjz6SuKkuFNdT9y9R9E53CME", #替换为自己的
                  database="neo4j" # 替换为自己的
                  )

graph_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
```

&emsp;&emsp;使用`convert_to_graph_documents`函数处理文档，进行实体和关系的提取。

```python
# 图转换器配置
graph_transformer = LLMGraphTransformer(
    llm=graph_llm,
    allowed_nodes=["公司", "产品", "技术", "市场", "活动", "合作伙伴"],    # 可以自定义节点
    allowed_relationships=["推出", "参与", "合作", "位于", "开发"],       # 可以自定义关系
)


graph_transformer = LLMGraphTransformer(llm=graph_llm)

graph_documents = graph_transformer.convert_to_graph_documents(documents)

graph.add_graph_documents(graph_documents)

print(f"Graph documents: {len(graph_documents)}")
print(f"Nodes from 1st graph doc:{graph_documents[0].nodes}")
print(f"Relationships from 1st graph doc:{graph_documents[0].relationships}")
```

&emsp;&emsp;完成后，可以查看`Neo4j Aura` 平台查看存储的节点。

![Neo4j节点图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526263.png)

&emsp;&emsp;登录。

![Neo4j登录图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526264.png)

&emsp;&emsp;进入后即可查看到生成的知识图谱。

![知识图谱图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221545064.png)

&emsp;&emsp;`Neo4j` 通过利用图算法（例如 PageRank 或社区检测）来检索子图。这些算法识别相关实体的集群，`LangChain` 从 `Neo4j` 检索子图并通过大模型生成响应，这里可以使用到`GraphCypherQAChain`工具。

```python
from langchain.chains import GraphCypherQAChain

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm,
    qa_llm=llm,
    validate_cypher=True, # Validate relationship directions
    verbose=True,
    allow_dangerous_requests=True
)
cypher_chain.invoke("小米科技有限责任公司推出了哪些创新技术？")
```

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm,
    qa_llm=llm,
    validate_cypher=True, # Validate relationship directions
    verbose=True,
    allow_dangerous_requests=True
)
cypher_chain.invoke("华为技术有限公司与哪些教育机构建立了合作？")
```

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm,
    qa_llm=llm,
    validate_cypher=True, # Validate relationship directions
    verbose=True,
    allow_dangerous_requests=True
)
cypher_chain.invoke("都有哪些公司在我的数据库中？")
```

```python
cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm,
    qa_llm=llm,
    validate_cypher=True,
    allow_dangerous_requests=True
)
response = cypher_chain.invoke("都有哪些公司在我的数据库中？")
```

```python
response["result"]
```

### 3. 创建传统 RAG Agent

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

chunk_size = 250
chunk_overlap = 30
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

# Split
splits = text_splitter.split_documents(documents)
splits
```

&emsp;&emsp;这里我们同样使用免费的在线`milvus`实例，地址如下：https://cloud.zilliz.com/login?redirect=/orgs

![Milvus注册图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221559348.png)

&emsp;&emsp;然后创建索引。

![创建索引图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526248.png)

&emsp;&emsp;选择免费实例。

![选择免费实例图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526249.png)

&emsp;&emsp;注意：这里需要保存好用户名和密码，用于接下来的远程连接。

![保存凭据图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526250.png)

&emsp;&emsp;等待创建完成后。

![等待完成图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221526252.png)

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
```

&emsp;&emsp;通过如下代码构建向量索引，并存储到云端的`Milvus`向量数据库中。

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_milvus import Milvus


# User: db_33fcec99d39aeeb
# Password: Jw7+<}Yy*Cx!9(z*

# Add to Milvus
vectorstore = Milvus.from_documents(
    documents=splits,
    collection_name="company_rag_milvus",
    embedding=embeddings,
    connection_args={
        "uri": "https://in03-33fcec99d39aeeb.serverless.gcp-us-west1.cloud.zilliz.com",
        "user": "db_33fcec99d39aeeb",
        "password": "Jw7+<}Yy*Cx!9(z*",
    }
)
```

![Milvus确认图](https://muyu20241105.oss-cn-beijing.aliyuncs.com/images/202411221605854.png)

```python
from langchain.prompts import PromptTemplate
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

# 提示
prompt = PromptTemplate(
    template="""You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    Use three sentences maximum and keep the answer concise:
    Question: {question}
    Context: {context}
    Answer:
    """,
    input_variables=["question", "document"],
)


# 数据预处理
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



# 构建传统的RAG Chain
rag_chain = prompt | graph_llm | StrOutputParser()

# 运行
question = "我的知识库中都有哪些公司信息"

# 构建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

# 执行检索
docs = retriever.invoke("question")

docs
```

&emsp;&emsp;运行 `RAG_chain`,生成最终的回复。

```python
generation = rag_chain.invoke({"context": docs, "question": question})
print(generation)
```

&emsp;&emsp;构建传统 `RAG` 的`Agent`节点:

```python
def vec_kg(state: AgentState):

    messages = state["messages"][-1]

    prompt = PromptTemplate(
        template="""You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise:
        Question: {question}
        Context: {context}
        Answer:
        """,
        input_variables=["question", "document"],
    )


    # 构建传统的RAG Chain
    rag_chain = prompt | graph_llm | StrOutputParser()
    # 运行
    question = "我的知识库中都有哪些公司信息"

    # 构建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    # 执行检索
    docs = retriever.invoke("question")
    generation = rag_chain.invoke({"context": docs, "question": question})

    final_response = [HumanMessage(content=generation, name="vec_kg")]

    return {"messages": final_response}
```

### 4. 构建混合知识库检索多代理系统

```python
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str
```

```python
def graph_kg(state: AgentState):
    messages = state["messages"][-1]

    response = cypher_chain.invoke(messages.content)
    final_response = [HumanMessage(content=response["result"], name="graph_kg")]
    return {"messages": final_response}
```

```python
def db_node(state: AgentState):
    result = db_agent.invoke(state)
    return {
        "messages": [
            HumanMessage(content=result["messages"][-1].content, name="sqler")
        ]
    }


def code_node(state: AgentState):
    result = code_agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, name="coder")]
    }
```

```python
def chat(state: AgentState):
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chatbot")]
    return {"messages": final_response}
```

&emsp;&emsp;新增两个不同的数据库代理节点：

```python
members = ["graph_kg", "vec_kg"]
options = members + ["FINISH"]
```

```python
from typing import Literal
from typing_extensions import TypedDict
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""

    next: Literal[*options]
```

&emsp;&emsp;`Literal`是`Python`的`typing`模块中的一个类型，用于定义一个变量的具体值的类型限制。当使用`Literal`时，实际上是在告诉`Python`，变量的值必须是指定的几个值中的一个。而 `next: Literal["chat", "coder", "sqler"]`意味着`next`属性只能赋予三个字符串值之一："chat"、"coder"、"sqler"或"FINISH"， 分别用来表示使用哪一个子代理来执行任务，或者直接通过`END`结束当前的图。

```python
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

def supervisor(state: AgentState):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- chat: Responds directly to user inputs using natural language.\n"
        "- graph_kg: Stores market and company information, built on a graph-based knowledge base, excels at answering broad and comprehensive questions.\n"
        "- vec_kg: Stores market and company information, constructed on a traditional semantic retrieval knowledge base, excels at answering detailed and fine-grained questions.\n"
        "Given the following user request, respond with the worker to act next."
        " Each worker will perform a task and respond with their results and status."
        " When finished, respond with FINISH."
    )

    messages = [{"role": "system", "content": system_prompt},] + state["messages"]

    response = llm.with_structured_output(Router).invoke(messages)

    next_ = response["next"]

    if next_ == "FINISH":
        next_ = END

    return {"next": next_}
```

```python
builder = StateGraph(AgentState)

# builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("coder", db_node)
builder.add_node("sqler", code_node)
builder.add_node("graph_kg", graph_kg)
builder.add_node("vec_kg", vec_kg)
```

&emsp;&emsp;然后让每个子代理在完成工作后总是向主管"汇报"，即需要构建它们之间的边。如下所示：

```python
for member in members:
    # 我们希望我们的工人在完成工作后总是向主管"汇报"
    builder.add_edge(member, "supervisor")
```

&emsp;&emsp;然后在图状态中填充`next`字段，路由到具体的某个节点或者结束图的运行，从来指定如何执行接下来的任务。

```python
builder.add_conditional_edges("supervisor", lambda state: state["next"])

# 添加开始和节点
builder.add_edge(START, "supervisor")

# 编译图
graph = builder.compile()
```

```python
from IPython.display import Image, display

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
```

&emsp;&emsp;编译完成后，就可以进行问答了，这里我们测试几轮不同的问题类型：

```python
for chunk in graph.stream({"messages": "都有哪些公司在我的数据库中。"}, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
```

## 拓展思考

### 1. 深度概念

&emsp;&emsp;**混合知识库检索的优势是什么？**

&emsp;&emsp;混合知识库检索结合了GraphRAG和传统向量检索的优势：
- **GraphRAG**：擅长回答需要全局理解和多跳推理的复杂问题
- **向量检索**：擅长回答需要精确匹配细节的简单问题
- **智能路由**：Supervisor根据问题类型自动选择合适的检索方式

&emsp;&emsp;**Neo4j和Milvus在GraphRAG中分别扮演什么角色？**

&emsp;&emsp;两个数据库在系统中承担不同职责：
- **Neo4j**：存储结构化的知识图谱，支持基于图算法的复杂查询
- **Milvus**：存储向量化的文本块，支持快速的语义相似度检索

&emsp;&emsp;**如何选择合适的知识库进行查询？**

&emsp;&emsp;选择依据查询类型：
- 需要全局主题理解：选择GraphRAG
- 需要精确细节匹配：选择向量检索
- 复杂多跳问题：优先GraphRAG
- 简单事实查询：优先向量检索

&emsp;&emsp;**Supervisor在混合知识库系统中的路由策略？**

&emsp;&emsp;Supervisor根据worker的专长进行智能路由：
- graph_kg：处理需要图结构知识的复杂问题
- vec_kg：处理需要细粒度匹配的简单问题
- chat：处理一般对话和任务分发
