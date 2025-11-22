#!/bin/bash

set -e

KEY_FILE="${1:-key.json}"
SECRET_NAME="${2:-GCP_SA_KEY}"

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file '$KEY_FILE' not found."
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed or not in PATH."
    echo "Install it with: brew install gh"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Authenticate with: gh auth login"
    exit 1
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo "Error: Could not determine repository. Make sure you're in a git repository."
    exit 1
fi

echo "Uploading '$KEY_FILE' to GitHub Actions secret '$SECRET_NAME' for repository '$REPO'..."
echo ""

if cat "$KEY_FILE" | gh secret set "$SECRET_NAME"; then
    echo ""
    echo "✓ Successfully uploaded secret '$SECRET_NAME' to GitHub Actions"
    echo ""
    echo "You can verify it was set by running:"
    echo "  gh secret list"
else
    echo ""
    echo "✗ Failed to upload secret"
    exit 1
fi

