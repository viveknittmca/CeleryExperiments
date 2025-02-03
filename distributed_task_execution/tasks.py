# Celery Task Definition
from celery import Celery
from celery.schedules import crontab
# from celery.exceptions import Retry
import random
import time

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task(bind=True, max_retries=3)
def execute_task(self, task_name):
    import random
    print(f"Executing {task_name}")
    if random.random() < 0.2:  # Simulate failure
        raise self.retry(exc=Exception(f"{task_name} failed"), countdown=2)
    return f"{task_name} completed"


@app.task(bind=True, max_retries=3)
def task_function(self, task_name):
    """Simulate task execution with failure possibility"""
    print(f"Executing {task_name}...")
    time.sleep(1)

    if random.random() < 0.2:  # 20% chance of failure
        raise self.retry(exc=Exception(f"{task_name} failed"), countdown=2)

    return f"{task_name} completed"


@app.task
def final_callback(results):
    """Executed only if all tasks succeed"""
    print("All tasks succeeded. Aggregating results:", results)
    # Simulate writing to an external system (DB, API, etc.)
    with open("results.txt", "w") as f:
        f.write("\n".join(results))
    return "Final task completed successfully"


@app.task(bind=True, max_retries=3)
def process_file(self, file_name):
    print(f"Processing {file_name}...")
    time.sleep(1)

    if random.random() < 0.2:  # Simulate failure
        raise self.retry(exc=Exception(f"Failed processing {file_name}"), countdown=2)

    return f"{file_name} processed"


@app.task
def write_to_db(results):
    """Write to DB only if all file processing succeeds"""
    print("All files processed successfully. Writing to DB.")
    return f"Stored in DB: {results}"


@app.task(bind=True, ignore_result=True)
def task3_with_fallback(self):
    try:
        print("Executing Task 3...")
        if random.random() < 0.3:
            raise Exception("Task 3 failed")
        return "Task 3 completed"
    except Exception:
        print("Task 3 failed, but continuing workflow...")


@app.task
def cleanup_expired_tokens():
    print("Cleaning up expired tokens...")
    return "Expired tokens cleaned!"


# Exponential retry in Celery using self.request.retries - Celery itself can delay re-queuing using
@app.task(bind=True, max_retries=5)
def process_task(self, task_name):
    try:
        print(f"Processing {task_name}...")
        if random.random() < 0.3:
            raise Exception("Task failed")
        return f"{task_name} completed"
    except Exception as e:
        delay = 2 ** self.request.retries  # Exponential delay: 2, 4, 8, 16s...
        raise self.retry(exc=e, countdown=delay)


# Each failure moves the message to a longer delay queue.
@app.task(bind=True, max_retries=5)
def process_task(self, task_name):
    """Process a task and implement exponential retry delays"""
    try:
        print(f"Processing {task_name}...")
        if random.random() < 0.5:  # Simulate a 50% chance of failure
            raise Exception("Task failed")
        return f"{task_name} completed"
    except Exception as e:
        retries = self.request.retries
        if retries < 3:
            retry_queue = f"retry_{2**retries}s"
            print(f"Retrying {task_name} in {2**retries} seconds via {retry_queue}")
            self.retry(exc=e, countdown=2**retries)  # 2s, 4s, 8s delay
        else:
            print(f"Max retries reached. Sending {task_name} to DLQ.")
            raise e  # Move to DLQ
