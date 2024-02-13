import os, subprocess, venv,json

def play():
    venv.create(env_dir="test", with_pip=True,system_site_packages=True)
    myenv = os.environ.copy()
    myenv.update({
        "venv_path": "test",
        "params": json.dumps({
            "gitea_url":"https://nimbus-dev-gitea.solytics.us/balgopal/ClimateRisk.git"
        })
    })
    subprocess.run(["test/bin/python","/code/worker/task.py"],env=myenv)

play()