#!/usr/bin/env bash
# The leads a signal produced, 1-100 per page. Free (a lead is charged once, when it is produced).
#
#   ./list-leads.sh <signalId> [since ISO-8601, e.g. 2026-10-01T00:00:00Z]
set -euo pipefail
. "$(dirname "$0")/_env.sh"

SIGNAL_ID="${1:?Usage: $0 <signalId> [since]}"
SINCE_ARG=()
[ -n "${2:-}" ] && SINCE_ARG=(--data-urlencode "since=$2")

curl -sS -G -X GET "$RODZ_BASE_URL/api/v1/signals/${SIGNAL_ID}/leads?limit=25&offset=0" \
  ${SINCE_ARG[@]+"${SINCE_ARG[@]}"} \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
# -> {"signalId": "...", "total": 42, "limit": 25, "offset": 0, "hasMore": true,
#     "leads": [{"signal": {...}, "contact": {...} or "", "company": {...}}]}
# A company-level lead (a funding round with no persona targeting...) has "contact": "".
