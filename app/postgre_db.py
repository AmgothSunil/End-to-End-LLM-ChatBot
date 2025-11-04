import os
import logging
import psycopg2
from dotenv import load_dotenv
from app.config import load_params

# Load environment variables
load_dotenv(override=True)

# Load parameters from YAML config
params = load_params('params.yaml')
postgre_params = params['postgre_params']

log_dir_path = postgre_params['log_dir_path']
postgre_log_file_path = postgre_params['postgre_logs_file_path']

# Ensure logging directory exists
os.makedirs(log_dir_path, exist_ok=True)

# Logger setup
logger = logging.getLogger("RDS_Storage")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_path = os.path.join(log_dir_path, postgre_log_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

# Formatter setup
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def create_pg_connection():
    """
    Establish and return a PostgreSQL database connection.

    Returns:
        psycopg2.extensions.connection: Active PostgreSQL connection object.

    Raises:
        psycopg2.Error: If connection to PostgreSQL fails.
    """
    try:
        logger.info("Initializing PostgreSQL database connection...")

        conn = psycopg2.connect(
            dbname=os.getenv("PG_DB_NAME"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT")
        )

        logger.debug("Successfully established connection with PostgreSQL database.")
        return conn

    except psycopg2.Error as e:
        logger.error("Database connection error: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error occurred during PostgreSQL connection: %s", e)
        raise


def database_init():
    """
    Initialize the PostgreSQL database schema for storing chat history.

    Creates a table 'chat_history' if it does not already exist.
    """
    try:
        logger.info("Creating chat_history table if not exists...")

        conn = create_pg_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_input TEXT NOT NULL,
                chatbot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        logger.debug("Chat history table initialized successfully.")

    except psycopg2.Error as e:
        logger.error("Database initialization error: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error during database initialization: %s", e)
        raise


def save_chathistory(user_input: str, bot_response: str):
    """
    Save a single user–chatbot interaction to the PostgreSQL database.

    Args:
        user_input (str): The user’s input text.
        bot_response (str): The chatbot’s generated response.
    """
    try:
        logger.info("Saving chat history to PostgreSQL database...")

        conn = create_pg_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chat_history (user_input, chatbot_response) VALUES (%s, %s)",
            (user_input, bot_response)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.debug("Chat history saved successfully.")

    except psycopg2.Error as e:
        logger.error("Error saving chat history: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error while saving chat history: %s", e)
        raise


def fetch_chathistory(limit: int):
    """
    Retrieve recent chat history records for contextual chatbot memory.

    Args:
        limit (int): The number of most recent records to retrieve.

    Returns:
        str: Formatted chat context string combining user inputs and bot responses.
    """
    try:
        logger.info("Fetching chat history (limit=%s)...", limit)

        conn = create_pg_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_input, chatbot_response
            FROM chat_history
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        rows.reverse()  # Oldest first
        context = "\n".join([f"User: {u}\nAssistant: {b}" for u, b in rows])

        logger.debug("Chat history fetched successfully.")
        return context

    except psycopg2.Error as e:
        logger.error("Error fetching chat history: %s", e)
        raise

    except Exception as e:
        logger.error("Unexpected error occured while fetching chats from database: %s", e)
        return ""  # Return empty string