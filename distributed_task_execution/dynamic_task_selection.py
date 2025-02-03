from celery import chain
from tasks import task_function


def create_workflow(task_list):
    chain_tasks = []
    if "task1" in task_list:
        chain_tasks.append(task_function.s("Task 1"))
    if "task2" in task_list:
        chain_tasks.append(task_function.s("Task 2"))
    if "task3" in task_list:
        chain_tasks.append(task_function.s("Task 3"))
    return chain(*chain_tasks)


message = {"tasks": ["task1", "task3"]}  # Task2 is missing
workflow = create_workflow(message["tasks"])
workflow.apply_async()



