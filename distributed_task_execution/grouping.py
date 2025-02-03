from celery import Celery, group

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task
def execute_task(task_name):
    print(f"Executing {task_name}")
    return f"{task_name} completed"


# Creating signatures
task1 = execute_task.s("Task 1")
task2 = execute_task.s("Task 2")
task3 = execute_task.s("Task 3")

# Running tasks in parallel using a group
workflow = group(task1, task2, task3)
result = workflow.apply_async()

print("Tasks dispatched!")
