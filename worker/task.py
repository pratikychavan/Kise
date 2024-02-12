import time
import os
from worker import vw
running_task_pid = os.getpid()
i = 0
while i<10:
    time.sleep(1)
    i+=1
    print(f"Inside VENV {running_task_pid}")
vw.complete_job()