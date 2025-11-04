import os
import logging
import mysql.connector
from dotenv import load_dotenv

from app.config import load_params

load_dotenv(override=True)

params = load_params("params.yaml")

rds_params = params['aws_rds_params']
log_dir_path = rds_params['log_dir_path']
db_logs_file_path = rds_params['db_logs_file_path']

# Ensure logging directory exists
os.makedirs(log_dir_path, exist_ok=True)

# Logger initialization
logger = logging.getLogger("RDS Storage")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_path = os.path.join(log_dir_path, db_logs_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

# set formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def create_connection():
    """Creating connection to the remote AWS RDS MySQL storage"""

    try:
        logger.info("Initializing connection to the remote AWS RDS MySQL storage.")

        conn = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )

        logger.debug("Connected to AWS RDS MySQL Successfully...")

        return conn

    except mysql.connector.Error as e:
        logger.error("Mysql connection failed: %s", e)
        raise
    
    except Exception as e:
        logger.error("Error occured while connection to remote storage: %s", e)


def database_init():
    """Initializing RDS Schema for Chat history"""

    try:
        logger.info("Initializing chat history table in rds database.")

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_input TEXT NOT NULL,
            chatbot_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        logger.debug("Chat History table created Successfully.")

    except Exception as e:
        logger.error("Unexpected error occured while creating chat history table: %s", e)
        raise


def save_chat(user_input: str, bot_response: str):
    """Save Chat history to the database"""

    try:
        logger.info("chat history saving to database")

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO chat_history (user_input, chatbot_response) VALUES (%s, %s)",
                (user_input, bot_response)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.debug("Chat history Successfully saved to database.")

    except Exception as e:
        logger.error("Error occured while saving chat history to database: %s", e)
        raise


def fetch_recent_chats(limit: int):
    """Get recent chats for chatbot context for conversation memory"""

    try:
        logger.info("Fetching recent chats.")

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_input, chatbot_response FROM chat_history ORDER BY id DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        rows.reverse()

        context = "\n".join([f"User: {u}\nAssistant: {b}" for u,b in rows])

        logger.debug("Recent chats fetched successfully.")

        return context

    except Exception as e:
        logger.error("Unexpected error occured while fetching chats from database: %s", e)
        return ""  # Return empty string