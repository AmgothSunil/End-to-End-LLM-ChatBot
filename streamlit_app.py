import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

# FastAPI backend URL 
API_URL = os.getenv("API_URL")

# Streamlit app title
st.set_page_config(page_title="LLM Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 LLM Chatbot (Google LLM + FastAPI)")

# Model selector
model = "gemini-2.5-flash"

# User input
question = st.text_area("Enter your question", height=100)

# Button
if st.button("Get Response"):
    if not question.strip():
        st.warning("Please enter a valid question.")
    else:
        try:
            with st.spinner("Generating response..."):
                response = requests.post(
                    API_URL,
                    json={"question": question, "model": model},
                    timeout=120
                )
            
            if response.status_code == 200:
                data = response.json()
                st.success("Response generated successfully!")
                st.markdown(f"### Model: `{data['model']}`")
                st.markdown(f"**Response:** {data['response']}")
            else:
                st.error(f"Server returned {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
