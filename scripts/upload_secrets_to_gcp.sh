#!/bin/bash

set -e

ENV_FILE="${1:-.env}"
PROJECT_ID="${GCP_PROJECT_ID:-poptheshop}"
SECRET_PREFIX="mbbs_"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file '$ENV_FILE' not found."
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed or not in PATH."
    exit 1
fi

echo "Uploading secrets from '$ENV_FILE' to GCP Secrets Manager (project: $PROJECT_ID)..."
echo ""

SECRET_COUNT=0
SUCCESS_COUNT=0
FAILED_COUNT=0

while IFS= read -r line || [ -n "$line" ]; do
    line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
        continue
    fi
    
    if [[ ! "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
        continue
    fi
    
    ENV_VAR_NAME=$(echo "$line" | cut -d'=' -f1)
    SECRET_VALUE=$(echo "$line" | cut -d'=' -f2- | sed 's/^"//;s/"$//')
    
    if [ -z "$ENV_VAR_NAME" ]; then
        continue
    fi

    SECRET_NAME="${SECRET_PREFIX}${ENV_VAR_NAME}"
    
    SECRET_COUNT=$((SECRET_COUNT + 1))
    
    echo -n "Processing $ENV_VAR_NAME (as $SECRET_NAME)... "
    
    if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
        echo -n "$SECRET_VALUE" | gcloud secrets versions add "$SECRET_NAME" \
            --data-file=- \
            --project="$PROJECT_ID" &>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✓ Updated"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "✗ Failed to update"
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    else
        echo -n "$SECRET_VALUE" | gcloud secrets create "$SECRET_NAME" \
            --data-file=- \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" &>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✓ Created"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "✗ Failed to create"
            FAILED_COUNT=$((FAILED_COUNT + 1))
        fi
    fi
done < "$ENV_FILE"

echo ""
echo "Summary:"
echo "  Total secrets processed: $SECRET_COUNT"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAILED_COUNT"

if [ $FAILED_COUNT -gt 0 ]; then
    exit 1
fi

