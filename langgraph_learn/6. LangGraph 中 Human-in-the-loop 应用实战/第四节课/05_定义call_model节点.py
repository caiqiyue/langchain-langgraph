def call_model(state):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}