import requests
import time
import os

OWNER = "USERNAME_GITHUB"
REPO = "REPO_GITHUB"

TOKEN = os.getenv("GH_TOKEN")

WORKFLOWS = [
    "lve.yml",
    "lve0.yml",
    "lve2.yml",
    "auto.yml",
    "lve1.yml"
]

SLEEP_AFTER_ALL = 300   # 300 = 5 menit (ubah ke 600 jika ingin 10 menit)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def trigger(workflow):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/dispatches"

    data = {"ref": "main"}

    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print(f"Triggered {workflow}")
    else:
        print("Error trigger:", r.text)


def running_count():

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?status=in_progress"

    r = requests.get(url, headers=HEADERS)

    return r.json()["total_count"]


def wait_finish():

    while True:

        r = running_count()

        if r == 0:
            return

        print("Waiting workflow finish...")
        time.sleep(20)


while True:

    print("Start Runner Queue")

    for wf in WORKFLOWS:

        wait_finish()

        trigger(wf)

        time.sleep(8)

        wait_finish()

        print(f"{wf} finished")

    print("All workflows finished")

    print(f"Sleep {SLEEP_AFTER_ALL} seconds")

    time.sleep(SLEEP_AFTER_ALL)
