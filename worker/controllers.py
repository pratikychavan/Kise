import json
import venv
import os
import subprocess
import psutil

from constants import sqs, get_subprocesses,set_subprocesses, VENV_ROOT, OUTPUT_ROOT, WORKER_ROOT, FILES_ROOT, LOG_ROOT

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
    
    def make_folders(self, task_id):
        subprocess.run(["mkdir", "-p", f"{OUTPUT_ROOT}/{task_id}"])
        subprocess.run(["mkdir", "-p", f"{VENV_ROOT}/{task_id}"])
        subprocess.run(["mkdir", "-p", f"{FILES_ROOT}/{task_id}"])
        subprocess.run(["mkdir", "-p", f"{LOG_ROOT}/{task_id}"])
    
    def make_task_env(self, task_id, params):
        task_env = os.environ.copy()
        task_env["venv_name"] = task_id
        task_env["params"] = json.dumps(params)
        return task_env
        
    def run_job(self, message):
        try:
            print(f"message: {message}")
            venv_name = message["params"]["task_id"]
            processes = get_subprocesses()
            processes[venv_name] = {"status": "Created"}
            set_subprocesses(processes)
            self.make_folders(venv_name)
            venv.create(
                env_dir=f"{VENV_ROOT}/{venv_name}", 
                with_pip=True,
                system_site_packages=True
            )
            task_env = self.make_task_env(venv_name, message["params"])
            activate_script = f"{VENV_ROOT}/{venv_name}/bin/activate"
            python_interpreter = f"/{VENV_ROOT}/{venv_name}/bin/python"
            subprocess.run(["bash", activate_script])
            task_output_buffer = open(f"{LOG_ROOT}/{venv_name}/task_exec.log", "w")
            p = subprocess.Popen(
                [python_interpreter, f"{WORKER_ROOT}/task.py"],
                env=task_env,
                stdout=task_output_buffer
                )
            processes = get_subprocesses()
            processes[venv_name] = {
                "task_id": venv_name,    
                "cpu_utilization": 0,
                "memory_utilization": 0,
                "status": "Running", 
                "PID":p.pid
                }
            set_subprocesses(processes)
            return "Created"
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)

    def delete_job(self, venv_name):
        processes = get_subprocesses()
        process = psutil.Process(processes[venv_name]["PID"])
        process.kill()
        del processes[venv_name]
        set_subprocesses(processes)
        return "Deleted"
    
    def suspend_job(self, venv_name):
        processes = get_subprocesses()
        process = psutil.Process(processes[venv_name]["PID"])
        process.suspend()
        processes[venv_name]["status"] = "Suspended"
        set_subprocesses(processes)
        return "Suspended"
    
    def resume_job(self, venv_name):
        processes = get_subprocesses()
        process = psutil.Process(processes[venv_name]["PID"])
        process.resume()
        processes[venv_name]["status"] = "Resumed"
        set_subprocesses(processes)
        return "Resumed"

    
    def get_metrics(self):
        processes = get_subprocesses()
        if not processes:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
            }
        metrics = []
        for sp in processes:
            process = psutil.Process(sp["PID"])
            metrics.append({
                "task_id": sp,
                "status":sp["status"],
                "process_id": sp["PID"],
                "cpu_utilization": process.cpu_percent,
                "memory_utilization": process.memory_percent,
            })
        return json.dumps({"operation":"venv_metrics","metrics":metrics})
    

