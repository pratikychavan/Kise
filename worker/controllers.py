import json
import venv
import os
import subprocess
import psutil
import signal

from constants import sqs,result_queue, SUBPROCESSES

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
        try:
            print(f"message: {message}")
            venv_name = message["params"]["task_id"]
            venv.create(
                env_dir=f"/code/worker/{venv_name}", 
                with_pip=True,
                system_site_packages=True
            )
            SUBPROCESSES[venv_name] = {"status": "Created"}
            activate_script = f"/code/worker/{venv_name}/bin/activate"
            python_interpreter = f"/code/worker/{venv_name}/bin/python"
            subprocess.run(["bash", activate_script])
            task_env = os.environ.copy()
            task_env["venv_name"] = venv_name
            task_env["params"] = json.dumps(message["params"])
            subprocess.run(["mkdir", "-p", f"/code/outputs/{venv_name}"])
            task_output_buffer = open(f"/code/outputs/{venv_name}/task_exec.log", "w")
            p = subprocess.Popen(
                [python_interpreter, "/code/worker/task.py"],
                env=task_env,
                stdout=task_output_buffer
                )
            SUBPROCESSES[venv_name] = {
                "task_id": venv_name,    
                "cpu_utilization": 0,
                "memory_utilization": 0,
                "status": "Running", 
                "PID":p.pid
                }
            return "Created"
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)

    def delete_job(self, venv_name):
        process = psutil.Process(SUBPROCESSES[venv_name]["PID"])
        process.kill()
        subprocess.run(["rm","-r",venv_name])
        del SUBPROCESSES[venv_name]
        return "Deleted"
    
    def suspend_job(self, venv_name):
        process = psutil.Process(SUBPROCESSES[venv_name]["PID"])
        process.suspend()
        SUBPROCESSES[venv_name]["status"] = "Suspended"
        return "Suspended"
    
    def resume_job(self, venv_name):
        process = psutil.Process(SUBPROCESSES[venv_name]["PID"])
        process.resume()
        SUBPROCESSES[venv_name]["status"] = "Resumed"
        return "Resumed"
    
    def complete_job(self, venv_name, result):
        self.send_message(result_queue, result)
        del SUBPROCESSES[venv_name]
        subprocess.run(["rm", "-r", venv_name])
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
    

