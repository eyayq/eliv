import requests

# =========================
# CONFIG
# =========================
OWNER = "OWNER"          # contoh: eyayq
REPO = "REPO"            # contoh: eliv
TOKEN = "GITHUB_TOKEN"   # personal access token

BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# =========================
# GET ALL WORKFLOW RUNS
# =========================
def get_runs():
    runs = []
    page = 1

    while True:
        url = f"{BASE_URL}?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        data = r.json()

        if "workflow_runs" not in data or len(data["workflow_runs"]) == 0:
            break

        runs.extend(data["workflow_runs"])
        page += 1

    return runs


# =========================
# DELETE RUN
# =========================
def delete_run(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    r = requests.delete(url, headers=headers)

    if r.status_code == 204:
        print(f"Deleted run {run_id}")
    else:
        print(f"Failed delete {run_id} : {r.status_code}")


# =========================
# MAIN
# =========================
def main():
    print("Fetching workflow runs...")

    runs = get_runs()
    print(f"Total runs found: {len(runs)}")

    for run in runs:
        run_id = run["id"]
        delete_run(run_id)

    print("Finished deleting workflow runs.")


if __name__ == "__main__":
    main()
