import os
import boto3

USER_HOME = os.path.expanduser("~")
APP_NAME = os.environ.get("APP_NAME", "Nimbus")
APP_HOME = os.path.join(USER_HOME, APP_NAME)

FK = b'uIawggMupuIJcQ1ynqz1atq6JPCvK_rz0FFQ0RbWkVc='
TASK_QUEUE_NAME = os.environ.get("TASK_QUEUE_NAME","EE-Task-Queue")
CONTROL_QUEUE_NAME = os.environ.get("CONTROL_QUEUE_NAME","EE-Control-Queue")
RESULT_QUEUE_NAME = os.environ.get("RESULT_QUEUE_NAME","EE-Result-Queue")
DJANGO_SERVER_URL = os.environ.get("DJANGO_SERVER_URL", "void_django:5000")

sqs = boto3.client("sqs")

concurrency = os.environ.get("CONCURRENCY",3)

task_queue = sqs.get_queue_url(QueueName=TASK_QUEUE_NAME)
control_queue = sqs.get_queue_url(QueueName=CONTROL_QUEUE_NAME)
result_queue = sqs.get_queue_url(QueueName=RESULT_QUEUE_NAME)