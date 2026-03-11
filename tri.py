import requests
import time
import os

OWNER = "eyayq"
REPO = "eliv"

TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SLEEP_AFTER_ALL = 120  # 5 menit

WORKFLOW_GROUPS = [
    ["lve.yml", "lve0.yml"],
    ["lve2.yml", "auto.yml"],
    ["hh.yml", "kk.yml"],
    ["jj.yml", "ii.yml"],
    ["lve1.yml"]
]


def trigger_workflow(workflow):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/dispatches"

    data = {"ref": "main"}

    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print("Triggered:", workflow)
    else:
        print("Trigger failed:", workflow, r.text)


def get_latest_run(workflow):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/runs?per_page=1"

    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print("API error:", r.text)
        return None

    data = r.json()

    if data["workflow_runs"]:
        return data["workflow_runs"][0]["id"]

    return None


def wait_run_finish(run_id):

    while True:

        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"

        r = requests.get(url, headers=HEADERS)

        if r.status_code != 200:
            print("API error:", r.text)
            time.sleep(10)
            continue

        status = r.json()["status"]

        print("Run status:", status)

        if status == "completed":
            return

        time.sleep(10)


while True:

    print("===== START WORKFLOW QUEUE =====")

    for group in WORKFLOW_GROUPS:

        run_ids = []

        for wf in group:

            trigger_workflow(wf)

            time.sleep(3)

            run_id = get_latest_run(wf)

            if run_id:
                run_ids.append(run_id)

        print("Waiting group:", group)

        for rid in run_ids:
            wait_run_finish(rid)

        print("Group finished:", group)

    print("All workflows finished")

    print("Sleep", SLEEP_AFTER_ALL, "seconds")

    time.sleep(SLEEP_AFTER_ALL)
