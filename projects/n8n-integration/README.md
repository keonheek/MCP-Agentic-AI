# n8n Integration

## Prerequisites

**Node.js is required** before any setup step below will work.

- `npx` (bundled with Node.js) is used to run the MCP server
- If `node --version` returns "command not found", install Node.js first: `references/sops/nodejs-setup.md`

---

## What this is

n8n is a self-hostable workflow automation platform (like Zapier but open-source and local). With Claude Code's n8n MCP, Claude can directly build, fix, and trigger n8n workflows via natural language.

Nate Herk's workflow: "I Will Never Fix Another n8n Workflow" — Claude auto-generates the JSON, deploys it, and fixes errors without you touching the n8n UI.

## Status

**Not yet installed.** Setup steps below.

---

## Setup steps

### 1. Install n8n (local, Docker recommended)

```bash
# Option A: npx (no install needed)
npx n8n

# Option B: Docker (recommended for stability)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

Access at: http://localhost:5678

### 2. Install n8n MCP server

```bash
npm install -g @n8n/mcp-server
```

Or check: https://github.com/n8n-io/n8n-mcp

### 3. Add to Claude Code global MCP settings

In Claude Code VS Code extension → Settings → MCP Servers, add:

```json
{
  "mcpServers": {
    "n8n": {
      "command": "npx",
      "args": ["-y", "@n8n/mcp-server"],
      "env": {
        "N8N_URL": "http://localhost:5678",
        "N8N_API_KEY": "get-from-n8n-settings"
      }
    }
  }
}
```

Get API key: n8n UI → Settings → API → Create API Key

### 4. Verify connection

Say to Claude: "list my n8n workflows" — should return existing workflows.

---

## Planned workflows

| Workflow | Trigger | Action |
|----------|---------|--------|
| Job application tracker | Manual | Create Notion entry + save to log |
| Weekly AI news digest | Monday 8am | Perplexity search → Notion page |
| GitHub PR summary | PR merged | Summarize changes → Notion |
| FinAgent alert | Daily | Check if Streamlit app is live → Slack/email if down |

---

## How to use once connected

```
"Build me an n8n workflow that does X"
"Fix the error in my n8n workflow for Y"
"Trigger the job-tracker workflow with these inputs"
```

Claude handles the JSON generation, error fixing, and deployment. You just describe what you want.

---

## Resources

- n8n docs: https://docs.n8n.io
- n8n MCP: https://github.com/n8n-io/n8n-mcp
- Nate Herk's tutorial: search "Nate Herk n8n Claude Code" on YouTube
