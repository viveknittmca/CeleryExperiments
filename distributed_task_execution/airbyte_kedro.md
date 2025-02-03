# 🚀 Implementing Airbyte with Kedro, Real-Time Streaming with RabbitMQ, and Monitoring with Prometheus
## 1️⃣ Integrating Airbyte with Kedro
Airbyte can be used to ingest data from APIs, PostgreSQL, and S3 into a structured format, which Kedro can then process.

### 1: Install and Start Airbyte
```commandline
curl -sSL https://raw.githubusercontent.com/airbytehq/airbyte/master/run-ab-platform.sh | bash
```
This starts Airbyte UI on http://localhost:8000.


### 2: Configure Airbyte Sources
Add a New Source:
1. Choose API as source (if reading from REST).
2. Choose PostgreSQL as source (if reading from DB).
3. Choose S3 as source (if reading CSV files).
4. Destination: Configure PostgreSQL or S3.

### 3: Trigger Airbyte Sync
After setting up sources and destinations, trigger:
```commandline
curl -X POST "http://localhost:8000/api/v1/jobs/sync"
```

✅ Airbyte fetches API/PostgreSQL/S3 data and loads it into Kedro-compatible storage.

## 2️⃣ Real-Time Streaming with RabbitMQ
...

## 3: Define Kedro Task Consumer in Celery

```commandline
import pika
import json
from celery_tasks import run_kedro_pipeline

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"Received event: {data}")

    # Trigger Kedro Pipeline Execution
    run_kedro_pipeline.delay()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer(queue="kedro_pipeline"):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
    print(f"Waiting for messages on {queue}...")
    channel.start_consuming()

```
