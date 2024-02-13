import os
import json
import subprocess

from controllers import VirtualEnvironmentWorker

running_task_pid = os.getpid()
venv_path = os.environ.get('venv_path')
params = json.loads(os.environ.get('params', {}))

print(f"Inside VENV {running_task_pid}")
print(f"venv_path: {venv_path}")

repo_name = params['gitea_url'].split("/")[-1].split(".")[0]

subprocess.run(["git", "clone", f"{params['gitea_url']}", f"/code/files/{repo_name}"])
subprocess.run(["pip","install","-r",f"/code/files/{repo_name}/requirements.txt"])

subprocess.run(["mkdir", "-p", f"/code/outputs/{repo_name}"])
os.chdir(f"/code/files/{repo_name}")

subprocess.run(["jupyter", "nbconvert", "--to", "html", "--execute", f"/code/files/{repo_name}/main.ipynb", "--output", f"/code/outputs/{repo_name}/output.html"])
subprocess.run([f"/code/worker/{venv_path}/bin/python", f"/code/files/{repo_name}/main.py", ">>", f"/code/outputs/{repo_name}/execution.log"])

VirtualEnvironmentWorker().complete_job(venv_path=venv_path, result={"task_id":venv_path, "result":"completed"})