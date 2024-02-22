import os
import venv
import json
import psutil
import pygit2
import shutil
import traceback
import subprocess
import multiprocessing
from datetime import datetime

from constants import sqs, result_queue, APP_HOME

def execute_task(data, active_processes):
    try:
        print("In execute task")

        task_id = data["task_id"]
        gitea_url = data["gitea_url"]
        print(f"Got task id: {task_id}")

        task_path_base = os.path.join(APP_HOME, task_id)
        task_venv = os.path.join(task_path_base, "venv")
        task_files = os.path.join(task_path_base, "files")
        task_outputs = os.path.join(task_path_base, "outputs")
        task_logs = os.path.join(task_path_base, "logs")
        print(f"Created task paths at {task_path_base}")

        os.makedirs(task_venv, exist_ok=True)
        os.makedirs(task_files, exist_ok=True)
        os.makedirs(task_outputs, exist_ok=True)
        os.makedirs(task_logs, exist_ok=True)
        print(f"Created folders at {task_path_base}")

        venv.create(env_dir=task_venv, with_pip=True, system_site_packages=True)
        print(f"Virtual Env created at {task_venv}")

        if os.name != "nt":
            pypath = os.path.join(task_venv, "bin", "python")
        else:
            pypath = os.path.join(task_venv, "Scripts", "python.exe")
        print(f"Venv pypath at {pypath}")

        pygit2.clone_repository(gitea_url, task_files)
        print(f"Cloned repository at {task_files}")

        main_file = os.path.join(task_files, data["execution_script"])
        execution_log_file = open(os.path.join(task_outputs, "execution_log.txt"), "w")
        print(f"Starting execution of {main_file}")
        print(f"Stdout at {execution_log_file.name}")

        subprocess.run([pypath, main_file], stdout=execution_log_file, cwd=task_files)
        execution_log_file.close()
        print("execution completed")

        shutil.rmtree(task_venv)
        shutil.rmtree(task_files)
        shutil.rmtree(task_outputs)
        shutil.rmtree(task_logs)
        print("removed extra files")
        
        active_processes[task_id]["status"] = "completed"
        sqs.send_message(
            QueueUrl=result_queue["QueueUrl"],
            MessageBody=json.dumps(
                active_processes[task_id]
            )
        )
        del active_processes[task_id]
        print(f"Completed task: {task_id}, Freeing system resources and exiting.")
        exit()
    except Exception as e:
        print(traceback.format_exc())
        active_processes[task_id]["status"] = "failed"
        sqs.send_message(
            QueueUrl=result_queue["QueueUrl"],
            MessageBody=json.dumps(
                active_processes[task_id]
            )
        )
        del active_processes[task_id]
        print(f"Failed task: {task_id}, Freeing system resources and exiting.")
        exit()

class ProcessActions:
    def __init__(self, message, active_processes):
        self.message = message
        self.active_processes = active_processes
        self.process = psutil.Process(self.active_processes[self.message["task_id"]]["pid"])
        self.action_map = {
            "delete": self.delete_process,
            "suspend": self.suspend_process,
            "resume": self.resume_process,
        }
    
    def delete_process(self):
        self.process.kill()
        del self.active_processes[self.message["task_id"]]
        return self.active_processes
    
    def suspend_process(self):
        self.process.suspend()
        self.active_processes[self.message["task_id"]]["status"] = "Suspended"
        return self.active_processes
    
    def resume_process(self):
        self.process.resume()
        self.active_processes[self.message["task_id"]]["status"] = "Resumed"
        return self.active_processes

def get_process_metrics(active_processes):
    tasks = []
    for task in active_processes:
        process_monitor = psutil.Process(active_processes[task]["pid"])
        tasks.append({
            "pid": process_monitor.pid,
            "created_at": datetime.fromtimestamp(
                process_monitor.create_time()
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "status": process_monitor.status(),
            "cpu_utilization": process_monitor.cpu_percent(),
            "memory_utilization": process_monitor.memory_percent(),
            "message": active_processes[task]["message"],
        })
    return {"operation":"venv_metrics","metrics":tasks}

def process_task_messages(
        task_response:dict, 
        task_queue_url:str, 
        active_processes:dict, 
        result_queue_url:str
    ):
    message = task_response["Messages"][0]
    message_body = json.loads(message["Body"])
    receipt_handle = message["ReceiptHandle"]
    sqs.delete_message(
        QueueUrl=task_queue_url, ReceiptHandle=receipt_handle
    )
    process = multiprocessing.Process(
        target=execute_task, args=(message_body, active_processes)
    )
    process.start()
    process_monitor = psutil.Process(process.pid)
    active_processes[message_body["task_id"]] = {
        "pid": process_monitor.pid,
        "created_at": datetime.fromtimestamp(
            process_monitor.create_time()
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "status": process_monitor.status(),
        "cpu_utilization": process_monitor.cpu_percent(),
        "memory_utilization": process_monitor.memory_percent(),
        "message": message_body,
    }
    sqs.send_message(
        QueueUrl=result_queue_url,
        MessageBody=json.dumps(
            active_processes[message_body["task_id"]]
        ),
    )
    return active_processes

def process_control_message(
    control_response:dict,
    active_processes:dict,
    control_queue_url:dict
):
    control_message = control_response["Messages"][0]
    data = json.loads(control_message["Body"])
    if data["task_id"] in active_processes and data["action"] in [
        "delete",
        "suspend",
        "resume",
    ]:
        control_receipt_handle = control_message["ReceiptHandle"]
        sqs.delete_message(
            QueueUrl=control_queue_url, ReceiptHandle=control_receipt_handle
        )
        active_processes = ProcessActions(
            data=data,
            active_processes=active_processes
        ).action_map[data["action"]]()
    elif data["action"] not in ["delete", "suspend", "resume"]:
        control_receipt_handle = control_message["ReceiptHandle"]
        sqs.delete_message(
            QueueUrl=control_queue_url, ReceiptHandle=control_receipt_handle
        )
    else:
        pass
    return active_processes