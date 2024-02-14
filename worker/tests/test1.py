from executor import vw

def play(data):
    vw.run_job(data)


data = {
    "operation": "some testing operation",
    "params": {
        "task_id": "test_task_id",
        "gitea_url": "https://nimbus-dev-gitea.solytics.us/balgopal/ClimateRisk.git"
    }
}

play(data)

# "params":{"task_id": "test_task_id","gitea_url": "https://nimbus-dev-gitea.solytics.us/balgopal/ClimateRisk.git"}