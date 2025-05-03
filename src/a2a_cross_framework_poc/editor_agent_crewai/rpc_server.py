# src/a2a_cross_framework_poc/editor_agent_crewai/rpc_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from uuid import uuid4
from crewai import Task, Crew
from a2a_cross_framework_poc.editor_agent_crewai.agent_config import get_translator_agent

app = FastAPI()

# JSON-RPC 2.0 request models
class TextPart(BaseModel):
    type: str
    text: str

class MessageModel(BaseModel):
    role: str
    parts: list[TextPart]

class SendParams(BaseModel):
    id: str
    message: MessageModel
    metadata: dict = Field(default_factory=dict)

class RPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: SendParams

@app.post("/rpc")
async def handle_rpc(req: RPCRequest):
    if req.method != "tasks/send":
        raise HTTPException(status_code=400, detail="Unsupported method")

    # Extract text to translate
    try:
        user_text = req.params.message.parts[0].text
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid message format")

    # Delegate to translator agent via CrewAI
    translator = get_translator_agent()
    task_desc = f"Translate the following to Chinese:\n{user_text}"
    task = Task(description=task_desc, agent=translator, expected_output="")
    crew = Crew(agents=[translator], tasks=[task], verbose=False)
    results = crew.kickoff()
    # Retrieve result string
    translated = next(iter(results.values())) if isinstance(results, dict) else results

    # Build JSON-RPC response
    response = {
        "jsonrpc": "2.0",
        "id": req.id,
        "result": {
            "id": req.params.id,
            "sessionId": str(uuid4()),
            "status": {"state": "completed"},
            "artifacts": [
                {"parts": [{"type": "text", "text": translated}], "index": 0}
            ],
            "metadata": {}
        }
    }
    return response
