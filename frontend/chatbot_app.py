import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend FastAPI URL
API_URL = os.getenv("API_URL")
if not API_URL:
    st.error("API_URL is missing in your .env file.")
    st.stop()

if not API_URL.endswith("/chat"):
    API_URL = f"{API_URL.rstrip('/')}/chat"

# Streamlit Page Setup
st.set_page_config(page_title="LLM Chatbot", page_icon="🤖", layout="wide")
st.title("LLM Chatbot (Google LLM + FastAPI)")

# Initialize session
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["history"] = []
    st.info("New chat session started!")

session_id = st.session_state["session_id"]
model = "gemini-2.5-flash"

# Session details
with st.expander("Session Details"):
    st.code(session_id, language="text")

# Chat input
if user_input := st.chat_input("Ask your question..."):
    payload = {
        "question": user_input,
        "model": model,
        "session_id": session_id,
    }

    try:
        with st.spinner("Thinking..."):
            response = requests.post(API_URL, json=payload, timeout=60)

        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                st.error("Backend returned non-JSON response.")
                st.stop()

            bot_reply = data.get("response", "No response received.")
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(bot_reply)

            st.session_state["history"].append({"role": "user", "content": user_input})
            st.session_state["history"].append({"role": "assistant", "content": bot_reply})
        else:
            try:
                err_detail = response.json().get("detail", response.text)
            except Exception:
                err_detail = response.text
            st.error(f"Server error [{response.status_code}]: {err_detail}")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")

# Show previous history
if st.session_state["history"]:
    st.divider()
    for msg in st.session_state["history"]:
        st.chat_message(msg["role"]).write(msg["content"])

# Start new chat button
if st.button("Start New Chat"):
    st.session_state.clear()
    st.rerun()