# src/a2a_cross_framework_poc/editor_agent_crewai/rpc_server.py

import os
import json
from typing import Any, Dict, Literal
from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Task, Crew
from a2a_cross_framework_poc.editor_agent_crewai.agent_config import get_translator_agent

app = FastAPI(title="Translator A2A RPC Server")

# 1) Serve the Agent Card
@app.get("/.well-known/agent.json")
async def agent_card():
    card_path = os.path.join(
        os.path.dirname(__file__),
        "..", "shared", "agent_cards", "editor_card.json"
    )
    return json.loads(open(card_path, encoding="utf-8").read())

# 2) JSON-RPC request model
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

# 3) The /rpc endpoint
@app.post("/rpc")
async def rpc_handler(rpc_req: JsonRpcRequest):
    if rpc_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract the text to translate
    message = rpc_req.params.get("message", {})
    text_to_translate = ""
    for part in message.get("parts", []):
        if part.get("type") == "text":
            text_to_translate = part.get("text", "")
            break

    # Run CrewAI translation
    translator = get_translator_agent()
    translation_task = Task(
        description=f"Translate to Chinese:\n\n{text_to_translate}",
        agent=translator,
        expected_output=""
    )
    crew = Crew(agents=[translator], tasks=[translation_task])
    results = crew.kickoff()

    if isinstance(results, dict):
        val = next(iter(results.values()))
    else:
        val = results

    if isinstance(val, dict) and "raw" in val:
        translated_str = val["raw"]
    else:
        translated_str = str(val)

    # Final JSON-RPC response (fully A2A compliant)
    return {
        "jsonrpc": "2.0",
        "id": rpc_req.id,
        "result": {
            "id": rpc_req.params.get("id"),
            "sessionId": None,
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": {"raw": translated_str}}
                    ],
                    "index": 0,
                    "append": False,
                    "lastChunk": True
                }
            ],
            "metadata": {}
        }
    }
