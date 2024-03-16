import boto3
import json
import os

from Scheduler.serializers import VirtualEnvironmentsSerializer
from Scheduler.models import Task, VirtualEnvironments
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
        # if not VirtualEnvironments.objects.all().count() < self.concurrency:
        #     raise OverflowError("Max Concurrency Achieved.")
        sqs.send_message(
            QueueUrl=task_queue["QueueUrl"],
            MessageBody=json.dumps(message)
        )
        vt = VirtualEnvironments(
            task_id=message["task_id"],
            status="Created"
        )
        vt.save()
        return {"task_id":message["task_id"],"status":"Created"}
    
    def delete_job(self, task_id):
        body = json.dumps({"task_id": task_id, "action":"delete"})
        sqs.send_message(
            QueueUrl=control_queue["QueueUrl"],
            MessageBody=body
        )
        vt = VirtualEnvironments.objects.filter(task_id=task_id)
        if vt.exists():
            vt.delete()
        return {"task_id":task_id, "status":"Deletion in progress"}
    
    def list_jobs(self):
        vts = VirtualEnvironments.objects.all()
        serializer = VirtualEnvironmentsSerializer(vts, many=True)
        return serializer.data
    
    def save_metrics(self, metrics):
        vt, new_vt = VirtualEnvironments.objects.get_or_create(task_id=metrics['task_id'])
        for k,v in metrics.items():
            setattr(vt, k, v)
        vt.save()

vp = VirtualEnvironmentProvider()

def send_mail_to_admin(task):
    pass

def debug_task():
    while True:
        message = sqs.receive_message(
            QueueUrl=result_queue["QueueUrl"],
            MaxNumberOfMessages=1
            )
        try:
            if message.get("Messages"):
                body = json.loads(message['Messages'][0]['Body'])
                print(body)
                if body.get("operation") and body.get("operation") == "venv_metrics" and body.get("metrics"):
                    for metric in body["metrics"]:
                        vp.save_metrics(metric)
                elif body.get("operation") and body.get("operation") == "task_update" and body.get("updates"):
                    vp.save_metrics(body["updates"])
                    tro = Task.objects.get(task_id=body["updates"]["task_id"])
                    tro.status = body["updates"]["status"]
                    tro.save()
                elif body.get("operation") not in ["venv_metrics", "task_update", None] and body.get("results"):
                    if body.get("action") in ["completed", "delete"]:
                        VirtualEnvironments.objects.get(task_id=body["task_id"]).delete()
                    tro = Task.objects.get(task_id=body["task_id"])
                    for k,v in body["results"].items():
                        setattr(tro, k, v)
                    tro.save()
                else:
                    print(f"invalid message: {body}")
                    send_mail_to_admin(body)
        except Exception as e:
            print(f"Something went wrong: {e}")
            send_mail_to_admin(f"{e}")

