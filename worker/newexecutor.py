import os
import shutil
import venv
import json
import boto3
import pygit2
import subprocess
import multiprocessing
from constants import task_queue, control_queue, VENV_ROOT, FILES_ROOT, OUTPUT_ROOT, LOG_ROOT


def execute_task(data):
    data = json.loads(data)
    
    task_id = data["task_id"]
    gitea_url = data["gitea_url"]
    
    task_venv = os.path.join(VENV_ROOT, task_id)
    task_files = os.path.join(FILES_ROOT, task_id)
    task_outputs = os.path.join(OUTPUT_ROOT, task_id)
    task_logs = os.path.join(LOG_ROOT, task_id)
    
    os.makedirs(task_venv, exist_ok=True)
    os.makedirs(task_files, exist_ok=True)
    os.makedirs(task_outputs, exist_ok=True)
    os.makedirs(task_logs, exist_ok=True)
    
    venv.create(
        env_dir=task_venv,
        with_pip=True,
        system_site_packages=True
    )
    
    if os.name != 'nt':
        pypath = os.path.join(task_venv, 'bin', 'python')  
    else: 
        pypath = os.path.join(task_venv, 'Scripts', 'python.exe')
    
    pygit2.clone_repository(gitea_url, task_files)
    
    main_file = os.path.join(task_files, data["execution_script"])
    execution_log_file = open(os.path.join(task_outputs, "execution_log.txt"),"w")
    
    subprocess.run([pypath, main_file], stdout=execution_log_file, cwd=task_files)
    execution_log_file.close()
    
    # shutil.rmtree(task_venv)
    # shutil.rmtree(task_files)
    # shutil.rmtree(task_outputs)
    # shutil.rmtree(task_logs)


def listen_to_sqs():
    sqs = boto3.client('sqs')
    task_queue_url = task_queue["QueueUrl"]
    control_queue_url = control_queue["QueueUrl"]
    concurrency = os.environ.get('CONCURRENCY', 3)
    active_processes = {}
    
    while True:
        try:
            task_response = sqs.receive_message(
                QueueUrl=task_queue_url,
                MaxNumberOfMessages=1
            )
            if len(active_processes) < concurrency:
                if 'Messages' in task_response:
                    message = task_response['Messages'][0]
                    message_body = message['Body']
                    process = multiprocessing.Process(target=execute_task, args=(message_body,))
                    process.start()
                    active_processes[message['MessageId']] = {
                        'process': process,
                        'message_body': message_body
                    }
                    receipt_handle = message['ReceiptHandle']
                    sqs.delete_message(
                        QueueUrl=task_queue_url,
                        ReceiptHandle=receipt_handle
                    )
            control_response = sqs.receive_message(
                QueueUrl=control_queue_url,
                MaxNumberOfMessages=1,
            )
            if 'Messages' in control_response:
                control_message = control_response['Messages'][0]
                control_message_body = control_message['Body']
                control_command = control_message_body.lower()
                if control_command == 'delete':
                    for process_info in active_processes.values():
                        process_info['process'].terminate()
                control_receipt_handle = control_message['ReceiptHandle']
                sqs.delete_message(
                    QueueUrl=control_queue_url,
                    ReceiptHandle=control_receipt_handle
                )
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    listen_to_sqs()
