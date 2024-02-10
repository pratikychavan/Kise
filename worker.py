import boto3
import json
import venv
import os
import subprocess
import time
import psutil

sqs = boto3.client("sqs")
task_queue = sqs.get_queue_url(QueueName="EE-Task-Queue.fifo")
control_queue = sqs.get_queue_url(QueueName="EE-Control-Queue.fifo")
result_queue = sqs.get_queue_url(QueueName="EE-Result-Queue.fifo")
SUBPROCESSES = {}

class VirtualEnvironmentWorker:

    def run_job(self, message):
        print(f"message: {message}")
        venv_path = message["key"].split(".")[0]
        venv.create(env_dir=f"./{venv_path}", with_pip=True)
        SUBPROCESSES[venv_path] = {"status": "Created"}
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_interpreter = os.path.join(venv_path, "bin", "python")
        subprocess.run(["bash", activate_script])
        p = subprocess.Popen([python_interpreter, "task.py"])
        SUBPROCESSES[venv_path] = {"status": "Running", "PID":p.pid}
        return "Created"
    
    def delete_job(self, venv_path):
        process = psutil.Process(SUBPROCESSES[venv_path]["PID"])
        process.kill()
        subprocess.run(["rm","-r",venv_path])
        del SUBPROCESSES[venv_path]
        return "Deleted"
    
    def suspend_job(self, venv_path):
        process = psutil.Process(SUBPROCESSES[venv_path]["PID"])
        process.suspend()
        SUBPROCESSES[venv_path]["status"] = "Suspended"
        return "Suspended"
    
    def resume_job(self, venv_path):
        process = psutil.Process(SUBPROCESSES[venv_path]["PID"])
        process.resume()
        SUBPROCESSES[venv_path]["status"] = "Resumed"
        return "Resumed"
    
    def get_metrics(self):
        if not SUBPROCESSES:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
            }
        for sp in SUBPROCESSES:
            process = psutil.Process(sp["PID"])
            return {
                "cpu_percent": process.cpu_percent,
                "memory_percent": process.memory_percent,
            }

class QueueManager:
    def __init__(self):
        pass
    
    def send_message(self, queue, message):
        sqs.send_message(
            QueueUrl=queue["QueueUrl"],
            MessageBody=json.dumps(message),
            MessageGroupId="1",
            MessageDeduplicationId="1"
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

concurrency = os.environ.get("CONCURRENCY",3)

vw = VirtualEnvironmentWorker()
qm = QueueManager()

while True:
    counter_for_metric_update = 0
    time.sleep(1)
    counter_for_metric_update += 1
    if counter_for_metric_update == 60:
        metrics = vw.get_metrics()
        qm.send_message(result_queue, metrics)
        counter_for_metric_update = 0
    if len(vw.venv_tracker) < concurrency:
        task_message = qm.receive_message(task_queue)
        if task_message.get("Messages"):
            qm.delete_message(task_queue, task_message)
            data = json.loads(task_message["Messages"][0]["Body"])
            status = vw.run_job(data)
            create_status = {
                "task_id": data["task_id"],
                "status": "Created"
                }
            qm.send_message(result_queue, create_status)
    control_message = qm.receive_message(control_queue)
    if control_message.get("Messages"):
        qm.delete_message(control_queue, control_message)
        data = json.loads(control_message["Messages"][0]["Body"])
        if data["action"] == "delete":
            vw.delete_job(data["task_id"])



