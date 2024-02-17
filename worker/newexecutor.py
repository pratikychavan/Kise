import os
import json
import time
import psutil
import traceback
import multiprocessing
from datetime import datetime
from constants import (
    sqs,
    task_queue,
    control_queue,
    result_queue,
)
from controllers import execute_task


def listen_to_sqs():
    task_queue_url = task_queue["QueueUrl"]
    control_queue_url = control_queue["QueueUrl"]
    result_queue_url = result_queue["QueueUrl"]
    concurrency = os.environ.get("CONCURRENCY", 3)
    manager = multiprocessing.Manager()
    active_processes = manager.dict()

    while True:
        try:
            time.sleep(5)
            print(active_processes)
            task_response = sqs.receive_message(
                QueueUrl=task_queue_url, MaxNumberOfMessages=1
            )
            if len(active_processes) < concurrency:
                if "Messages" in task_response:
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
            control_response = sqs.receive_message(
                QueueUrl=control_queue_url,
                MaxNumberOfMessages=1,
            )
            if "Messages" in control_response:
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
                    control_process = psutil.Process(
                        active_processes[data["task_id"]]["pid"]
                    )
                    if data["action"] == "delete":
                        control_process.kill()
                        del active_processes[data["task_id"]]
                    elif data["action"] == "suspend":
                        control_process.suspend()
                        active_processes[data["task_id"]]["status"] = "Suspended"
                    elif data["action"] == "resume":
                        control_process.resume()
                        active_processes[data["task_id"]]["status"] = "Resumed"
                elif data["action"] not in ["delete", "suspend", "resume"]:
                    control_receipt_handle = control_message["ReceiptHandle"]
                    sqs.delete_message(
                        QueueUrl=control_queue_url, ReceiptHandle=control_receipt_handle
                    )
                else:
                    pass
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")


if __name__ == "__main__":
    listen_to_sqs()
