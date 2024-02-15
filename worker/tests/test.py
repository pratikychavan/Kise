import boto3
import json
import venv
import os
import subprocess
import time
import psutil

sqs = boto3.client("sqs")
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue")
# SUBPROCESSES = {}

class QueueManager:
    def __init__(self):
        pass
    
    def send_message(self, queue, message):
        sqs.send_message(
            QueueUrl=queue["QueueUrl"],
            MessageBody=json.dumps(message)
        )
    
    def receive_message(self, queue):
        return sqs.receive_message(
            QueueUrl=queue["QueueUrl"], 
            MaxNumberOfMessages=1
        )
    
    def delete_message(self, queue, message):
        sqs.delete_message(
            QueueUrl=queue["QueueUrl"], 
            ReceiptHandle=message["Messages"][0]["ReceiptHandle"]
        )
        

qm = QueueManager()

for num in range(5):
    qm.send_message(task_queue, {"task_id":f"test_{num}", "key":f"some_key_{num}"})

time.sleep(60)

for num in range(5):
    qm.send_message(control_queue, {"task_id":f"test_{num}", "action":"delete"})