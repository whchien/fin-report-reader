import time

import openai
from openai import OpenAI
from loguru import logger

from src.config import DATA_DIR, ASSISTANT_QUERY, ASSISTANT_NAME, ASSISTANT_PROMPT, OPENAI_MODEL, MAX_RETRIES, RETRY_DELAY

import time
import functools


def retry_on_exception(exception, retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            retry_count = 0
            while retry_count < retries:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    retry_count += 1
                    logger.info(f"Retry: {retry_count}. Exception: {e}")
                    time.sleep(delay)
                    continue
            logger.error(f"Max retries reached {retry_count}. Exception: {e}")
        return wrapper_retry

    return decorator_retry


class ReportAnalyst:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = None
        self.vector_store_id = None

    def init_rag_assistant(self) -> None:
        assistant = self.client.beta.assistants.create(
            name=ASSISTANT_NAME,
            instructions=ASSISTANT_PROMPT,
            model=OPENAI_MODEL,
            tools=[{"type": "file_search"}],
        )

        vector_store = self.client.beta.vector_stores.create(name="Financial Statements")
        logger.info("Assistant created: {}", assistant.id)
        logger.info("Vector store created: {}", vector_store.id)

        self.reinit(assistant.id, vector_store.id)

        self.client.beta.assistants.update(
            assistant_id=self.assistant_id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}},
        )

    def reinit(self, assistant_id: str, vector_store_id: str) -> None:
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id

    @retry_on_exception(openai.APIConnectionError)
    def upload_file_to_vector_store(self, path: str) -> bool:
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store_id, files=[open(path, "rb")],
        )
        logger.info("File batch created: {}", file_batch.id)
        return True

    @retry_on_exception(openai.APIConnectionError)
    def ask_document(self, query: str) -> str:
        logger.info(f"Querying document with {self.assistant_id} and {self.vector_store_id}")
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": query}],
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}}
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant_id
        )

        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text
        logger.info("Querying done!")
        return message_content.value

    def run(self, file_path: str) -> str:
        self.init_rag_assistant()
        _ = self.upload_file_to_vector_store(file_path)
        response = self.ask_document(ASSISTANT_QUERY)
        return response
