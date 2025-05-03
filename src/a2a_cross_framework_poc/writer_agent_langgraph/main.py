# writer_agent_langgraph/main.py

import uuid
import requests
import json
from a2a_cross_framework_poc.writer_agent_langgraph.agent_flow import create_writer_agent_graph

# Step 1: Run the LangGraph writer agent
graph = create_writer_agent_graph()
state = {"messages": [{"type": "human", "content": "Write a blog post on the A2A protocol"}]}
result = graph.invoke(state)

# Extract generated text from result
ai_message = result["messages"][-1]
generated_text = ai_message.content if hasattr(ai_message, 'content') else ai_message["content"]

print("\n=== Writer Agent Output ===")
print(generated_text)

# Step 2: Send it via A2A to editor/translator agent's RPC endpoint
a2a_payload = {
    "jsonrpc": "2.0",
    "id": f"task-{uuid.uuid4()}",
    "method": "tasks/send",
    "params": {
        "id": f"task-{uuid.uuid4()}",
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": f"Translate this blog post to Chinese:\n\n{generated_text}"
                }
            ]
        }
    }
}

print("\n=== Sending to Translator Agent via A2A ===")
response = requests.post("http://localhost:8001/rpc", json=a2a_payload)
response.raise_for_status()
translated = response.json()

print("\n=== Translated Output from Translator Agent ===")
artifact_parts = translated["result"]["artifacts"][0]["parts"]
translated_text = artifact_parts[0]["text"]["raw"] if isinstance(artifact_parts[0]["text"], dict) else artifact_parts[0]["text"]
print(translated_text)
