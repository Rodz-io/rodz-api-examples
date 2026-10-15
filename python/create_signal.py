"""Create a signal from one of the bodies in ../signals/.

    python create_signal.py job-changes             # people who just started a new job
    python create_signal.py fundraising             # companies that just raised a round
    python create_signal.py job-offers              # companies hiring for a role
    python create_signal.py competitor-connections  # people connecting with your competitors' teams

    python create_signal.py job-changes --activate --webhook https://your-server.example/webhooks/rodz

The bodies create a DRAFT: nothing runs and nothing is charged until the signal is active.
An active signal is charged per lead delivered, up to its dailyLeadLimit.
"""

import argparse
import json

from rodz import ROOT, rodz

CREATE = {
    "job-changes": "POST /api/v1/signals/job-changes",
    "fundraising": "POST /api/v1/signals/fundraising",
    "job-offers": "POST /api/v1/signals/job-offers",
    "competitor-connections": "POST /api/v1/signals/competitor-connections",
}

parser = argparse.ArgumentParser()
parser.add_argument("signal", choices=CREATE)
parser.add_argument("--activate", action="store_true", help="create it active instead of draft")
parser.add_argument("--webhook", help="URL that receives each lead as it is produced")
args = parser.parse_args()

body = json.loads((ROOT / "signals" / f"{args.signal}.json").read_text(encoding="utf-8"))
if args.activate:
    body["status"] = "active"
if args.webhook:
    body["webhookUrl"] = args.webhook

method, path = CREATE[args.signal].split(" ")
signal = rodz(method, path, json=body)
print(f"Created {signal['signalTypeId']} signal {signal['id']} ({signal['status']})")
for w in signal.get("warnings", []):
    print(f"  warning [{w['code']}]: {w['message']}")
