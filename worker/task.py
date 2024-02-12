import time
import os
from worker.controllers import VirtualEnvironmentWorker
running_task_pid = os.getpid()
i = 0
venv_path = os.environ.get('venv_path')
while i<10:
    time.sleep(1)
    i+=1
    print(f"Inside VENV {running_task_pid}")
print(f"venv_path: {venv_path}")
VirtualEnvironmentWorker().complete_job(venv_path=venv_path, result={"task_id":venv_path, "result":"completed"})