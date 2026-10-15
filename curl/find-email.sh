#!/usr/bin/env bash
# Find a professional email from a name and a company domain, with deliverability status.
#
#   ./find-email.sh Marie Dupont doctolib.fr
set -euo pipefail
. "$(dirname "$0")/_env.sh"

FIRST="${1:?Usage: $0 <firstName> <lastName> <domain>}"; LAST="${2:?}"; DOMAIN="${3:?}"

curl -sS -G -X GET "$RODZ_BASE_URL/api/v1/enrichment/find-email" \
  --data-urlencode "firstName=$FIRST" \
  --data-urlencode "lastName=$LAST" \
  --data-urlencode "domain=$DOMAIN" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
# -> {"data": {"email": "...", "status": "Valid", ...}, "requestId": "..."}
