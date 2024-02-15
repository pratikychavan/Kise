import os
import json
import subprocess
from constants import sqs, control_queue, result_queue, VENV_ROOT, FILES_ROOT, OUTPUT_ROOT

running_task_pid = os.getpid()
venv_name = os.environ.get('venv_name')
params = json.loads(os.environ.get('params', {}))

venv_path = f"{VENV_ROOT}/{venv_name}" 
repo_path = f"{FILES_ROOT}/{venv_name}"
outputs_path = f"{OUTPUT_ROOT}/{venv_name}"

subprocess.run(["git", "clone", f"{params['gitea_url']}", repo_path])
subprocess.run(["pip","install","-r",f"{repo_path}/requirements.txt"])

subprocess.run(["mkdir", "-p", outputs_path])

os.chdir(repo_path)

subprocess.run(["jupyter", "nbconvert", "--to", "html", "--execute", f"{repo_path}/main.ipynb", "--output", f"{outputs_path}/output.html"])

out_buffer = open(f"{outputs_path}/execution.log","w")
subprocess.run([f"{venv_path}/bin/python", f"{repo_path}/main.py"], stdout=out_buffer)
out_buffer.close()

subprocess.run(["rm", "-rf", f"{VENV_ROOT}/{venv_name}"])

result={
        "task_id":venv_name, 
        "action":"completed"
        }
sqs.send_message(
    QueueUrl=control_queue["QueueUrl"],
    MessageBody=json.dumps(result)
)
sqs.send_message(
    QueueUrl=result_queue["QueueUrl"],
    MessageBody=json.dumps(result)
)
exit()