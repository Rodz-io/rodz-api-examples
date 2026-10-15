"""Receive Rodz leads on your own server. Standard library only.

    RODZ_WEBHOOK_SECRET=... python webhook_receiver.py      # listens on http://0.0.0.0:8000/webhooks/rodz

Expose it publicly (a server, or a tunnel while you test), set that URL as the signal's
webhookUrl, then send a sample lead with:  POST /api/v1/signals/{signalId}/test-webhook

What every delivery looks like (a signal-lead webhook is snake_case and nested):

    headers  X-Webhook-Id         the lead's id: the same on every retry and replay -> deduplicate on it
             X-Webhook-Signature  HMAC-SHA256 hex of  "<timestamp>." + raw body, keyed with your webhook secret
             X-Webhook-Timestamp  the <timestamp> above
    body     {"signal":  {"id", "name", "type", "last_signal", "last_signal_date", "heat_score", ...type fields},
              "contact": {"lead_id", "first_name", "last_name", "title", "email", "phone",
                          "linkedin_profile_url", "matched_persona", ...}   or ""  (company-level lead),
              "company": {"name", "website", "linkedin_url", "industry", "hq_city", "hq_country_code", ...}}

The webhook secret is under Integrations -> API in the Rodz dashboard.
Answer 2xx fast; a 5xx or a timeout is retried, a 4xx is not, a 429 asks Rodz to retry later.
"""

import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ.get("RODZ_WEBHOOK_SECRET", "")
PORT = int(os.environ.get("PORT", "8000"))
seen_ids = set()  # use your database in production


def signature_ok(body: bytes, signature: str, timestamp: str) -> bool:
    message = f"{timestamp}.".encode("utf-8") + body
    expected = hmac.new(SECRET.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhooks/rodz":
            return self._reply(404)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        if SECRET and not signature_ok(
            body, self.headers.get("X-Webhook-Signature"), self.headers.get("X-Webhook-Timestamp")
        ):
            return self._reply(401)

        delivery_id = self.headers.get("X-Webhook-Id")
        if delivery_id in seen_ids:  # a retry of a lead we already have
            return self._reply(200)
        seen_ids.add(delivery_id)

        lead = json.loads(body)
        signal, contact, company = lead["signal"], lead["contact"], lead["company"]
        tag = " [test]" if signal.get("is_test") else " [replay]" if signal.get("is_replay") else ""
        print(f"{signal['last_signal']} (heat {signal.get('heat_score')}){tag}: {company.get('name')}")
        if contact:  # "" when the lead is about a company, not a person
            print(f"  {contact.get('first_name')} {contact.get('last_name')}, {contact.get('title')} {contact.get('email')}")

        # Heavy work (CRM push, sequencing...) belongs in a queue: answer first.
        self._reply(200)

    def _reply(self, code):
        self.send_response(code)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not SECRET:
        print("RODZ_WEBHOOK_SECRET is not set: signatures are NOT verified (fine for a first test only).")
    print(f"Listening on http://0.0.0.0:{PORT}/webhooks/rodz")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
