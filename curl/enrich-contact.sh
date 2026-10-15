#!/usr/bin/env bash
# Full professional profile of a person from a LinkedIn URL (or email, or name + company).
# freshness=cached: 0.25 credits, answered in about a second from a profile at most 8 days old.
# freshness=live (default): 0.5 credits, fetched at request time.
#
#   ./enrich-contact.sh https://www.linkedin.com/in/some-profile
set -euo pipefail
. "$(dirname "$0")/_env.sh"

PROFILE_URL="${1:?Usage: $0 <LinkedIn profile URL>}"

curl -sS -G -X GET "$RODZ_BASE_URL/api/v1/enrichment/contact?freshness=cached" \
  --data-urlencode "url=$PROFILE_URL" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
# -> {"data": {"person": {"firstName": ..., "headline": ..., "currentCompanyDetail": [...], ...}},
#     "requestId": "..."}
