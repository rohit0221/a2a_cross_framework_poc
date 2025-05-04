import streamlit as st
import requests
import uuid
import json

WRITER_RPC = "http://localhost:8000/rpc"
TRANSLATOR_RPC = "http://localhost:8001/rpc"

st.title("📝 A2A Blog Generator + Translator")

topic = st.text_input("Enter blog topic:", "")
submit = st.button("Generate + Translate")

if submit and topic:
    with st.spinner("Calling Writer Agent..."):
        task_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": topic}]
                },
                "metadata": {}
            }
        }
        writer_resp = requests.post(WRITER_RPC, json=payload).json()
        eng_text = writer_resp["result"]["artifacts"][0]["parts"][0]["text"]["raw"]

    st.markdown("### ✍️ English Blog")
    st.text_area("English Output", eng_text, height=200)

    with st.spinner("Sending to Translator Agent..."):
        trans_id = str(uuid.uuid4())
        trans_payload = {
            "jsonrpc": "2.0",
            "id": trans_id,
            "method": "tasks/send",
            "params": {
                "id": trans_id,
                "message": {
                    "role": "user",
                    "parts": [{
                        "type": "text",
                        "text": f"Translate this to Chinese:\n{eng_text}"
                    }]
                },
                "metadata": {}
            }
        }
        trans_resp = requests.post(TRANSLATOR_RPC, json=trans_payload).json()
        zh_text = trans_resp["result"]["artifacts"][0]["parts"][0]["text"]["raw"]

    st.markdown("### 🌏 Translated Blog (Simplified Chinese)")
    st.text_area("Chinese Output", zh_text, height=200)
