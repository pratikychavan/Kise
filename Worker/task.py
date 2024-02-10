import time
import os
running_task_pid = os.getpid()
while True:
    time.sleep(10)
    print(f"Inside VENV {running_task_pid}")