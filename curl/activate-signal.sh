#!/usr/bin/env bash
# Turn a draft signal on (and optionally set where its leads are POSTed).
# An active signal is charged per lead delivered, up to its dailyLeadLimit.
#
#   ./activate-signal.sh <signalId> [https://your-server.example/webhooks/rodz]
set -euo pipefail
. "$(dirname "$0")/_env.sh"

SIGNAL_ID="${1:?Usage: $0 <signalId> [webhookUrl]}"
WEBHOOK_URL="${2:-}"
if [ -n "$WEBHOOK_URL" ]; then
  BODY="{\"status\": \"active\", \"webhookUrl\": \"$WEBHOOK_URL\"}"
else
  BODY='{"status": "active"}'
fi

curl -sS -X PATCH "$RODZ_BASE_URL/api/v1/signals/${SIGNAL_ID}" \
  -H "Authorization: Bearer $RODZ_API_KEY" \
  -H "Content-Type: application/json" \
  --data "$BODY"
echo
