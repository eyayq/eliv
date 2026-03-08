#!/bin/bash

OWNER="OWNER"
REPO="REPO"
TOKEN="GITHUB_TOKEN"

PAGE=1

while true
do
  echo "Fetching page $PAGE"

  RESPONSE=$(curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=100&page=$PAGE")

  IDS=$(echo $RESPONSE | jq '.workflow_runs[].id')

  if [ -z "$IDS" ]; then
    echo "No more runs found."
    break
  fi

  for id in $IDS
  do
    echo "Cancelling run $id"

    curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/repos/$OWNER/$REPO/actions/runs/$id/cancel
  done

  PAGE=$((PAGE+1))

done

echo "Finished cancelling all workflow runs."
