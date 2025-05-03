# src/a2a_cross_framework_poc/editor_agent_crewai/rpc_server.py

from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

from a2a_cross_framework_poc.shared.json_rpc import server as rpc_server  # 🟢 ensure this import works

app = FastAPI()

# Mount the JSON-RPC router at /rpc
app.include_router(rpc_server.router, prefix="/rpc")  # 🟢 ACTUALLY mounts the /rpc path

@app.get("/.well-known/agent.json")
async def get_agent_card():
    agent_card_path = os.path.join(
        os.path.dirname(__file__), "..", "shared", "agent_cards", "editor_card.json"
    )
    return FileResponse(agent_card_path, media_type="application/json")
