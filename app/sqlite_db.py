import os
import sqlite3
import logging
from sqlite3 import OperationalError, IntegrityError, DatabaseError

from app.config import load_params

# Load parameters
params = load_params("params.yaml")
sqlite_params = params["sqlite_params"]

# Directories
log_dir_path = sqlite_params["log_dir_path"]
db_logs_file_path = sqlite_params["db_logs_file_path"]
db_path = sqlite_params["db_path"]
output_limit = sqlite_params["output_limit"]


os.makedirs(log_dir_path, exist_ok=True)
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Logger setup
logger = logging.getLogger("SQLiteDB")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_path = os.path.join(log_dir_path, db_logs_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def sqlite_init() -> None:
    """Initialize SQLite database and create chat history table if not exists."""
    try:
        logger.info("Initializing SQLite database at %s", db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                chatbot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        logger.debug("SQLite database initialized successfully.")

    except OperationalError as oe:
        logger.error("Database operation failed: %s", oe, exc_info=True)
        raise

    except DatabaseError as de:
        logger.error("General database error: %s", de, exc_info=True)
        raise

    except Exception as e:
        logger.error("Error occurred while initializing SQLite database: %s", e, exc_info=True)
        raise

    finally:
        if 'conn' in locals():
            conn.close()


def save_chat_history(user_input: str, response: str):
    """Save user question and chatbot response to database"""

    try:
        logger.info("Saving chat history to database.")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (user_input, chatbot_response) VALUES (?, ?)",
        (user_input, response))

        conn.commit()
        conn.close()

        logger.debug("User input and chatbot response successfully saved to database.")

    except IntegrityError as ie:
        logger.error("Integrity constraint violated: %s", ie)
        raise

    except OperationalError as oe:
        logger.error("Operational error while saving chat: %s", oe)
        raise

    except DatabaseError as de:
        logger.error("Database error: %s", de)
        raise

    except Exception as e:
        logger.exception("Unexpected error while saving chat history: %s", e)
        raise

    finally:
        if 'conn' in locals():
            conn.close()


def fetch_recent_chats(limit: int):
    """Fetch recent 5 chats from database for chatbot context"""

    try:
        logger.info("fetching chat history for llm context")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_input, chatbot_response FROM chat_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )

        rows = cursor.fetchall()
        conn.close()

        rows.reverse()
        context = "\n".join([f"User: {u}\n Assistant: {b[-output_limit:]}" for u,b in rows])
        
        logger.debug("chat history fetched successfully.")

        return context

    except OperationalError as oe:
        logger.error("Operational error while fetching chat history: %s", oe)
        return ""

    except DatabaseError as de:
        logger.error("Database error while fetching chats: %s", de)
        return ""

    except Exception as e:
        logger.exception("Unexpected error while fetching chat history: %s", e)
        return ""
    
    finally:
        if 'conn' in locals():
            conn.close()
