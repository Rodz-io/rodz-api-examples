#!/usr/bin/env bash
# Create a signal from one of the bodies in ../signals/.
#
#   ./create-signal.sh job-changes             # people who just started a new job
#   ./create-signal.sh fundraising             # companies that just raised a round
#   ./create-signal.sh job-offers              # companies hiring for a role
#   ./create-signal.sh competitor-connections  # people connecting with your competitors' teams
#
# The bodies create the signal as a DRAFT: nothing runs and nothing is charged until you
# set "status": "active". Add "webhookUrl" to receive each lead as it is produced, or read
# the leads later with list-leads.sh.
set -euo pipefail
. "$(dirname "$0")/_env.sh"

SIGNAL="${1:?Usage: $0 job-changes|fundraising|job-offers|competitor-connections}"
BODY="$SIGNALS_DIR/$SIGNAL.json"
[ -f "$BODY" ] || { echo "No body $BODY" >&2; exit 1; }

case "$SIGNAL" in
  job-changes)            ENDPOINT="POST /api/v1/signals/job-changes" ;;
  fundraising)            ENDPOINT="POST /api/v1/signals/fundraising" ;;
  job-offers)             ENDPOINT="POST /api/v1/signals/job-offers" ;;
  competitor-connections) ENDPOINT="POST /api/v1/signals/competitor-connections" ;;
  *) echo "Unknown signal $SIGNAL" >&2; exit 1 ;;
esac

curl -sS -X "${ENDPOINT%% *}" "$RODZ_BASE_URL${ENDPOINT#* }" \
  -H "Authorization: Bearer $RODZ_API_KEY" \
  -H "Content-Type: application/json" \
  --data @"$BODY"
echo
# -> 201 with the signal: {"id": "...", "status": "draft", "signalTypeId": "...", "config": {...},
#    "applied": {...}, "warnings": [...]}  Read "warnings": they flag filter values that
#    are probably not what you meant.
