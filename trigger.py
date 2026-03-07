import requests
import time
import os

# =========================
# CONFIG (ENVIRONMENT)
# =========================
OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
TOKEN = os.getenv("TOKEN")
BRANCH = os.getenv("BRANCH", "main")
INTERVAL = int(os.getenv("INTERVAL", "300"))

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
    try:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows"
        r = session.get(url, timeout=30)

        if r.status_code != 200:
            print("Gagal mengambil workflow:", r.status_code)
            return []

        data = r.json()
        return data.get("workflows", [])

    except Exception as e:
        print("Error ambil workflow:", e)
        return []


# =========================
# TRIGGER WORKFLOW
# =========================
def trigger_workflow(workflow_id, name):
    try:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow_id}/dispatches"

        payload = {"ref": BRANCH}

        r = session.post(url, json=payload, timeout=30)

        if r.status_code == 204:
            print(f"[OK] {name}")

        elif r.status_code == 403:
            print(f"[LIMIT] {name}")

        else:
            print(f"[FAIL] {name} -> {r.status_code}")

    except Exception as e:
        print(f"[ERROR] {name}:", e)


# =========================
# RUN SEMUA WORKFLOW
# =========================
def run_all_workflows():
    workflows = get_workflows()

    if not workflows:
        print("Tidak ada workflow ditemukan")
        return

    for wf in workflows:

        name = wf.get("name", "unknown")
        workflow_id = wf.get("id")

        if not workflow_id:
            continue

        if wf.get("state") != "active":
            print(f"[SKIP] {name}")
            continue

        trigger_workflow(workflow_id, name)


# =========================
# LOOP UTAMA
# =========================
def main():
    while True:

        print("=================================")
        print("Trigger semua workflow")
        print("Repository:", OWNER + "/" + REPO)
        print("=================================")

        run_all_workflows()

        print(f"Menunggu {INTERVAL} detik...\n")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
