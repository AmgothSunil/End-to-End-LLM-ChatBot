import os
import logging
import mysql.connector
from mysql.connector import Error
from app.config import load_params
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Load parameters from YAML config
params = load_params('params.yaml')
workbench_params = params['workbench_params']

log_dir_path = workbench_params['log_dir_path']
workbench_logs_file_path = workbench_params['workbench_logs_file_path']

# Ensure logging directory exists
os.makedirs(log_dir_path, exist_ok=True)

# Logger setup
logger = logging.getLogger("Workbench_Storage")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_path = os.path.join(log_dir_path, workbench_logs_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

# Formatter setup
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def create_mysql_connection():
    """
    Establish and return a MySQL database connection.
    """
    try:
        logger.info("Initializing MySQL database connection...")
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            port=os.getenv("MYSQL_PORT")
        )

        if conn.is_connected():
            logger.debug("Successfully connected to MySQL database.")
            return conn
        else:
            raise Exception("Failed to establish MySQL connection.")

    except Error as e:
        logger.error("MySQL connection error: %s", e)
        raise

    except Exception as e:
        logger.exception("Unexpected error during MySQL connection: %s", e)
        raise


def database_init():
    """
    Create the chat_history table if it doesn't exist.
    """
    try:
        conn = create_mysql_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_input TEXT NOT NULL,
                chatbot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        logger.debug("Chat history table initialized successfully.")

    except Error as e:
        logger.error("MySQL table initialization error: %s", e)
        raise

    except Exception as e:
        logger.exception("Unexpected error initializing table: %s", e)
        raise


def save_chathistory(user_input: str, bot_response: str):
    """
    Save user chat history to MySQL database.
    """
    try:
        conn = create_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chat_history (user_input, chatbot_response) VALUES (%s, %s)",
            (user_input, bot_response)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.debug("Chat history saved successfully in MySQL database.")

    except Error as e:
        logger.error("MySQL insert error: %s", e)
        raise

    except Exception as e:
        logger.exception("Unexpected error while saving chat history: %s", e)
        raise


def fetch_chathistory(limit: int):
    """
    Fetch recent chat history from MySQL database.
    """
    try:
        conn = create_mysql_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_input, chatbot_response FROM chat_history ORDER BY id DESC LIMIT %s", (limit,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        rows.reverse()
        context = "\n".join([f"User: {u}\nAssistant: {b}" for u, b in rows])

        logger.debug("Chat history fetched successfully.")
        return context

    except Error as e:
        logger.error("MySQL fetch error: %s", e)
        raise

    except Exception as e:
        logger.exception("Unexpected error while fetching chat history: %s", e)
        raise