import pika

def publish_task(task_name, payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue=task_name)
    channel.basic_publish(exchange="", routing_key=task_name, body=payload)

    print(f"Published {task_name} Task: {payload}")
    connection.close()

publish_task("process_order", "Order123")
publish_task("send_email", "user@example.com")
