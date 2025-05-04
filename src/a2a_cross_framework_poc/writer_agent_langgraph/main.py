# src/a2a_cross_framework_poc/writer_agent_langgraph/main.py

import os
import uuid
import json
import requests
from dotenv import load_dotenv

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# ----- 1) Writer Agent Definition -----
class WriterState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def writer_tool_node(state: WriterState) -> WriterState:
    user_msg = next((m for m in state["messages"] if isinstance(m, HumanMessage)), None)
    instruction = user_msg.content if user_msg else "Write a blog on the A2A protocol."
    response = llm.invoke([HumanMessage(content=instruction)])
    return {"messages": state["messages"] + [response]}

def create_writer_agent_graph():
    graph = StateGraph(WriterState)
    graph.add_node("writer_tool", writer_tool_node)
    graph.set_entry_point("writer_tool")
    graph.set_finish_point("writer_tool")
    return graph.compile()


# ----- 2) Generate the English Blog -----
graph = create_writer_agent_graph()
initial_state = {"messages": [HumanMessage(content="Write a blog on the A2A protocol. within 20 words")]}

state = graph.invoke(initial_state)
blog_text = state["messages"][-1].content.strip()

print("\n=== Written Blog by Writer Agent ===\n")
print(blog_text)


# ----- 3) Discover Translator Agent -----
AGENT_URL       = "http://localhost:8001"
AGENT_CARD_URL  = f"{AGENT_URL}/.well-known/agent.json"
RPC_ENDPOINT    = f"{AGENT_URL}/rpc"   # no trailing slash

print("\n=== Discovering Translator Agent ===")
agent_card = requests.get(AGENT_CARD_URL).json()
print(json.dumps(agent_card, indent=2))


# ----- 4) Build & Send A2A JSON-RPC Task -----
print("\n=== Sending to Translator Agent via A2A ===")
task_id = str(uuid.uuid4())
payload = {
    "jsonrpc": "2.0",
    "id": task_id,
    "method": "tasks/send",
    "params": {
        "id": task_id,
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": f"Please translate this blog into Simplified Chinese only. Do not include any English:\n\n{blog_text}"
                }
            ]
        },
        "metadata": {}
    }
}

resp = requests.post(RPC_ENDPOINT, json=payload)
resp.raise_for_status()
result = resp.json()


# ----- 5) Extract & Print Only the Chinese -----
print("\n=== Chinese Blog Translation ===\n")
if "result" in result:
    artifacts = result["result"].get("artifacts", [])
    for art in artifacts:
        for part in art.get("parts", []):
            text_obj = part.get("text", {})
            raw = text_obj.get("raw")
            if isinstance(raw, str):
                print(raw.strip())
else:
    print("⚠️ A2A error:", result.get("error"))
