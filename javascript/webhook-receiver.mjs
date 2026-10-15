// Receive Rodz leads on your own server. Node 18+, no dependencies.
//
//   RODZ_WEBHOOK_SECRET=... node webhook-receiver.mjs     # listens on http://0.0.0.0:8000/webhooks/rodz
//
// Expose it publicly, set that URL as the signal's webhookUrl, then send a sample lead with
// POST /api/v1/signals/{signalId}/test-webhook
//
// Every delivery (a signal-lead webhook is snake_case and nested):
//   X-Webhook-Id         the lead's id, the same on every retry and replay: deduplicate on it
//   X-Webhook-Signature  HMAC-SHA256 hex of "<timestamp>." + raw body, keyed with your webhook secret
//   X-Webhook-Timestamp  that timestamp
//   body: { signal: {...}, contact: {...} or "", company: {...} }
// The webhook secret is under Integrations -> API in the Rodz dashboard.
// Answer 2xx fast; a 5xx or a timeout is retried, a 4xx is not, a 429 asks Rodz to retry later.
import { createHmac, timingSafeEqual } from 'node:crypto';
import { createServer } from 'node:http';

const SECRET = process.env.RODZ_WEBHOOK_SECRET || '';
const PORT = Number(process.env.PORT || 8000);
const seenIds = new Set(); // use your database in production

function signatureOk(rawBody, signature = '', timestamp = '') {
  const expected = createHmac('sha256', SECRET).update(`${timestamp}.`).update(rawBody).digest('hex');
  return expected.length === signature.length && timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}

createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/webhooks/rodz') return res.writeHead(404).end();
  const chunks = [];
  req.on('data', (c) => chunks.push(c));
  req.on('end', () => {
    const raw = Buffer.concat(chunks);
    if (SECRET && !signatureOk(raw, req.headers['x-webhook-signature'], req.headers['x-webhook-timestamp'])) {
      return res.writeHead(401).end();
    }
    const id = req.headers['x-webhook-id'];
    if (seenIds.has(id)) return res.writeHead(200).end(); // a retry of a lead we already have
    seenIds.add(id);

    const { signal, contact, company } = JSON.parse(raw.toString('utf8'));
    const tag = signal.is_test ? ' [test]' : signal.is_replay ? ' [replay]' : '';
    console.log(`${signal.last_signal} (heat ${signal.heat_score})${tag}: ${company?.name}`);
    // contact is "" when the lead is about a company, not a person
    if (contact) console.log(`  ${contact.first_name} ${contact.last_name}, ${contact.title} ${contact.email}`);

    res.writeHead(200).end(); // heavy work (CRM push, sequencing...) belongs in a queue
  });
}).listen(PORT, () => {
  if (!SECRET) console.log('RODZ_WEBHOOK_SECRET is not set: signatures are NOT verified (fine for a first test only).');
  console.log(`Listening on http://0.0.0.0:${PORT}/webhooks/rodz`);
});
