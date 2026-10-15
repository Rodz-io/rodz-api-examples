#!/usr/bin/env bash
# The signal catalog: every signal you can create, its createEndpoint, its configParameters
# and its pricingModel (credits per lead). Free. Start here.
set -euo pipefail
. "$(dirname "$0")/_env.sh"

curl -sS -X GET "$RODZ_BASE_URL/api/v1/signal-types" \
  -H "Authorization: Bearer $RODZ_API_KEY"
echo
