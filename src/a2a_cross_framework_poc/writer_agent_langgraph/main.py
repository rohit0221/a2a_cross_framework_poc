# src/a2a_cross_framework_poc/writer_agent_langgraph/main.py

import requests
import uuid
import json

# Discover the translator agent card
AGENT_URL = "http://localhost:8001"
AGENT_CARD_URL = f"{AGENT_URL}/.well-known/agent.json"
RPC_ENDPOINT = f"{AGENT_URL}/rpc/"

print("\n=== Discovering Translator Agent ===")
agent_card = requests.get(AGENT_CARD_URL).json()
print(json.dumps(agent_card, indent=2))

# Create a blog post draft
blog_draft = """
# Understanding the A2A Protocol: Bridging Communication in the Digital Age

The A2A (Application-to-Application) protocol enables seamless communication between software agents. It allows agents built in different frameworks to exchange tasks, collaborate, and operate securely across boundaries.

This standard uses JSON-RPC 2.0, supports streaming updates and task artifacts, and defines agent discovery via Agent Cards. It's a foundational step toward modular, interoperable agentic systems.
"""

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
                    "text": f"Translate this blog post to Chinese:\n{blog_draft}"
                }
            ]
        },
        "metadata": {}
    }
}

response = requests.post(RPC_ENDPOINT, json=payload)
result = response.json()

print("\n=== Translated Output from Translator Agent ===")
artifacts = result.get("result", {}).get("artifacts", [])
for artifact in artifacts:
    for part in artifact.get("parts", []):
        print(part.get("text", {}).get("raw", "[No content]"))
