#!/usr/bin/env bash
# How many credits are left on the account. Free.
set -euo pipefail
. "$(dirname "$0")/_env.sh"

curl -sS -X GET "$RODZ_BASE_URL/api/v1/account/credits" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
# -> {"credits": 1234.5, "companyName": "Acme"}
