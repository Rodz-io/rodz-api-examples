# Connect Claude to Rodz (MCP)

Rodz runs a hosted MCP server, so Claude can set up and tune your signals, read their leads, check your credits and enrich people and companies, in plain language.

- **URL:** `https://api.rodz.io/mcp` (Streamable HTTP)
- **Sign-in:** your Rodz account (OAuth) in Claude on the web, Desktop and mobile; or your API key as `Authorization: Bearer USR_...` in Claude Code, Cursor and any tool that lets you set a header.
- Every tool call is an ordinary API call on your account: same rate limits, same credit prices as the REST API. Tools that spend credits say so and give the price. A signal created as a **draft** costs nothing until you activate it.

## Claude (web, Desktop, mobile): custom connector

1. In Claude, open **Settings → Connectors** and click **Add custom connector** (on Team and Enterprise plans an owner adds it under **Organization settings → Connectors**, then each member connects).
2. Name it `Rodz`, paste `https://api.rodz.io/mcp`, leave the advanced OAuth fields empty, click **Add**.
3. Click **Connect**, sign in to Rodz, check the account shown and click **Allow**.
4. In a chat, enable Rodz from the tools menu.

A connector added on claude.ai is also available in Claude Desktop and the mobile apps. You can revoke it at any time under **Settings → Connected apps** in the Rodz dashboard.

### Claude Desktop with an API key instead (optional)

Claude Desktop reaches the hosted server through the open-source `mcp-remote` bridge (Node.js 18+). Add this to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), then restart Claude Desktop:

```json
{
  "mcpServers": {
    "rodz": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.rodz.io/mcp", "--header", "Authorization:${RODZ_AUTH}"],
      "env": { "RODZ_AUTH": "Bearer USR_your_api_key_here" }
    }
  }
}
```

## Claude Code

```bash
claude mcp add --transport http rodz https://api.rodz.io/mcp \
  --header "Authorization: Bearer USR_your_api_key_here"
```

Without `--header`, Claude Code signs in with your Rodz account instead: run `/mcp` and choose **Authenticate**.

Cursor works the same way: in `~/.cursor/mcp.json`, add `"rodz": { "url": "https://api.rodz.io/mcp", "headers": { "Authorization": "Bearer USR_your_api_key_here" } }` under `mcpServers`.

## The tools

`list_signal_types`, `list_personas`, `list_industries`, `list_technographic_tools`, `list_signals`, `get_signal`, `create_signal`, `update_signal`, `pause_signal`, `resume_signal`, `delete_signal`, `get_signal_funnel`, `list_signal_leads`, `list_watched_companies`, `add_watched_companies`, `get_credit_balance`, `get_credit_usage`, `enrich_contact`, `enrich_company`, `find_email`, `search_companies`, `search_people`, `start_phone_lookup`, `get_phone_lookup_result`.

## 5 prompts to start with

1. **Get alerted on job changes**
   > Create a draft job-change signal for Sales Directors and Heads of Revenue who just joined a 51-500 employee company in France. Show me the config before you activate it.

2. **Track funding rounds**
   > Which signal type tells me a company just raised money? Set one up for seed to Series B rounds in France over 1M, targeting the CEO, as a draft.

3. **Find companies hiring**
   > Set up a draft signal for companies in France posting SDR or Business Developer jobs this week, and give me the Sales Director at each one.

4. **See who engages with your competitors on LinkedIn**
   > Watch the new LinkedIn connections of my competitor's sales team (https://www.linkedin.com/company/your-competitor) and keep only marketing and sales directors at 51-500 employee companies in France.

5. **Tune a signal and check the bill**
   > Why is my fundraising signal so quiet? Show me its funnel, relax the filter that removes the most, and tell me how many credits I have left and what I spent this week.

More in the API docs: <https://api.rodz.io/docs>.
