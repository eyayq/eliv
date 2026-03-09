import requests
import time
import os

OWNER = "eyayq"
REPO = "eliv"

TOKEN = os.getenv("GH_TOKEN")

SLEEP_AFTER_ALL = 300  # 5 menit

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Grup workflow yang akan dijalankan bersamaan
WORKFLOW_GROUPS = [
    ["lve.yml", "lve0.yml"],
    ["lve2.yml", "auto.yml"],
    ["lve1.yml"]
]


def get_running_count():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=in_progress"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            print("API Error:", r.text)
            return 0

        data = r.json()

        return data.get("total_count", 0)

    except Exception as e:
        print("Request error:", e)
        return 0


def wait_until_finish():

    while True:

        running = get_running_count()

        print("Running workflow:", running)

        if running == 0:
            break

        time.sleep(10)


def trigger_workflow(workflow):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/dispatches"

    data = {"ref": "main"}

    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print("Triggered:", workflow)
    else:
        print("Trigger failed:", workflow, r.text)


while True:

    print("===== START WORKFLOW QUEUE =====")

    for group in WORKFLOW_GROUPS:

        wait_until_finish()

        for wf in group:
            trigger_workflow(wf)
            time.sleep(3)

        print("Waiting group to finish:", group)

        wait_until_finish()

        print("Group finished:", group)

    print("All workflows finished")

    print("Sleep", SLEEP_AFTER_ALL, "seconds")

    time.sleep(SLEEP_AFTER_ALL)
