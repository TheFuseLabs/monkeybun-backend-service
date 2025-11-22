# GCP Deployment Guide

This guide walks through the setup and deployment process for the Monkeybun Backend Service on Google Cloud Platform.

## Prerequisites

Install the Google Cloud SDK on your local machine:

```bash
brew install --cask google-cloud-sdk
```

Authenticate with your Google Cloud account:

```bash
gcloud auth login
```

Set the default project:

```bash
gcloud config set project poptheshop
```

## Enable Required GCP Services

Enable the necessary Google Cloud APIs for deployment:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

This enables:

- **Cloud Run**: For hosting the containerized API
- **Artifact Registry**: For storing Docker images
- **Cloud Build**: For building container images
- **Secret Manager**: For securely storing environment variables

## Upload Secrets to GCP

Upload your environment variables to Google Secret Manager:

```bash
./scripts/upload_secrets_to_gcp.sh .env.prod
```

This script reads your local `.env` file and creates corresponding secrets in GCP Secret Manager.

## Local Testing

Before deploying, test the Docker container locally:

```bash
docker build -t monkeybun-backend-service .
docker run -p 8000:8000 --env-file .env monkeybun-backend-service
```

This builds the Docker image and runs it on port 8000 with your local environment variables.

## Service Account Setup

Create a service account for GitHub Actions to use during CI/CD:

```bash
gcloud iam service-accounts create github-actions-sa \
  --project=poptheshop \
  --display-name="GitHub Actions Service Account"
```

## Configure Service Account Permissions

Grant the service account the necessary permissions to deploy and manage resources:

### Artifact Registry Access

Allows the service account to push Docker images:

```bash
gcloud projects add-iam-policy-binding poptheshop \
  --member="serviceAccount:github-actions-sa@poptheshop.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### Cloud Run Admin Access

Allows the service account to deploy and manage Cloud Run services:

```bash
gcloud projects add-iam-policy-binding poptheshop \
  --member="serviceAccount:github-actions-sa@poptheshop.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Secret Manager Access

Allows the service account to read secrets during deployment:

```bash
gcloud projects add-iam-policy-binding poptheshop \
  --member="serviceAccount:github-actions-sa@poptheshop.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Service Usage Consumer

Allows the service account to consume GCP services:

```bash
gcloud projects add-iam-policy-binding poptheshop \
  --member="serviceAccount:github-actions-sa@poptheshop.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

## Generate Service Account Key

Create a key file for the service account to use in GitHub Actions:

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-sa@poptheshop.iam.gserviceaccount.com \
  --project=poptheshop
```

**Important**: Add `key.json` to your `.gitignore` and store the contents securely in GitHub Secrets.

## Grant Compute Service Account Access

Allow the service account to act as the Compute Engine service account:

```bash
PROJECT_NUMBER=$(gcloud projects describe poptheshop --format="value(projectNumber)")
gcloud iam service-accounts add-iam-policy-binding $PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --member="serviceAccount:github-actions-sa@poptheshop.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project=poptheshop
```

## Grant Secrets Access to Compute Service Account

Grant the Compute Engine service account access to all required secrets:

```bash
PROJECT_NUMBER=$(gcloud projects describe poptheshop --format="value(projectNumber)")
COMPUTE_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

for SECRET in POSTGRES_URL LOG_LEVEL SUPABASE_PUBLISHABLE_KEY SUPABASE_PROJECT_URL SUPABASE_PROJECT_REF SUPABASE_JWT_AUDIENCE SUPABASE_SERVICE_ROLE_KEY S3_REGION S3_ACCESS_KEY_ID S3_SECRET_ACCESS_KEY_ID S3_ENDPOINT SUPABASE_DEV_USERNAME SUPABASE_DEV_PASSWORD GOOGLE_PLACES_API_KEY RESEND_API_KEY; do
  echo "Granting access to $SECRET..."
  gcloud secrets add-iam-policy-binding mbbs_$SECRET \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/secretmanager.secretAccessor" \
    --project=poptheshop
done
```

This allows the Cloud Run service to access secrets at runtime.

## Configure Public Access

Make the Cloud Run service publicly accessible:

```bash
gcloud run services add-iam-policy-binding monkeybun-backend-service \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=poptheshop
```

This allows anyone on the internet to invoke the API endpoint. Remove this if you need to restrict access.
