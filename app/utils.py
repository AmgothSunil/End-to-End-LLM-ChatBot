import os
import csv
from datetime import datetime
import mlflow
import logging
from mlflow.exceptions import MlflowException
from dotenv import load_dotenv

from app.config import load_params

load_dotenv(override=True)

# Load parameters
params = load_params('params.yaml')
utils_params = params['utils']

# Paths
log_dir_path = utils_params['log_dir_path']
utils_log_file_path = utils_params['utils_log_file_path']

# Ensure logging directory and chat log directories exist
os.makedirs(log_dir_path, exist_ok=True)

# Logger setup
logger = logging.getLogger("Utils")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_path = os.path.join(log_dir_path, utils_log_file_path)
file_handler = logging.FileHandler(file_path)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Prevent duplicate handlers
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def log_to_csv(question: str, response: str, file_path: str) -> None:
    """
    Save chat history (user question and model response) to a local CSV file.

    Args:
        question (str): The user’s input question.
        response (str): The LLM’s generated response.
        file_path (str): Path to the CSV file where logs will be stored.

    Returns:
        None

    Raises:
        FileNotFoundError: If the provided file path is invalid.
        OSError: If writing to the CSV file fails due to an IO error.
        Exception: For any unexpected errors during CSV writing.
    """
    try:
        logger.info("Saving chat history to CSV file: %s", file_path)

        with open(file_path, 'a', newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), question, response])

        logger.debug("User chat history successfully saved to CSV.")

    except FileNotFoundError as fnf_error:
        logger.error("Chat log file not found: %s", fnf_error, exc_info=True)
        raise

    except OSError as os_error:
        logger.error("IO error while writing chat history: %s", os_error, exc_info=True)
        raise

    except Exception as e:
        logger.exception("Unexpected error while saving chat history: %s", str(e))
        raise


def mlflow_init() -> mlflow:
    """
    Initialize MLflow tracking for experiment logging.

    Returns:
        mlflow: The initialized MLflow client instance.

    Raises:
        MlflowException: If MLflow tracking URI or experiment setup fails.
        Exception: For any other unexpected errors during initialization.
    """
    try:
        logger.info("Initializing MLflow tracking client...")

        mlflow.set_tracking_uri("https://dagshub.com/AmgothSunil/End-to-End-LLM-ChatBot.mlflow")
        mlflow.set_experiment("LLM Chatbot Experiments")

        logger.debug("MLflow successfully initialized for experiment tracking.")
        return mlflow

    except MlflowException as mlf_error:
        logger.error("MLflow initialization failed: %s", mlf_error, exc_info=True)
        raise

    except Exception as e:
        logger.exception("Unexpected error occurred during MLflow initialization: %s", str(e))
        raise


def log_to_mlflow(mlflow_client: mlflow, model_name: str, question: str, response: str) -> None:
    """
    Log chatbot parameters, metrics, and responses to MLflow.

    Args:
        mlflow_client (mlflow): The initialized MLflow tracking client.
        model_name (str): The name of the LLM model used.
        question (str): The user’s input question.
        response (str): The generated response from the LLM.

    Returns:
        None

    Raises:
        MlflowException: If logging to MLflow fails.
        ValueError: If provided arguments are empty or invalid.
        Exception: For any other unexpected errors during logging.
    """
    try:
        if not all([mlflow_client, model_name, question, response]):
            raise ValueError("All arguments (mlflow_client, model_name, question, response) must be provided.")

        logger.info("Logging chatbot run details to MLflow for model: %s", model_name)

        with mlflow.start_run(run_name=f"{model_name}_run"):
            mlflow.log_param("model_name", model_name)
            mlflow.log_param("question", question)
            mlflow.log_metric("response_length", len(response.split()))
            mlflow.log_text(response, "response.txt")

        logger.debug("Successfully logged chatbot run data to MLflow.")

    except MlflowException as mlf_error:
        logger.error("MLflow logging failed: %s", mlf_error, exc_info=True)
        raise

    except ValueError as val_err:
        logger.error("Invalid input to MLflow logging: %s", val_err, exc_info=True)
        raise

    except Exception as e:
        logger.exception("Unexpected error while logging to MLflow: %s", str(e))
        raise