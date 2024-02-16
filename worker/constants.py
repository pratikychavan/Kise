import boto3
import os

sqs = boto3.client("sqs")
concurrency = os.environ.get("CONCURRENCY",3)
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue")

USER_HOME = os.path.expanduser("~")
APP_HOME = os.path.join(USER_HOME, "Nimbus")