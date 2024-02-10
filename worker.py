import boto3
import json
import venv
import os
import subprocess
import signal
import time

sqs = boto3.client("sqs")
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue.fifo")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue.fifo")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue.fifo")


class VirtualEnvironmentWorker:
    def __init__(self):
        self.venv_tracker = {}

    def run_job(self, message):
        print(f"message: {message}")
        venv_path = message["key"].split(".")[0]
        venv.create(env_dir=f"./{venv_path}", with_pip=True)
        self.venv_tracker[venv_path] = {"status": "Created"}
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_interpreter = os.path.join(venv_path, "bin", "python")
        subprocess.run(["bash", activate_script])
        p = subprocess.Popen([python_interpreter, "task.py"])
        self.venv_tracker[venv_path] = {"status": "Running", "PID":p.pid}
        return "Created"
    
    def delete_job(self, venv_path):
        os.kill(self.venv_tracker[venv_path]["PID"], signal.SIGTERM)
        return "Deleted"

concurrency = os.environ.get("CONCURRENCY",3)

vw = VirtualEnvironmentWorker()
while True:
    time.sleep(1)
    if len(vw.venv_tracker) < concurrency:
        task_messages = sqs.receive_message(
                QueueUrl=task_queue["QueueUrl"], 
                MaxNumberOfMessages=1
                )
        if task_messages.get("Messages"):
            sqs.delete_message(
                QueueUrl=task_queue["QueueUrl"], 
                ReceiptHandle=task_messages["Messages"][0]["ReceiptHandle"]
            )
            data = json.loads(task_messages["Messages"][0]["Body"])
            status = vw.run_job(data)
            create_status = json.dumps({
                "task_id": data["task_id"],
                "status": "Created"
                })
            sqs.send_message(
                QueueUrl=result_queue["QueueUrl"],
                MessageBody=create_status,
                MessageGroupId="1",
                MessageDeduplicationId="1"
            )
    control_message = sqs.receive_message(
            QueueUrl=control_queue["QueueUrl"],
            MaxNumberOfMessages=1
    )
    if control_message.get("Messages"):
        sqs.delete_message(
                QueueUrl=control_queue["QueueUrl"], 
                ReceiptHandle=task_messages["Messages"][0]["ReceiptHandle"]
            )
        data = json.loads(control_message["Messages"][0]["Body"])
        if data["action"] == "delete":
            vw.delete_job(data["task_id"])



