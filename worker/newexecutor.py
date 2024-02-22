import os
import json
import time
import traceback
import multiprocessing
from constants import (
    sqs,
    task_queue,
    control_queue,
    result_queue,
)
from controllers import process_control_message, process_task_messages, get_process_metrics

def listen_to_sqs():
    task_queue_url = task_queue["QueueUrl"]
    control_queue_url = control_queue["QueueUrl"]
    result_queue_url = result_queue["QueueUrl"]
    concurrency = int(os.environ.get("CONCURRENCY", 3))
    manager = multiprocessing.Manager()
    active_processes = manager.dict()

    while True:
        try:
            time.sleep(5)
            
            metrics = get_process_metrics(active_processes)
            sqs.send_message(
                QueueUrl=result_queue_url,
                MessageBody=json.dumps(metrics)
            )
            
            control_response = sqs.receive_message(
                QueueUrl=control_queue_url,
                MaxNumberOfMessages=1,
            )
            if "Messages" in control_response:
                active_processes = process_control_message(
                    control_response=control_response,
                    active_processes=active_processes,
                    control_queue_url=control_queue_url
                )
            
            task_response = sqs.receive_message(
                QueueUrl=task_queue_url, MaxNumberOfMessages=1
            )
            if len(active_processes) < concurrency:
                if "Messages" in task_response:
                    active_processes = process_task_messages(
                        task_response=task_response, 
                        task_queue_url=task_queue_url,
                        active_processes=active_processes, 
                        result_queue_url=result_queue_url
                    )
            
            print(active_processes)
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")


if os.environ.get("ARCHITECTURE","queue") == "queue":
    listen_to_sqs()
