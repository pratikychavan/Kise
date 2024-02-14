import os
import json
import subprocess
from controllers import VirtualEnvironmentWorker
print("imports done")

running_task_pid = os.getpid()
venv_name = os.environ.get('venv_name')
params = json.loads(os.environ.get('params', {}))
print(params)
print("got vars")
repo_name = params['gitea_url'].split("/")[-1].split(".")[0]
venv_path = f"/code/worker/{venv_name}" 
repo_path = f"/code/worker/files/{repo_name}"
outputs_path = f"/code/worker/outputs/{repo_name}"
print("created vars")
subprocess.run(["git", "clone", f"{params['gitea_url']}", repo_path])
subprocess.run(["pip","install","-r",f"{repo_path}/requirements.txt"])
print("got repo content")
subprocess.run(["mkdir", "-p", outputs_path])
os.chdir(repo_path)
print("created output buffers")
subprocess.run(["jupyter", "nbconvert", "--to", "html", "--execute", f"{repo_path}/main.ipynb", "--output", f"{outputs_path}/output.html"])
print("jupyter file run")
out_buffer = open(f"{outputs_path}/execution.log","w")
print("py file out put buffer created")
subprocess.run([f"{venv_path}/bin/python", f"{repo_path}/main.py"], stdout=out_buffer)
print("py file done")
out_buffer.close()
print("send to complete job")
VirtualEnvironmentWorker().complete_job(
    venv_name=venv_name, 
    result={
        "task_id":venv_name, 
        "result":"completed"
        }
    )