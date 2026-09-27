#!/usr/bin/env bash
# ==============================================================================
# One-Click Setup for GitHub Actions CI/CD to Google Cloud Run
# Project: serviceapartments | Service: stackmf
# ==============================================================================
set -e

PROJECT_ID="serviceapartments"
SA_NAME="github-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "========================================================="
echo "1. Configuring GCP Project: ${PROJECT_ID}"
echo "========================================================="
gcloud config set project "${PROJECT_ID}"

echo "========================================================="
echo "2. Enabling Required Free-Tier GCP APIs..."
echo "========================================================="
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com

echo "========================================================="
echo "3. Verifying CI/CD Service Account: ${SA_NAME}"
echo "========================================================="
if ! gcloud iam service-accounts describe "${SA_EMAIL}" &>/dev/null; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub Actions Cloud Run Deployer"
  echo "Service account created."
else
  echo "Service account ${SA_EMAIL} already exists and ready."
fi

echo "========================================================="
echo "4. Assigning Deployment Permissions..."
echo "========================================================="
ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/cloudbuild.builds.editor"
  "roles/artifactregistry.admin"
  "roles/storage.admin"
)

for ROLE in "${ROLES[@]}"; do
  echo "Granting ${ROLE}..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None &>/dev/null || true
done

echo "========================================================="
echo "5. Generating Service Account Key for GitHub Secrets..."
echo "========================================================="
KEY_FILE="gcp-key.json"
gcloud iam service-accounts keys create "${KEY_FILE}" \
  --iam-account="${SA_EMAIL}"

echo ""
echo "========================================================="
echo "✅ SETUP COMPLETE! COPY THE JSON BELOW INTO GITHUB SECRETS"
echo "========================================================="
echo "1. Go to: https://github.com/anshuagrawal86/stackmf/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name:  GCP_SA_KEY"
echo "4. Value: (Copy and paste the entire JSON below)"
echo "---------------------------------------------------------"
cat "${KEY_FILE}"
echo ""
echo "---------------------------------------------------------"
rm -f "${KEY_FILE}"
echo "Service account key securely displayed above and deleted from local storage."
