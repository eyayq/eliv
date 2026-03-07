import requests
import time
import os
import json

# =========================
# LOAD CONFIG FROM SECRET
# =========================

secret_data = os.getenv("TRIGGER_PY")

if not secret_data:
    print("Secret TRIGGER_PY tidak ditemukan")
    exit(1)

try:
    config = json.loads(secret_data)
except Exception as e:
    print("Format JSON secret salah:", e)
    exit(1)

OWNER = config.get("OWNER")
REPO = config.get("REPO")
TOKEN = config.get("TOKEN")
BRANCH = config.get("BRANCH", "main")
INTERVAL = int(config.get("INTERVAL", 300))

if not OWNER or not REPO or not TOKEN:
    print("OWNER / REPO / TOKEN tidak lengkap di secret")
    exit(1)

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
        print(f"[ERROR] {name}: {e}")

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
