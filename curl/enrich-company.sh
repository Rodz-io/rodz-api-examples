#!/usr/bin/env bash
# Company size, industry, headquarters, founding year, description... from a domain
# (or a company name, or a LinkedIn company URL).
#
#   ./enrich-company.sh doctolib.fr
set -euo pipefail
. "$(dirname "$0")/_env.sh"

DOMAIN="${1:?Usage: $0 <domain>}"

curl -sS -G -X GET "$RODZ_BASE_URL/api/v1/enrichment/firmographic" \
  --data-urlencode "domain=$DOMAIN" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
# -> {"data": {"company": {"firmographics": {"name": ..., "companySize": "51-200",
#     "industries": ..., "HQcity": ..., "founded": ...}}}, "requestId": "..."}
