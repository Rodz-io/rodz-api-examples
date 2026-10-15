#!/usr/bin/env bash
# Send a sample lead (signal.is_test = true) to a webhook, to check your receiver before
# real leads arrive. Free.
#
#   ./test-webhook.sh <signalId> [https://your-server.example/webhooks/rodz]
# Without a URL, the signal's saved webhookUrl is used.
set -euo pipefail
. "$(dirname "$0")/_env.sh"

SIGNAL_ID="${1:?Usage: $0 <signalId> [url]}"
URL="${2:-}"
BODY='{}'
[ -n "$URL" ] && BODY="{\"url\": \"$URL\"}"

curl -sS -X POST "$RODZ_BASE_URL/api/v1/signals/${SIGNAL_ID}/test-webhook" \
  -H "Authorization: Bearer $RODZ_API_KEY" \
  -H "Content-Type: application/json" \
  --data "$BODY"
echo
# -> {"success": true, "statusCode": 200, "signed": true, "payloadSent": {...}, ...}
