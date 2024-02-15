import boto3
import os

sqs = boto3.client("sqs")
concurrency = os.environ.get("CONCURRENCY",3)
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue")
SUBPROCESSES = {}
WORKER_ROOT = "/code/worker"
TASK_ROOT = "/code/worker/tasks"
VENV_ROOT = "/code/worker/tasks/venv"
FILES_ROOT = "/code/worker/tasks/files"
OUTPUT_ROOT = "/code/worker/tasks/output"
LOG_ROOT = "/code/worker/logs"
