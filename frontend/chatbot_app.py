import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend FastAPI URL (set this in your .env )
API_URL = os.getenv("API_URL")

# Streamlit Page Setup
st.set_page_config(page_title="LLM Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 LLM Chatbot (Google LLM + FastAPI)")

# Generate or reuse a session ID
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["history"] = []  # Initializing chat history
    st.info("New chat session started!")

session_id = st.session_state["session_id"]
model = "gemini-2.5-flash"

# Display the session ID (optional)
with st.expander("Session Details"):
    st.code(session_id, language="text")

# Chat UI
user_input = st.text_area("Enter your question", height=100)

# When user clicks the button
if st.button("Get Response"):
    if not user_input.strip():
        st.warning("Please enter a valid question.")
    else:
        try:
            with st.spinner("Generating response..."):
                payload = {
                    "question": user_input,
                    "model": model,
                    "session_id": session_id,
                }
                response = requests.post(API_URL, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                bot_reply = data.get("response", "No response received.")
                st.divider()
                st.subheader("Response")
                st.write(bot_reply)
                st.session_state["history"].append(("user", user_input))
                st.session_state["history"].append(("bot", bot_reply))
            else:
                st.error(f"Server returned {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")

# Display chat history
if st.session_state["history"]:
    st.divider()
    st.subheader("Chat History")

    for role, message in st.session_state["history"]:
        if role == "user":
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)

# Button to reset the chat
if st.button("Start New Chat"):
    st.session_state.clear()
    st.rerun()