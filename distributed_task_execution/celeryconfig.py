from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'cleanup-every-hour': {
        'task': 'tasks.cleanup_expired_tokens',
        'schedule': crontab(minute=0, hour='*'),  # Runs every hour
    }
}


# Configure Celery to Use RabbitMQ for Retries
broker_url = "pyamqp://guest@localhost//"

task_routes = {
    'tasks.process_task': {'queue': 'task_queue'}
}

task_acks_late = True  # Ensures tasks are not lost on failure
task_reject_on_worker_lost = True  # Prevents re-processing of failed tasks


# Postgres
broker_url = "pyamqp://guest@localhost//"  # Using RabbitMQ as broker
result_backend = "db+postgresql://user:password@localhost/celery_db"

# Followed by
# celery -A tasks backend_cleanup
