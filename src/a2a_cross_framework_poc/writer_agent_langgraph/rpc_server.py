from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

AGENT_CARD_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "shared", "agent_cards", "writer_card.json"
)

@app.get("/.well-known/agent.json")
async def get_agent_card():
    with open(AGENT_CARD_PATH, "r", encoding="utf-8") as f:
        card = json.load(f)
    return JSONResponse(content=card)
