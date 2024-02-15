import boto3
import os

sqs = boto3.client("sqs")
concurrency = os.environ.get("CONCURRENCY",3)
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue")

USER_HOME = os.path.expanduser("~")
APP_HOME = os.path.join(USER_HOME, "Nimbus")

WORKER_ROOT = os.path.join(APP_HOME,"worker")
TASK_ROOT = os.path.join(APP_HOME,"tasks")
VENV_ROOT = os.path.join(APP_HOME,"tasks","venvs")
FILES_ROOT = os.path.join(APP_HOME,"tasks","files")
OUTPUT_ROOT = os.path.join(APP_HOME,"tasks","output")
LOG_ROOT = os.path.join(APP_HOME,"logs")

SUBPROCESSES = {}

def get_subprocesses():
    return SUBPROCESSES

def set_subprocesses(subprocesses):
    global SUBPROCESSES
    SUBPROCESSES = subprocesses