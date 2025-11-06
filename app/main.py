import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from app.config import load_params
from app.chatbot import generate_response

load_dotenv()

# Langsmith Tracing
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = os.getenv("LANGCHAIN_PROJECT")
os.environ['LANGCHAIN_TRACING_V2'] = 'true'

# Configuration & Logging

# Load parameters
params = load_params("params.yaml")
main_params = params["main"]

# Paths
log_dir_path = main_params["log_dir_path"]
main_log_file_path = main_params["main_log_file_path"]

# Ensure directories exist
os.makedirs(log_dir_path, exist_ok=True)

# Logger setup
logger = logging.getLogger("Main")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_path = os.path.join(log_dir_path, main_log_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Prevent duplicate handlers
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)



# FastAPI App Initialization

app = FastAPI(
    title="LLM Chatbot API",
    description="A production-grade chatbot powered by Groq LLM with MLflow tracking.",
    version="1.0.0",
)

# Request Model

class ChatRequest(BaseModel):
    """Schema for incoming chatbot requests."""
    question: str
    model: str = "gemini-2.5-flash"
    session_id: str

# API Endpoints

@app.get("/")
def home() -> dict:
    """
    Root endpoint for health check or greeting.

    Returns:
        dict: A welcome message indicating the API is active.
    """
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to the LLM Chatbot API!"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    """
    Handle user chat requests, generate a response using the selected LLM,
    log chat history locally, and track the run using MLflow.

    Args:
        request (ChatRequest): Contains the user's question and selected model.

    Returns:
        dict: Contains the model used, user question, and generated response.

    Raises:
        HTTPException: If the chatbot fails to generate a response or internal error occurs.
    """
    try:
        logger.info("Received chat request for model: %s", request.model)

        # Generate response using chatbot
        response = generate_response(request.model, request.question, request.session_id)
        logger.debug("Chatbot response generated successfully.")
    
        return {
            "model": request.model,
            "session_id": request.session_id,
            "question": request.question,
            "response": response,
        }

    except ValueError as val_err:
        logger.error("Validation error in chat input: %s", val_err, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid input: {val_err}")

    except HTTPException as http_err:
        logger.error("HTTP exception occurred: %s", http_err.detail, exc_info=True)
        raise

    except Exception as e:
        logger.exception("Unexpected error in chat endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error occurred.")



# Run the FastAPI App
if __name__ == "__main__":
    """
    Entry point for running the FastAPI server.

    Launches the chatbot API with Uvicorn on host 0.0.0.0:8000.
    """
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)