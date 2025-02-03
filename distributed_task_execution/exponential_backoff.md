Exponential Backoff When Re-Queuing Failed Messages in RabbitMQ
By default, when a Celery task fails, the message is re-queued immediately.
To introduce exponential backoff, configure Celery's retry settings in RabbitMQ.

Solution: Use Dead Letter Exchanges (DLX) with Time-To-Live (TTL)
Configure RabbitMQ TTL to delay message re-processing.
Each failure moves the message to a delay queue for 2^attempt seconds.
Once TTL expires, the message moves back to the main queue.

```
rabbitmqctl set_policy retry \
".*" '{"dead-letter-exchange":"delayed_retry","message-ttl":2000}' --apply-to queues
```


🔹 What is a Dead Letter Queue (DLQ)?
In normal cases, a DLQ is a queue where messages go when they cannot be processed after multiple attempts.
This happens due to:
Message TTL Expiry (time-to-live exceeded).
Max Delivery Attempts Reached (message rejected too many times).
Queue Overload (message cannot be processed).
🔹 How Do We Use DLQs for Delayed Retries?
Instead of discarding messages immediately when a failure occurs, we can configure RabbitMQ to:



Move the failed message into a DLQ (but not permanently).
Apply a time-to-live (TTL) to delay message re-processing.
After TTL expires, move the message back to the original queue for another attempt.
This allows us to implement exponential backoff retries without blocking the original queue.



What Does dead-letter-exchange: "delayed_retry" Do?

```
"dead-letter-exchange":"delayed_retry"
```

This means:

When a message fails or is rejected, instead of being dropped, it is sent to a Dead Letter Exchange (DLX) called "delayed_retry".
This DLX is linked to a delay queue that holds the message for a specific TTL (Time-To-Live).
Once the TTL expires, the message is automatically returned to the main queue for re-processing.

🔹 Example Configuration
Let's say we have a queue task_queue, and we want messages that fail to be:

1. Sent to a dead-letter-exchange (delayed_retry).
2. Held in a delay queue for a certain TTL (2000ms for first failure).
3. Returned to task_queue after TTL expires for retry.

```commandline
rabbitmqctl set_policy retry \
".*" '{"dead-letter-exchange":"delayed_retry","message-ttl":2000}' --apply-to queues
```


🔹 Implementing Exponential Backoff Using DLX
To introduce exponential backoff:

Configure multiple delay queues (e.g., 2s, 4s, 8s, 16s, etc.).
Route failed messages to a progressively longer delay queue before re-processing.

RabbitMQ Queue Policy for Exponential Delays
We define multiple delayed queues with increasing TTL:

```commandline
rabbitmqctl set_policy "retry-2s" "retry_2s_queue" '{"message-ttl":2000, "dead-letter-exchange":"task_exchange"}'
rabbitmqctl set_policy "retry-4s" "retry_4s_queue" '{"message-ttl":4000, "dead-letter-exchange":"task_exchange"}'
rabbitmqctl set_policy "retry-8s" "retry_8s_queue" '{"message-ttl":8000, "dead-letter-exchange":"task_exchange"}'

```



RabbitMQ Setup: Dead Letter Exchange (DLX) for Delayed Retries
We'll configure RabbitMQ queues to delay retries using DLX.

🔹 Step 1: Define Main Queue and Retry Queues
We'll set up:

A main queue (task_queue) for processing.
Three retry queues (retry_2s, retry_4s, retry_8s) for exponential delays.
A final dead-letter queue (dlq) for messages that fail after maximum retries.
Create Exchanges and Queues


```commandline
# Declare the main exchange
rabbitmqctl add_vhost my_vhost
rabbitmqctl set_policy retry ".*" \
    '{"dead-letter-exchange":"retry_exchange"}' --apply-to queues

# Create a queue for immediate processing
rabbitmqctl declare queue task_queue \
    --arguments '{"x-dead-letter-exchange":"retry_exchange"}'

# Create retry queues with increasing TTL
rabbitmqctl declare queue retry_2s \
    --arguments '{"x-message-ttl":2000, "x-dead-letter-exchange":"task_exchange"}'
rabbitmqctl declare queue retry_4s \
    --arguments '{"x-message-ttl":4000, "x-dead-letter-exchange":"task_exchange"}'
rabbitmqctl declare queue retry_8s \
    --arguments '{"x-message-ttl":8000, "x-dead-letter-exchange":"task_exchange"}'

# Create final DLQ for failed messages
rabbitmqctl declare queue dlq

```

To check if failed messages reach dlq:
```commandline
rabbitmqctl list_queues name messages
```

```commandline
celery -A tasks worker --loglevel=info -Q task_queue

```


Broker + Backend:
 Allowed combinations:

Broker = RabbitMQ (pyamqp://), Backend = PostgreSQL (db+postgresql://)
Broker = Redis (redis://), Backend = PostgreSQL (db+postgresql://)
Broker = RabbitMQ (pyamqp://), Backend = Redis (redis://)

```
db+postgresql://user:password@localhost/dbname
```


# Monitor Failed Tasks in Real-Time
## 🔹 Option 1: Using celery events
Run the following command to track real-time task execution:

```
celery -A tasks events --loglevel=info
```

## 🔹 This provides a live feed of task statuses.

## 🔹 Option 2: Querying PostgreSQL Directly
To see failed tasks:
```
SELECT * FROM celery_taskmeta WHERE status = 'FAILURE';
```


# Monitor Celery Tasks Using Flower
## Flower is a web UI for Celery monitoring.

### 🔹 Step 1: Install Flower

```pip install flower```

### 🔹 Step 2: Start Flower
```
celery -A tasks flower
```

🌍 Open http://localhost:5555 in your browser to:

View task execution.
Monitor worker status.
Retry failed tasks.


# 4️⃣ Configuring Task Expiration & Revocation
## 🔹 Expiring Tasks (expires)
Set an expiration time to auto-remove stale tasks.
```
process_task.apply_async(args=["Task_1"], expires=3600)  # Expires in 1 hour
```
## 🔹 Revoking a Running Task
If a task is taking too long, revoke it:
```
celery -A tasks revoke <task_id> --terminate
```
## 🔹 Terminate ensures the task is forcibly killed.