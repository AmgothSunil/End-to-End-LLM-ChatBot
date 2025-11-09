import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.core.config import load_params
from app.services.chatbot import Chatbot
from app.core.logger import setup_logger
from app.core.exception import AppException
from app.db.mango_database import AsyncMongoDatabase

load_dotenv()

# LangSmith tracing
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Load config and logger
params = load_params("config/params.yaml")
main_params = params.get("main", {})
main_log_file_path = main_params.get("fastapi_log_file_path", "fastapi.log")
logger = setup_logger("FastAPI", main_log_file_path)

#  Initialize MongoDB instance
mongo = AsyncMongoDatabase()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("App starting up...")
    # Motor connects lazily, so we just ensure client exists
    if mongo.client is None:
        mongo.client  # create client
    logger.info("MongoDB client initialized and ready.")
    
    yield  # App runs here
    
    # Shutdown
    await mongo.close_connection()
    logger.info("App shutting down. MongoDB connection closed.")


# FastAPI App
app = FastAPI(
    title="LLM Chatbot API (Async)",
    description="A fully async chatbot with MongoDB + LangChain + Gemini",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    """Schema for incoming chatbot requests."""
    question: str = Field(..., min_length=1)
    model: str = Field(default="gemini-2.5-flash")
    session_id: str


@app.get("/")
async def home() -> dict:
    """Health check endpoint."""
    logger.info("Root endpoint accessed.")
    return {"message": "Async LLM Chatbot API running successfully "}


@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """Async chat endpoint."""
    try:
        chatbot = Chatbot(request.model, request.question, request.session_id)
        response = await chatbot.generate_response()
        return {"model": request.model, "response": response}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected server error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error.")


if __name__ == "__main__":
    uvicorn.run("app.api.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)