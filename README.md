# Rodz API examples

**Rodz detects buying signals (job changes, funding rounds, hiring, people engaging with your competitors, technology adoption, public tenders and more) and delivers each matching prospect as an enriched lead, to your webhook, your CRM or your sales tool.**
Rodz produces 46 signal types (<https://www.rodz.io/en/product/signals/>). With the API you create a signal, set its filters, and receive each new lead (the person, their company and the event that triggered it) by webhook or by polling. Pay per lead delivered, in credits; data hosted in Europe. API reference: <https://api.rodz.io/docs>. Overview: <https://www.rodz.io/en/api/>.

Short, runnable examples in **curl**, **Python** (`requests`) and **JavaScript** (Node 18+ `fetch`, no dependencies), plus how to plug Rodz into **Claude** with MCP.

**Who this is for:** developers adding buying signals to a product, a CRM sync or an internal tool; growth and RevOps teams wiring signals into n8n, Make or Clay through webhooks; builders of AI agents that need fresh B2B events through MCP.

## Use cases

| I want to... | Signal | curl | Python | JavaScript |
|---|---|---|---|---|
| **Get alerted when decision-makers change jobs** (new buyers in their first 90 days, past champions at a new company) | [`job-changes`](signals/job-changes.json) | [create-signal.sh](curl/create-signal.sh) `job-changes` | [create_signal.py](python/create_signal.py) `job-changes` | [create-signal.mjs](javascript/create-signal.mjs) `job-changes` |
| **Track funding rounds** (companies with fresh budget, and their CEO) | [`fundraising`](signals/fundraising.json) | [create-signal.sh](curl/create-signal.sh) `fundraising` | [create_signal.py](python/create_signal.py) `fundraising` | [create-signal.mjs](javascript/create-signal.mjs) `fundraising` |
| **Find companies hiring** for a role you sell to (hiring = budget) | [`job-offers`](signals/job-offers.json) | [create-signal.sh](curl/create-signal.sh) `job-offers` | [create_signal.py](python/create_signal.py) `job-offers` | [create-signal.mjs](javascript/create-signal.mjs) `job-offers` |
| **See who engages with your competitors on LinkedIn** (new connections of their sales teams) | [`competitor-connections`](signals/competitor-connections.json) | [create-signal.sh](curl/create-signal.sh) `competitor-connections` | [create_signal.py](python/create_signal.py) `competitor-connections` | [create-signal.mjs](javascript/create-signal.mjs) `competitor-connections` |
| **Read the leads** a signal produced | | [list-leads.sh](curl/list-leads.sh) | [list_leads.py](python/list_leads.py) | [list-leads.mjs](javascript/list-leads.mjs) |
| **Receive leads in real time** on a webhook (signature check, retries, dedup) | | [test-webhook.sh](curl/test-webhook.sh) | [webhook_receiver.py](python/webhook_receiver.py) | [webhook-receiver.mjs](javascript/webhook-receiver.mjs) |
| **Enrich a contact** (LinkedIn profile, professional email) or **a company** | | [enrich-contact.sh](curl/enrich-contact.sh), [find-email.sh](curl/find-email.sh), [enrich-company.sh](curl/enrich-company.sh) | [enrich.py](python/enrich.py) | [enrich.mjs](javascript/enrich.mjs) |
| **Check your credit balance** and what you spent | | [check-credits.sh](curl/check-credits.sh) | [check_credits.py](python/check_credits.py) | [check-credits.mjs](javascript/check-credits.mjs) |
| **Connect Claude via MCP** and drive all of the above in plain language | | | | [claude-mcp/](claude-mcp/README.md) |

The four signal bodies in [`signals/`](signals/) are shared by the three languages. Edit them (titles, locations, company sizes...) and run.

## Quick start

1. Create an API key in the Rodz dashboard under **Integrations → API**.
2. `cp .env.example .env` and paste the key after `RODZ_API_KEY=`.
3. Run an example:

```bash
# curl
bash curl/check-credits.sh
bash curl/create-signal.sh job-changes

# Python
pip install -r python/requirements.txt
python python/check_credits.py
python python/create_signal.py fundraising

# JavaScript (Node 18+)
node javascript/check-credits.mjs
node javascript/create-signal.mjs job-offers
```

## What it costs

- **Creating a signal is free.** The bodies here create it as a **draft**: nothing runs and nothing is charged until you set `"status": "active"` (`--activate` in the Python and JavaScript examples, or [activate-signal.sh](curl/activate-signal.sh)).
- An active signal is charged **per lead delivered**, up to its `dailyLeadLimit` (20 in these bodies). The credits per lead of every signal type, and its paid add-ons, are in `pricingModel` from `GET /api/v1/signal-types` ([list-signal-types.sh](curl/list-signal-types.sh), [list_signal_types.py](python/list_signal_types.py)).
- Contact enrichment: **0.25 credits** with `freshness=cached` (profile at most 8 days old, about 1 s), **0.5 credits** with `freshness=live`.
- Reading your signals, leads, credits and the signal catalog is free.

## How the API works, in five lines

- `Authorization: Bearer USR_...` on every call; base URL `https://api.rodz.io`.
- REST requests and responses are **camelCase** (`webhookUrl`, `dailyLeadLimit`, `signalTypeId`).
- A lead delivered to your webhook is **snake_case and nested**: `signal`, `contact`, `company` (`contact.first_name`, `company.linkedin_url`). A lead about a company rather than a person has `"contact": ""`.
- Each delivery carries `X-Webhook-Id` (the same on every retry: deduplicate on it) and `X-Webhook-Signature` / `X-Webhook-Timestamp` (HMAC-SHA256 of `"<timestamp>." + body` with your webhook secret).
- An error carries a `code` and a `message` (for example `INVALID_API_KEY`); a `429` comes with `Retry-After`.

## Checked against the live spec

Every request body, endpoint and query parameter in this repository is checked against the published OpenAPI spec:

```bash
python scripts/validate_against_spec.py
```

No API key needed, nothing is created, no credits are spent.

## FAQ

**Is there an API for job change alerts?**
Yes. Create a `job-changes` signal ([body](signals/job-changes.json)) with the job titles, locations and company sizes you target, and every decision-maker who starts a new role in that scope is delivered as a lead to your webhook or read with `GET /api/v1/signals/{id}/leads`.

**Can I get new funding rounds through an API?**
Yes. A `fundraising` signal ([body](signals/fundraising.json)) delivers each newly announced round that matches your filters as a lead, with the company and the decision-maker to contact.

**Can an AI agent use Rodz?**
Yes. Rodz runs a hosted MCP server at `https://api.rodz.io/mcp`: Claude, Claude Code, Cursor or any MCP client can create signals, read leads and enrich contacts in plain language. Setup: [claude-mcp/](claude-mcp/README.md) and <https://www.rodz.io/en/rodz-in-claude/>.

**How is it priced?**
Per lead delivered, in credits, with no subscription; the credits per lead of each signal type come from `GET /api/v1/signal-types` (see [What it costs](#what-it-costs)). Credit packs: <https://www.rodz.io/en/pricing/>.

## Links

- API overview: <https://www.rodz.io/en/api/> (French: <https://www.rodz.io/fr/api/>)
- API reference: <https://api.rodz.io/docs> (OpenAPI: <https://api.rodz.io/openapi.json>)
- Rodz in Claude (MCP): <https://www.rodz.io/en/rodz-in-claude/>
- The 46 signal types: <https://www.rodz.io/en/product/signals/>
- Pricing: <https://www.rodz.io/en/pricing/>
- Support: support@rodz.io

Topics: buying signals, intent signals, trigger events, job change alerts, funding round alerts, B2B lead generation API, sales intelligence, MCP server, webhooks.

MIT licence.
