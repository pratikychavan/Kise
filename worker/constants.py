import os
import boto3

USER_HOME = os.path.expanduser("~")
APP_NAME = os.environ.get("APP_NAME", None)
APP_HOME = os.path.join(USER_HOME, APP_NAME)

TASK_QUEUE_NAME = os.environ.get("TASK_QUEUE_NAME",None)
CONTROL_QUEUE_NAME = os.environ.get("CONTROL_QUEUE_NAME",None)
RESULT_QUEUE_NAME = os.environ.get("RESULT_QUEUE_NAME",None)

sqs = boto3.client("sqs")

concurrency = os.environ.get("CONCURRENCY",3)

task_queue = sqs.get_queue_url(QueueName=TASK_QUEUE_NAME)
control_queue = sqs.get_queue_url(QueueName=CONTROL_QUEUE_NAME)
result_queue = sqs.get_queue_url(QueueName=RESULT_QUEUE_NAME)