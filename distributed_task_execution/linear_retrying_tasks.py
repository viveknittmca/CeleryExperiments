import random

from celery import app, chain


@app.task(bind=True, max_retries=3)
def task_function(self, task_name):
    try:
        print(f"Executing {task_name}...")
        if random.random() < 0.3:  # Simulated failure
            raise Exception(f"{task_name} failed")
        return f"{task_name} completed"
    except Exception as e:
        raise self.retry(exc=e, countdown=2)  # Linear retry every 2 seconds


@app.task(bind=True, max_retries=3)
def task_function(self, task_name):
    try:
        print(f"Executing {task_name}...")
        if random.random() < 0.3:
            raise Exception(f"{task_name} failed")
        return f"{task_name} completed"
    except Exception as e:
        raise self.retry(exc=e, countdown=2)


@app.task
def error_handler(request, exc, traceback):
    print(f"Task {request.id} failed. Exception: {exc}")


workflow = chain(
    task_function.s("Task 1").on_error(error_handler.s()),
    task_function.s("Task 2").on_error(error_handler.s()),
    task_function.s("Task 3").on_error(error_handler.s())
)

workflow.apply_async()
