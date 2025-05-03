# src/a2a_cross_framework_poc/shared/json_rpc/server.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from a2a_cross_framework_poc.editor_agent_crewai.agent_config import get_translator_agent
from crewai import Task, Crew

router = APIRouter()

class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: dict

@router.post("/")
async def handle_rpc(rpc_req: JsonRpcRequest):
    if rpc_req.method == "tasks/send":
        task_id = rpc_req.params.get("id")
        message = rpc_req.params.get("message", {})
        text_to_translate = ""

        for part in message.get("parts", []):
            if part.get("type") == "text":
                text_to_translate = part.get("text", "")
                break

        translator = get_translator_agent()
        translation_task = Task(
        description=f"Translate the following text **into simplified Chinese only**, without repeating the English text.:\n{text_to_translate}",
        agent=translator,
        expected_output=""
        )

        crew = Crew(agents=[translator], tasks=[translation_task])
        result = crew.kickoff()
        final_text = next(iter(result.values())) if isinstance(result, dict) else result

        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "result": {
                "id": task_id,
                "sessionId": None,
                "status": {"state": "completed"},
                "artifacts": [{
                    "parts": [{
                        "type": "text",
                        "text": { "raw": final_text }
                    }],
                    "index": 0
                }],
                "metadata": {}
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": rpc_req.id,
        "error": {"code": -32601, "message": "Method not found"}
    }
