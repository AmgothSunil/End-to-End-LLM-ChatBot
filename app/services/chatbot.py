import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.logger import setup_logger
from app.core.config import load_params
from app.core.exception import AppException
from app.db.mango_database import AsyncMongoDatabase

load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise EnvironmentError("GOOGLE_API_KEY is missing in the .env file")

params = load_params("config/params.yaml")
chatbot_params = params.get("chatbot", {})

chatbot_logs_file_path = chatbot_params.get("chatbot_logs_file_path", "chatbot.log")
chat_history_limit = chatbot_params.get("chat_history_limit", 5)

logger = setup_logger(name="Chatbot", log_file_name=chatbot_logs_file_path)

# Initialize async DB
mongo = AsyncMongoDatabase()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who answers user queries accurately and politely. "
               "You are aware of the previous conversation history provided below."),
    ("user", "Context:\n{context}\n\nQuestion: {input}")
])
output_parser = StrOutputParser()


class Chatbot:
    """Async Chatbot for handling user queries."""

    def __init__(self, llm: str, question: str, session_id: str):
        self.llm = llm
        self.question = question
        self.session_id = session_id

    async def generate_response(self) -> str:
        """Generate LLM response asynchronously."""
        try:
            if not self.question.strip():
                raise ValueError("Question cannot be empty.")

            logger.info(f"[Session {self.session_id}] Generating response using model: {self.llm}")

            # Fetch context from MongoDB
            context = await mongo.fetch_recent_chats(self.session_id, chat_history_limit)

            # Initialize LLM
            llm_model = ChatGoogleGenerativeAI(model=self.llm, api_key=gemini_api_key)
            chain = prompt | llm_model | output_parser

            # Async invocation
            response = await chain.ainvoke({"input": self.question, "context": context})

            if not response or not isinstance(response, str):
                response = "I'm sorry, I couldn't generate a valid response."

            # Save to DB asynchronously
            await mongo.save_chat(self.session_id, self.question, response)

            logger.info(f"[Session {self.session_id}] Response generated and saved.")
            return response

        except Exception as e:
            raise AppException(e, sys)