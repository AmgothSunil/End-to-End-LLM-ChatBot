import os
import logging
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from app.config import load_params
from app.sqlite_db import sqlite_init, save_chat_history, fetch_recent_chats

params = load_params('params.yaml')
chatbot_params = params['chatbot']

log_dir_path = chatbot_params['log_dir_path']
chatbot_log_file_path = chatbot_params['chatbot_log_file_path']
chat_history_limit = chatbot_params['chat_history_limit']

# Ensure logging directory exists
os.makedirs(log_dir_path, exist_ok=True)

# Logger setup
logger = logging.getLogger("Chatbot")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_path = os.path.join(log_dir_path, chatbot_log_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Prevent duplicate handlers
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# Load environment variables
load_dotenv(override=True)
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY is missing in the .env file")

# Initialize database

sqlite_init()
logger.info("SQLite database connection initialized successfully.")


# Prompt setup

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who answers user queries accurately and politely. "
               "You are aware of the previous conversation history provided below."),
    ("user", "Context:\n{context}\n\nQuestion: {input}")
])

# Output parser
output_parser = StrOutputParser()


# Main chatbot function

def generate_response(llm: str, question: str) -> str:
    """
    Generate a response to a user question using the specified language model.
    """
    try:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info("Initializing chatbot with model: %s", llm)

        # Fetch latest 5 messages as context
        context = fetch_recent_chats(limit=chat_history_limit)

        llm_model = ChatGroq(model=llm, api_key=groq_api_key)
        chain = prompt | llm_model | output_parser

        logger.debug("Generating LLM response...")
        response = chain.invoke({"input": question, "context": context})

        # Save interaction to DB
        save_chat_history(question, response)

        logger.info("Response generated successfully.")
        logger.debug("Chat history saved Succesfully.")
        return response

    except ValueError as ve:
        logger.error("Invalid input: %s", ve, exc_info=True)
        raise

    except KeyError as ke:
        logger.error("Missing configuration key: %s", ke, exc_info=True)
        raise

    except Exception as e:
        logger.exception("Unexpected error while generating response: %s", e)
        raise RuntimeError(f"Chatbot failed to generate response: {e}") from e