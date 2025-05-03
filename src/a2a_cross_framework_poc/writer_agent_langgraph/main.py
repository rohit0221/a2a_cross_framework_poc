# src/a2a_cross_framework_poc/writer_agent_langgraph/main.py

import requests
import uuid
import json
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# === Define Writer Agent ===
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

# === Generate Blog ===
graph = create_writer_agent_graph()
initial_state = {"messages": [HumanMessage(content="Write a blog on the A2A protocol.")]}
state = graph.invoke(initial_state)
blog_output = state["messages"][-1].content

print("\n=== Written Blog by Writer Agent ===")
print(blog_output)

# === Discover Translator Agent ===
AGENT_URL = "http://localhost:8001"
AGENT_CARD_URL = f"{AGENT_URL}/.well-known/agent.json"
RPC_ENDPOINT = f"{AGENT_URL}/rpc"  # ✅ no trailing slash

print("\n=== Discovering Translator Agent ===")
try:
    agent_card = requests.get(AGENT_CARD_URL).json()
    print(json.dumps(agent_card, indent=2))
except Exception as e:
    print(f"❌ Failed to fetch agent card: {e}")
    exit(1)

# === Build A2A Task Payload ===
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
                    "text": f"Please translate this blog to Simplified Chinese only. Don't include English:\n{blog_output}"
                }
            ]
        },
        "metadata": {}
    }
}

# === Send JSON-RPC Task ===
try:
    response = requests.post(RPC_ENDPOINT, json=payload)
    response.raise_for_status()
    result = response.json()
except Exception as e:
    print(f"❌ Failed to send or parse A2A response: {e}")
    exit(1)

# === Parse and Print Translation ===
print("\n=== Translated Output from Translator Agent ===")
if "result" in result:
    artifacts = result["result"].get("artifacts", [])
    if artifacts:
        for artifact in artifacts:
            for part in artifact.get("parts", []):
                text_obj = part.get("text", {})
                print(text_obj.get("raw", "[Missing raw field]"))
    else:
        print("⚠️ No artifacts returned.")
else:
    print("❌ A2A error:", result.get("error", "[No error message]"))
