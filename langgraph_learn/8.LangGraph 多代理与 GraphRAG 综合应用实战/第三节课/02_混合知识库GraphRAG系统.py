# -*- coding: utf-8 -*-
"""
【案例】Multi-Agent 实现混合多知识库检索
============================================

本案例展示如何使用 LangGraph 和 Neo4j + Milvus 实现混合知识库检索系统

要点：
1. Neo4j 图数据库存储知识图谱 (GraphRAG)
2. Milvus 向量数据库存储文本块 (传统RAG)
3. Supervisor 架构协调 graph_kg 和 vec_kg 两个代理

案例说明：
构建一个混合知识库检索系统：
- graph_kg: 基于图知识库，擅长回答全局性问题
- vec_kg: 基于向量检索，擅长回答细节性问题
- Supervisor: 智能路由选择合适的检索方式
"""

# ============================================================
# 1. 环境配置
# ============================================================
import getpass
import os

from langchain_openai import ChatOpenAI

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
graph_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# ============================================================
# 2. GraphRAG 设置 (Neo4j)
# ============================================================
# 注意：以下配置需要替换为实际的连接信息
# graph = Neo4jGraph(
#     url='neo4j+s://your-instance.databases.neo4j.io',
#     username="neo4j",
#     password="your-password",
#     database="neo4j"
# )

# ============================================================
# 3. 传统 RAG 设置 (Milvus)
# ============================================================
# 注意：以下配置需要替换为实际的连接信息
# embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# vectorstore = Milvus.from_documents(
#     documents=splits,
#     collection_name="company_rag_milvus",
#     embedding=embeddings,
#     connection_args={
#         "uri": "https://your-instance.serverless.gcp-us-west1.cloud.zilliz.com",
#         "user": "your-user",
#         "password": "your-password",
#     }
# )

# ============================================================
# 4. 定义状态模式
# ============================================================
from langgraph.graph import StateGraph, MessagesState, START, END

class AgentState(MessagesState):
    next: str

# ============================================================
# 5. 定义图知识库代理 (GraphRAG)
# ============================================================
from langchain.chains import GraphCypherQAChain
from langchain_core.messages import HumanMessage

# 注意：以下代码需要有效的 graph 连接
# cypher_chain = GraphCypherQAChain.from_llm(
#     graph=graph,
#     cypher_llm=llm,
#     qa_llm=llm,
#     validate_cypher=True,
#     allow_dangerous_requests=True
# )

def graph_kg(state: AgentState):
    """基于图知识库的检索代理"""
    messages = state["messages"][-1]
    # response = cypher_chain.invoke(messages.content)
    # final_response = [HumanMessage(content=response["result"], name="graph_kg")]
    # 为了示例，返回占位响应
    final_response = [HumanMessage(content="GraphRAG response (需要配置Neo4j)", name="graph_kg")]
    return {"messages": final_response}

# ============================================================
# 6. 定义向量知识库代理 (传统RAG)
# ============================================================
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 注意：以下代码需要有效的 vectorstore 连接
# prompt = PromptTemplate(
#     template="""You are an assistant for question-answering tasks.
#     Use the following pieces of retrieved context to answer the question.
#     If you don't know the answer, just say that you don't know.
#     Use three sentences maximum and keep the answer concise:
#     Question: {question}
#     Context: {context}
#     Answer:
#     """,
#     input_variables=["question", "document"],
# )

# rag_chain = prompt | graph_llm | StrOutputParser()

def vec_kg(state: AgentState):
    """基于向量检索的代理"""
    messages = state["messages"][-1]
    # question = messages.content
    # retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    # docs = retriever.invoke(question)
    # generation = rag_chain.invoke({"context": docs, "question": question})
    # final_response = [HumanMessage(content=generation, name="vec_kg")]
    # 为了示例，返回占位响应
    final_response = [HumanMessage(content="Vector RAG response (需要配置Milvus)", name="vec_kg")]
    return {"messages": final_response}

# ============================================================
# 7. 定义 Supervisor
# ============================================================
from typing import Literal
from typing_extensions import TypedDict

members = ["graph_kg", "vec_kg"]
options = members + ["FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""
    next: Literal[*options]

def supervisor(state: AgentState):
    """Supervisor 负责管理对话并决定下一步调用哪个代理"""
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- graph_kg: Stores market and company information, built on a graph-based knowledge base, "
        "excels at answering broad and comprehensive questions.\n"
        "- vec_kg: Stores market and company information, constructed on a traditional semantic retrieval "
        "knowledge base, excels at answering detailed and fine-grained questions.\n"
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

# ============================================================
# 8. 构建图
# ============================================================
def chat(state: AgentState):
    """通用对话代理"""
    messages = state["messages"][-1]
    model_response = llm.invoke(messages.content)
    final_response = [HumanMessage(content=model_response.content, name="chatbot")]
    return {"messages": final_response}


builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("chat", chat)
builder.add_node("graph_kg", graph_kg)
builder.add_node("vec_kg", vec_kg)

# 每个子代理完成后向主管汇报
for member in members:
    builder.add_edge(member, "supervisor")

# 条件边根据 next 字段路由
builder.add_conditional_edges("supervisor", lambda state: state["next"])

# 设置入口点
builder.add_edge(START, "supervisor")

# 编译图
graph = builder.compile()

# ============================================================
# 9. 测试运行
# ============================================================
print("=" * 50)
print("案例：Multi-Agent 混合多知识库检索系统")
print("=" * 50)

print("\n--- 测试：查询数据库中的公司信息 ---")
# 注意：由于没有配置实际的Neo4j和Milvus连接，这里仅演示结构
print("系统架构：Supervisor + graph_kg + vec_kg")
print("graph_kg: 基于Neo4j图数据库的GraphRAG检索")
print("vec_kg: 基于Milvus向量数据库的传统RAG检索")

print("\n" + "=" * 50)
print("案例说明：")
print("=" * 50)
print("""
本案例实现了混合多知识库检索系统。

架构特点：
1. Supervisor 作为中央控制器
2. graph_kg 基于图知识库，擅长全局性问题
3. vec_kg 基于向量检索，擅长细节性问题

使用场景：
- 需要全局理解：选择 graph_kg
- 需要精确匹配：选择 vec_kg
- Supervisor 自动选择合适的检索方式

配置说明：
需要提供有效的 Neo4j Aura 和 Milvus Cloud 连接才能完整运行。
""")