import requests
import os
import json
import time

secret_data = os.getenv("DELETE_LOG_CONFIG")

if not secret_data:
    print("Secret DELETE_LOG_CONFIG tidak ditemukan")
    exit(1)

config = json.loads(secret_data)

OWNER = config["OWNER"]
REPO = config["REPO"]
TOKEN = config["TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

session = requests.Session()
session.headers.update(HEADERS)


# =========================
# AMBIL SEMUA WORKFLOW RUN
# =========================
def get_all_runs():

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=100"

    runs = []

    while url:

        r = session.get(url)

        if r.status_code != 200:
            print("Gagal mengambil workflow runs:", r.status_code)
            break

        data = r.json()

        runs.extend(data.get("workflow_runs", []))

        url = r.links.get("next", {}).get("url")

    return runs


# =========================
# DELETE WORKFLOW RUN
# =========================
def delete_run(run_id):

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"

    r = session.delete(url)

    if r.status_code == 204:
        print("Deleted:", run_id)
        return True

    print("Failed delete:", run_id, r.status_code)
    return False


# =========================
# DELETE SEMUA LOG
# =========================
def delete_all():

    print("Mengambil semua workflow logs...")

    runs = get_all_runs()

    print("Total logs:", len(runs))

    if not runs:
        return

    for run in runs:

        delete_run(run["id"])

        time.sleep(0.3)


if __name__ == "__main__":

    print("Repository:", OWNER + "/" + REPO)

    delete_all()

    print("Selesai menghapus semua workflow logs")
