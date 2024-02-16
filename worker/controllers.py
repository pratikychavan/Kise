import os
import venv
import json
import pygit2
import shutil
import traceback
import subprocess

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