#!/usr/bin/env bash

set -euo pipefail

if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "Fetching all workflow runs..."
echo ""

RUN_IDS=$(gh run list --limit 1000 --json databaseId --jq '.[].databaseId')

if [ -z "$RUN_IDS" ]; then
    echo "No workflow runs found."
    exit 0
fi

TOTAL=$(echo "$RUN_IDS" | wc -l | xargs)
echo "Found $TOTAL workflow run(s) to delete."
echo ""

CURRENT=0
for RUN_ID in $RUN_IDS; do
    CURRENT=$((CURRENT + 1))
    echo "[$CURRENT/$TOTAL] Deleting workflow run: $RUN_ID"
    gh run delete "$RUN_ID" --yes 2>/dev/null || echo "  Warning: Failed to delete run $RUN_ID (may already be deleted)"
done

echo ""
echo "Workflow runs deletion complete!"

