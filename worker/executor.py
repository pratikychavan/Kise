import traceback
import time
import json

from constants import SUBPROCESSES, concurrency, task_queue, control_queue, result_queue
from controllers import VirtualEnvironmentWorker

vw = VirtualEnvironmentWorker()

def check_task_messages():
    if len(SUBPROCESSES) < concurrency:
        task_message = vw.receive_message(task_queue)
        if task_message.get("Messages"):
            vw.delete_message(task_queue, task_message)
            data = json.loads(task_message["Messages"][0]["Body"])
            status = vw.run_job(data)
            create_status = {
                "operation": "task_update",
                "updates":{
                    "task_id": data["task_id"],
                    "status": status
                    }
            }
            vw.send_message(result_queue, create_status)

def check_control_messages():
    control_message = vw.receive_message(control_queue)
    if control_message.get("Messages"):
        vw.delete_message(control_queue, control_message)
        data = json.loads(control_message["Messages"][0]["Body"])
        if data["task_id"] not in SUBPROCESSES:
            vw.send_message(control_queue, data)
        elif data["action"] == "delete":
            vw.delete_job(data["task_id"])
        elif data["action"] == "suspend":
            vw.suspend_job(data["task_id"])
        elif data["action"] == "resume":
            vw.resume_job(data["task_id"])

def task_executor():
    try:
        counter_for_metric_update = 0
        time.sleep(1)
        counter_for_metric_update += 1
        if counter_for_metric_update == 10:
            metrics = vw.get_metrics()
            vw.send_message(result_queue, metrics)
            counter_for_metric_update = 0
        check_task_messages()
        check_control_messages()
    except Exception as e:
        traceback.print_exc()
        print("Something broke")

from multiprocessing.pool import ThreadPool

while True:
    pool = ThreadPool(2)
    pool.apply_async(task_executor)
    pool.close()
    pool.join()