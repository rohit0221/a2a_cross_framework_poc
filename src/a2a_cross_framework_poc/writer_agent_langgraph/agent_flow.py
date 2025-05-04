from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# ✅ Load OpenAI API key from .env
load_dotenv()

# Define the state schema
class WriterState(TypedDict):
    messages: Annotated[list, add_messages]

# Instantiate the model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Define the writer tool logic
def writer_tool_node(state: WriterState) -> WriterState:
    user_msg = next((m for m in state["messages"] if isinstance(m, HumanMessage)), None)
    instruction = user_msg.content if user_msg else "Write a blog on the A2A protocol."
    response = llm.invoke([HumanMessage(content=instruction)])
    return {"messages": state["messages"] + [response]}

# Create the LangGraph graph
def create_writer_agent_graph():
    graph = StateGraph(WriterState)
    graph.add_node("writer_tool", writer_tool_node)
    graph.set_entry_point("writer_tool")
    graph.set_finish_point("writer_tool")
    return graph.compile()
