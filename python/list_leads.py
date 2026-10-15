"""Print every lead a signal produced (pages through all of them). Free.

    python list_leads.py <signalId> [--since 2026-10-01T00:00:00Z]
"""

import argparse

from rodz import rodz

parser = argparse.ArgumentParser()
parser.add_argument("signal_id")
parser.add_argument("--since", help="only leads produced at or after this ISO-8601 time")
args = parser.parse_args()
signal_id = args.signal_id

offset = 0
while True:
    params = {"limit": 100, "offset": offset}
    if args.since:
        params["since"] = args.since
    page = rodz("GET", f"/api/v1/signals/{signal_id}/leads", params=params)
    for lead in page["leads"]:
        company = lead["company"]
        contact = lead["contact"]  # "" for a company-level lead (e.g. a funding round without personas)
        who = f"{contact['first_name']} {contact['last_name']} ({contact['title']})" if contact else "-"
        print(f"{lead['signal']['last_signal_date']}  {company['name']:<30} {who}  {contact and contact['email']}")
    if not page["hasMore"]:
        break
    offset += page["limit"]
print(f"{page['total']} leads")
