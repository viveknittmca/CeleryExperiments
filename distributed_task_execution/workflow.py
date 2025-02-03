# Orchestrating the Execution
from celery import group
from tasks import execute_task

workflow = group(
    execute_task.s("Task 1"),
    execute_task.s("Task 2"),
    execute_task.s("Task 3")
)

result = workflow.apply_async()

if result.successful():
    print("All tasks succeeded. Writing results.")
    # Write results to external system
else:
    print("Execution failed. No state is leaked.")



# from celery import Celery, chain
# from celery.result import AsyncResult
# from kombu import Connection
#
# # This service acts as an orchestrator for the workflow
# app = Celery("workflow", broker="pyamqp://guest@localhost//")
#
# # Import tasks from independent services
# from task1_service import process_order
# from task2_service import send_email
# from task3_service import generate_invoice
# from task4_service import write_to_db
#
# def start_workflow(order_id):
#     """Trigger sequential execution of tasks as a chain"""
#     workflow = chain(
#         process_order.s(order_id),
#         send_email.s(),
#         generate_invoice.s(),
#         write_to_db.s()
#     )
#     return workflow.apply_async()
#
# def check_workflow_status(task_id):
#     """Check the status of the entire workflow"""
#     result = AsyncResult(task_id)
#     return {"task_id": task_id, "status": result.state, "result": result.result}
#


# workflow_result = start_workflow("ORDER123")
# print("Workflow started:", workflow_result.id)

# check_workflow_status(workflow_result.id)
