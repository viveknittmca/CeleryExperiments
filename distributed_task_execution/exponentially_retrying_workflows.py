import random
import time

from celery import app
from celery.exceptions import Retry


@app.task(bind=True, max_retries=3)
def task_with_exponential_backoff(self, task_name):
    try:
        print(f"Executing {task_name}...")
        if random.random() < 0.3:
            raise Exception(f"{task_name} failed")
        return f"{task_name} completed"
    except Exception as e:
        delay = 2 ** self.request.retries  # Exponential delay: 2, 4, 8 seconds...
        raise self.retry(exc=e, countdown=delay)


# Applying Different Retry Strategies for Workflow vs Tasks
# To apply exponential backoff at the workflow level but linear retry at the task level, handle retries outside Celery
def execute_with_exponential_backoff(chain_workflow, max_retries=3):
    for attempt in range(max_retries):
        try:
            return chain_workflow.apply_async()
        except Retry:
            delay = 2 ** attempt  # Exponential: 2s, 4s, 8s...
            print(f"Workflow failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    print("Workflow failed after max retries.")
