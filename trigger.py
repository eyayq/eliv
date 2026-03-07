import requests
import time
import os
import json

secret_data = os.getenv("TRIGGER_PY")

if not secret_data:
    print("Secret TRIGGER_PY tidak ditemukan")
    exit(1)

config = json.loads(secret_data)

OWNER = config.get("OWNER")
REPO = config.get("REPO")
TOKEN = config.get("TOKEN")
BRANCH = config.get("BRANCH", "main")
INTERVAL = int(config.get("INTERVAL", 300))

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

session = requests.Session()
session.headers.update(HEADERS)


# =========================
# AMBIL WORKFLOW
# =========================
def get_workflows():

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows"
    r = session.get(url)

    workflows = []

    if r.status_code == 200:
        for wf in r.json().get("workflows", []):
            if wf["state"] == "active":
                workflows.append((wf["id"], wf["name"]))

    return workflows


# =========================
# TRIGGER WORKFLOW
# =========================
def trigger_workflow(workflow_id, name):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow_id}/dispatches"

    payload = {"ref": BRANCH}

    r = session.post(url, json=payload)

    if r.status_code == 204:
        print("[TRIGGERED]", name)
        return True

    print("[FAIL TRIGGER]", name, r.status_code)
    return False


# =========================
# AMBIL RUN TERBARU
# =========================
def get_latest_run(workflow_id):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow_id}/runs?per_page=1"

    r = session.get(url)

    if r.status_code != 200:
        return None

    runs = r.json().get("workflow_runs", [])

    if not runs:
        return None

    return runs[0]


# =========================
# CEK STATUS WORKFLOW
# =========================
def check_status(workflows):

    finished = {}
    failed = []

    for workflow_id, name in workflows:

        run = get_latest_run(workflow_id)

        if not run:
            continue

        status = run["status"]
        conclusion = run["conclusion"]

        if status != "completed":
            continue

        finished[workflow_id] = True

        print(name, "->", conclusion)

        if conclusion != "success":
            failed.append((workflow_id, name))

    return finished, failed


# =========================
# JALANKAN SEMUA DAN MONITOR
# =========================
def run_all():

    workflows = get_workflows()

    if not workflows:
        print("Tidak ada workflow aktif")
        return

    print("\nTrigger semua workflow")

    for workflow_id, name in workflows:
        trigger_workflow(workflow_id, name)
        time.sleep(2)

    remaining = workflows

    while True:

        print("\nCek status workflow...")

        finished, failed = check_status(remaining)

        if len(finished) == len(remaining):

            if not failed:
                print("\nSEMUA WORKFLOW BERHASIL")
                return

            print("\nAda workflow gagal, membuat run baru")

            remaining = []

            for workflow_id, name in failed:

                trigger_workflow(workflow_id, name)

                remaining.append((workflow_id, name))

                time.sleep(2)

        time.sleep(15)


# =========================
# LOOP UTAMA
# =========================
def main():

    while True:

        print("\n============================")
        print("Repository:", OWNER + "/" + REPO)
        print("============================")

        run_all()

        print("\nMenunggu", INTERVAL, "detik")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
