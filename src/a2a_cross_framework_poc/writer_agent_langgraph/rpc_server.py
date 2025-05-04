import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal

from langchain_core.messages import HumanMessage
from a2a_cross_framework_poc.writer_agent_langgraph.agent_flow import create_writer_agent_graph

app = FastAPI(title="Writer A2A RPC Server")

# 1) Serve the Agent Card
@app.get("/.well-known/agent.json")
async def agent_card():
    card_path = os.path.join(
        os.path.dirname(__file__),
        "..", "shared", "agent_cards", "writer_card.json"
    )
    return json.loads(open(card_path, encoding="utf-8").read())

# 2) JSON-RPC request model
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

# 3) /rpc handler for tasks/send
@app.post("/rpc")
async def rpc_handler(rpc_req: JsonRpcRequest):
    if rpc_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract topic from parts
    message = rpc_req.params.get("message", {})
    topic = "Write a blog on the A2A protocol."
    for part in message.get("parts", []):
        if part.get("type") == "text":
            topic = part.get("text", topic)
            break

    # Run LangGraph Writer Flow
    graph = create_writer_agent_graph()
    initial_state = {"messages": [HumanMessage(content=topic)]}
    state = graph.invoke(initial_state)
    blog_text = state["messages"][-1].content.strip()

    # Return A2A-compliant response
    return {
        "jsonrpc": "2.0",
        "id": rpc_req.id,
        "result": {
            "id": rpc_req.params.get("id"),
            "sessionId": "writer-session-1",
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": {"raw": blog_text}}
                    ],
                    "index": 0,
                    "append": False,
                    "lastChunk": True
                }
            ],
            "metadata": {}
        }
    }
