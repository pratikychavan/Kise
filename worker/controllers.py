import json
import venv
import os
import subprocess
import psutil
import signal

from worker.constants import sqs,result_queue, SUBPROCESSES

class VirtualEnvironmentWorker:
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
    
    def run_job(self, message):
        print(f"message: {message}")
        venv_path = message["task_id"]
        venv.create(
            env_dir=f"./{venv_path}", 
            with_pip=True,
            system_site_packages=True
        )
        SUBPROCESSES[venv_path] = {"status": "Created"}
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_interpreter = os.path.join(venv_path, "bin", "python")
        task_env = os.environ.copy()
        subprocess.run(["bash", activate_script])
        task_env["venv_path"] = venv_path
        p = subprocess.Popen(
            [python_interpreter, "worker/task.py"],
            env=task_env
            )
        SUBPROCESSES[venv_path] = {
            "task_id": venv_path,    
            "cpu_utilization": 0,
            "memory_utilization": 0,
            "status": "Running", 
            "PID":p.pid
            }
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
    
    def complete_job(self, venv_path, result):
        self.send_message(result_queue, result)
        # del SUBPROCESSES[venv_path]
        subprocess.run(["rm", "-r", venv_path])
        os.kill(os.getpid(), signal.SIGTERM)
        exit()
    
    def get_metrics(self):
        if not SUBPROCESSES:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
            }
        metrics = []
        for sp in SUBPROCESSES:
            process = psutil.Process(sp["PID"])
            metrics.append({
                "task_id": sp,
                "status":sp["status"],
                "process_id": sp["PID"],
                "cpu_utilization": process.cpu_percent,
                "memory_utilization": process.memory_percent,
            })
        return json.dumps({"operation":"venv_metrics","metrics":metrics})
    

vw = VirtualEnvironmentWorker()
