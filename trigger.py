import requests
import time
import os

OWNER = "USERNAME_GITHUB"
REPO = "REPOSITORY_NAME"

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


def trigger_workflow(workflow):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/dispatches"

    data = {
        "ref": "main"
    }

    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print(f"Triggered {workflow}")
        return True
    else:
        print("Trigger Error:", r.text)
        return False


def get_running_count():

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=in_progress"

    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print("API Error:", r.text)
        return 1

    data = r.json()

    if "total_count" not in data:
        print("Unexpected API Response:", data)
        return 1

    return data["total_count"]


def wait_until_finish():

    while True:

        running = get_running_count()

        if running == 0:
            return

        print("Waiting workflow to finish...")
        time.sleep(20)


while True:

    print("Start Runner Queue")

    for workflow in WORKFLOWS:

        wait_until_finish()

        ok = trigger_workflow(workflow)

        if not ok:
            time.sleep(30)
            continue

        time.sleep(10)

        wait_until_finish()

        print(f"{workflow} finished")

    print("All workflows finished")

    print(f"Sleep {SLEEP_AFTER_ALL} seconds")

    time.sleep(SLEEP_AFTER_ALL)
