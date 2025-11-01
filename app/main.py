import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import load_params
from app.chatbot import generate_response
from app.utils import log_to_csv, mlflow_init, log_to_mlflow



# Configuration & Logging

# Load parameters
params = load_params("params.yaml")
main_params = params["main"]

# Paths
log_dir_path = main_params["log_dir_path"]
main_log_file_path = main_params["main_log_file_path"]
chat_logs_file_path = main_params["chat_logs_file_path"]

# Ensure directories exist
os.makedirs(log_dir_path, exist_ok=True)
os.makedirs(os.path.dirname(chat_logs_file_path), exist_ok=True)

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

# Initialize MLflow
try:
    mlflow_client = mlflow_init()
    logger.info("MLflow client initialized successfully.")
except Exception as e:
    logger.error("Failed to initialize MLflow client: %s", e, exc_info=True)
    mlflow_client = None



# Request Model

class ChatRequest(BaseModel):
    """Schema for incoming chatbot requests."""
    question: str
    model: str = "llama-3.1-8b-instant"



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
        response = generate_response(request.model, request.question)
        logger.debug("Chatbot response generated successfully.")

        # Log chat to CSV
        log_to_csv(request.question, response, chat_logs_file_path)
        logger.debug("Chat history saved to CSV at: %s", chat_logs_file_path)

        # Log to MLflow (if initialized)
        if mlflow_client:
            log_to_mlflow(mlflow_client, request.model, request.question, response)
            logger.debug("Chat session logged to MLflow.")
        else:
            logger.warning("MLflow client not initialized; skipping MLflow logging.")

        return {
            "model": request.model,
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