import boto3
import json
import venv
import os
import subprocess
import signal
import time

from Application.serializers import SomeTaskSerializer
from Application.models import SomeTaskReview
# task_queue = "EE-Task-Queue"
# control_queue = "EE-Control-Queue"

sqs = boto3.client("sqs")
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue.fifo")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue.fifo")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue.fifo")

class VirtualEnvironmentProvider:
    def __init__(self):
        self.venv_tracker = {}
        self.concurrency = os.environ.get("CONCURRENCY",3)
        pass
    
    def create_job(self, message):
        sqs.send_message(
            QueueUrl=task_queue,
            MessageBody=json.dumps(message),
            MessageGroupId="1",
            MessageDeduplicationId="1"
        )
        self.venv_tracker[message["task_id"]] = {"status": "Created"}
        return {"task_id":message["task_id"],"status":"Created"}
    
    def update_venv_tracker(self, message):
        if message["task_status"] in ["Completed", "Deleted", "Error"]:
            del self.venv_tracker[message["task_id"]]
        else:
            self.venv_tracker[message["task_id"]] = {"status":message["task_status"]}
    
    def delete_job(self, task_id):
        sqs.send_message(
            QueueUrl=control_queue,
            MessageBody={"task_id": task_id, "action":"delete"},
            MessageGroupId="1",
            MessageDeduplicationId="1"
        )
        return {"task_id":task_id, "status":"Deletion in progress"}
    
    def list_jobs(self):
        return self.venv_tracker

vp = VirtualEnvironmentProvider()

def debug_task():
    while True:
        message = sqs.receive_message(
            QueueUrl=result_queue["QueueUrl"],
            MaxNumberOfMessages=1
            )
        try:
            body = json.loads(message['Messages'][0]['Body'])
            tro = SomeTaskReview.objects.get(task_id=body["task_id"])
            if body.get("task_status") in ["Created", "Running"]:
                vp.update_venv_tracker(body)
                tro.status = "In Progress"
                tro.save()
            else:
                serializer = SomeTaskSerializer(tro, body)
                if serializer.is_valid():
                    serializer.save()
        except Exception as e:
            pass
