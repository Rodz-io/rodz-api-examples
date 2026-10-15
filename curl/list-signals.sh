#!/usr/bin/env bash
# Your signals, with leadsToday / leadsTotal for each. Free.
set -euo pipefail
. "$(dirname "$0")/_env.sh"

curl -sS -X GET "$RODZ_BASE_URL/api/v1/signals?status=active&limit=50" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
