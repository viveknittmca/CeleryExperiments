from celery import Celery, chain
import time
import random

app = Celery('tasks', broker='redis://localhost:6379/0')


# How This Works
# Task 1 executes.
# Task 2 starts only after Task 1 completes successfully.
# Task 3 starts only after Task 2 completes successfully.
# Final Step (final_step) runs only if all preceding tasks succeed.
# If any task fails, it retries up to 3 times before the entire workflow fails.

@app.task(bind=True, max_retries=3)
def task_function(self, task_name):
    """Execute a task sequentially with retries"""
    print(f"Executing {task_name}...")
    time.sleep(1)

    if random.random() < 0.2:  # Simulate failure with 20% probability
        raise self.retry(exc=Exception(f"{task_name} failed"), countdown=2)

    return f"{task_name} completed"


@app.task
def final_step(results):
    """Final step executed only if all tasks succeed"""
    print("All tasks succeeded. Writing results:", results)
    return f"Final step received: {results}"


# Sequential execution using `chain`
workflow = chain(
    task_function.s("Task 1"),
    task_function.s("Task 2"),
    task_function.s("Task 3"),
    final_step.s()
)

workflow.apply_async()
print("Chain dispatched!")
