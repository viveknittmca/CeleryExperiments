# Building a REST API (FastAPI) for Triggering Celery Tasks
## Step 1: Install FastAPI and Celery

```commandline
pip install fastapi uvicorn celery redis
```

##  2: Create celery_config.py
```commandline
from celery import Celery

# Configure Celery with RabbitMQ as broker and PostgreSQL as results backend
app = Celery(
    "tasks",
    broker="pyamqp://guest@localhost//",
    backend="db+postgresql://user:password@localhost/celery_db",
)
```

## 3: Define Celery Tasks in tasks.py
```commandline
from celery_config import app
import time

@app.task(bind=True)
def long_running_task(self, task_name):
    """Simulate a long-running task"""
    print(f"Executing {task_name}...")
    time.sleep(5)
    return f"{task_name} completed!"

```

## 4: Create FastAPI Endpoint in api.py
```commandline
from fastapi import FastAPI, BackgroundTasks
from celery.result import AsyncResult
from tasks import long_running_task

app = FastAPI()

@app.post("/trigger-task/")
async def trigger_task(task_name: str):
    """Trigger Celery Task via API"""
    task = long_running_task.apply_async(args=[task_name])
    return {"task_id": task.id, "status": "Task Dispatched"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Check Task Status"""
    result = AsyncResult(task_id)
    return {"task_id": task_id, "status": result.state, "result": result.result}

```