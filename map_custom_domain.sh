#!/usr/bin/env bash
# ==============================================================================
# Map Custom Domain stackmf.com to Google Cloud Run
# Usage: ./map_custom_domain.sh [subdomain]
# Default maps stackmf.com and www.stackmf.com
# ==============================================================================
PROJECT_ID="serviceapartments"
REGION="us-central1"
SERVICE="stackmf"
DOMAIN="${1:-stackmf.com}"

echo "========================================================="
echo "Creating Cloud Run Domain Mapping for: ${DOMAIN}"
echo "Service: ${SERVICE} in Region: ${REGION}"
echo "========================================================="

gcloud beta run domain-mappings create \
  --project="${PROJECT_ID}" \
  --service="${SERVICE}" \
  --domain="${DOMAIN}" \
  --region="${REGION}"

echo ""
echo "========================================================="
echo "✅ HOSTINGER DNS SETUP INSTRUCTIONS FOR ${DOMAIN}"
echo "========================================================="
echo "1. Log into your Hostinger hPanel: https://hpanel.hostinger.com"
echo "2. Go to: Domains -> stackmf.com -> DNS / Nameservers"
echo "3. Add the following records as instructed by Google Cloud:"
echo "   - For root domain (stackmf.com): A / AAAA records provided by Cloud Run"
echo "   - For subdomains (e.g. www.stackmf.com):"
echo "     * Type:       CNAME"
echo "     * Name:       www"
echo "     * Target:     ghs.googlehosted.com."
echo "     * TTL:        300 (or default)"
echo "4. Click 'Add Record'."
echo ""
echo "Google Cloud will automatically provision a free Managed SSL certificate (HTTPS) within ~15 minutes!"
