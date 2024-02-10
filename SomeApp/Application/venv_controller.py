import boto3
import json
import venv
import os
import subprocess
import signal
import time

from Application.serializers import SomeTaskSerializer, VenvTrackerSerializer
from Application.models import SomeTaskReview, VenvTracker
# task_queue = "EE-Task-Queue"
# control_queue = "EE-Control-Queue"

sqs = boto3.client("sqs")
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue")

class VirtualEnvironmentProvider:
    def __init__(self):
        self.concurrency = os.environ.get("CONCURRENCY",3)
        pass
    
    def create_job(self, message):
        if not VenvTracker.objects.all().count() < self.concurrency:
            raise OverflowError("Max Concurrency Achieved.")
        sqs.send_message(
            QueueUrl=task_queue,
            MessageBody=json.dumps(message)
        )
        vt = VenvTracker(
            task_id=message["task_id"],
            status="Created"
        )
        vt.save()
        return {"task_id":message["task_id"],"status":"Created"}
    
    def delete_job(self, task_id):
        sqs.send_message(
            QueueUrl=control_queue,
            MessageBody={"task_id": task_id, "action":"delete"}
        )
        vt = VenvTracker.objects.filter(task_id=task_id)
        if vt.exists():
            vt.delete()
        return {"task_id":task_id, "status":"Deletion in progress"}
    
    def list_jobs(self):
        vts = VenvTracker.objects.all()
        serializer = VenvTrackerSerializer(vts, many=True)
        if serializer.is_valid():
            return serializer.data
        return serializer.errors

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
