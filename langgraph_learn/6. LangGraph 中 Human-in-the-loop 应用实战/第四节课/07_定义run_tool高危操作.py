def run_tool(state):
    new_messages = []
    tool_calls = state["messages"][-1].tool_calls
    
    # tools =  [get_weather, insert_weather_to_db, query_weather_from_db, delete_weather_from_db]
    tools =  [delete_weather_from_db]
    tools = {t.name: t for t in tools}
    
    for tool_call in tool_calls:
        tool = tools[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        new_messages.append(
            {
                "role": "tool",
                "name": tool_call["name"],
                "content": result,
                "tool_call_id": tool_call["id"],
            }
        )
    return {"messages": new_messages}