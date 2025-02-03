# Building a Celery Framework for Junior Developers
The goal is to create a framework where junior developers only need to define tasks without worrying about:

1. Celery-specific attributes (e.g., retries, countdown, ignore_result).
2. Error handling and exponential backoff.
3. Queue management and retry logic.


## Key Design Considerations
To achieve this, we can use:

1. Factory Pattern → To generate Celery tasks dynamically.
2. Decorator Pattern → To wrap task functions with Celery configurations.
3. Functional Composition → To separate Celery attributes from business logic.
4. Higher-Order Functions → To provide retry logic automatically.

## Implementing the Framework
### Step 1: Create a Task Wrapper (task_framework)
This function:
1. Wraps any function into a Celery task.
2. Handles retries and backoff automatically.
3. Separates business logic from Celery attributes.

```commandline
from celery import Celery
import time
import random
import functools

app = Celery('tasks', broker='pyamqp://guest@localhost//', backend='db+postgresql://user:password@localhost/celery_db')

def task_framework(retries=3, backoff=2, ignore_result=False):
    """Framework decorator to wrap any function as a Celery task."""
    
    def decorator(func):
        @app.task(bind=True, max_retries=retries, ignore_result=ignore_result)
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                print(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
                return func(*args, **kwargs)
            except Exception as e:
                delay = backoff ** self.request.retries  # Exponential backoff
                print(f"Retrying {func.__name__} in {delay} seconds due to error: {e}")
                raise self.retry(exc=e, countdown=delay)
        
        return wrapper

    return decorator

```


### Step 2: Junior Developer Defines a Task
A junior developer only needs to write business logic:

```commandline

@task_framework(retries=5, backoff=3, ignore_result=True)
def process_order(order_id):
    print(f"Processing order: {order_id}")
    if random.random() < 0.3:
        raise Exception("Order processing failed")
    return f"Order {order_id} processed"
```

What Happens Automatically?
1. The function becomes a Celery task.
2. It retries up to 5 times on failure.
3. It uses exponential backoff (3, 9, 27, ... seconds).
4. It doesn’t expose results (ignore_result=True).


## Advanced Features for Framework
###  Adding Task Selection (Dynamic Task Chaining)
We can dynamically select which tasks to run based on a message.

```commandline
TASK_REGISTRY = {}

def register_task(name):
    """Registers a function as a task."""
    def decorator(func):
        TASK_REGISTRY[name] = func
        return func
    return decorator

@register_task("task1")
@task_framework(retries=3)
def task1(data):
    print(f"Task1 processing: {data}")
    return f"Task1 result: {data}"

@register_task("task2")
@task_framework(retries=2)
def task2(data):
    print(f"Task2 processing: {data}")
    return f"Task2 result: {data}"

```

Now, tasks can be dynamically selected at runtime:

```commandline
def execute_dynamic_workflow(task_list, data):
    chain_tasks = [TASK_REGISTRY[task].s(data) for task in task_list if task in TASK_REGISTRY]
    workflow = chain(*chain_tasks)
    return workflow.apply_async()

```

```commandline
execute_dynamic_workflow(["task1", "task2"], "Sample Data")

```