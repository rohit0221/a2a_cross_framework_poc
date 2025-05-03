from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv
load_dotenv()
class WriterState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def writer_tool_node(state: WriterState) -> WriterState:
    user_message = next((m for m in state["messages"] if isinstance(m, HumanMessage)), None)
    instruction = user_message.content if user_message else "Write something about the A2A protocol."

    response = llm.invoke([HumanMessage(content=instruction)])

    return {
        "messages": state["messages"] + [response]
    }

def create_writer_agent_graph():
    graph = StateGraph(WriterState)
    graph.add_node("writer_tool", writer_tool_node)
    graph.set_entry_point("writer_tool")
    graph.set_finish_point("writer_tool")
    return graph.compile()
