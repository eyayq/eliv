import requests
import time
import os

OWNER = "eyayq"
REPO = "eliv"

TOKEN = os.getenv("GH_TOKEN")

WORKFLOWS = [
    "lve.yml",
    "lve0.yml",
    "lve2.yml",
    "auto.yml",
    "lve1.yml"
]

SLEEP_AFTER_ALL = 300  # 5 menit

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_running_count():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=in_progress"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            print("API Error:", r.text)
            return 0

        data = r.json()

        if "total_count" in data:
            return data["total_count"]

        print("Unexpected API response:", data)
        return 0

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

    data = {
        "ref": "main"
    }

    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print("Triggered:", workflow)
    else:
        print("Trigger failed:", r.text)


while True:

    print("===== START RUNNER QUEUE =====")

    for wf in WORKFLOWS:

        wait_until_finish()

        trigger_workflow(wf)

        time.sleep(5)

        wait_until_finish()

        print(wf, "finished")

    print("All workflows finished")

    print("Sleeping", SLEEP_AFTER_ALL, "seconds")

    time.sleep(SLEEP_AFTER_ALL)
