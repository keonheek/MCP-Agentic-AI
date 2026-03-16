# GitHub MCP Setup

## What it unlocks

Once connected, Claude Code can:
- Create and list pull requests
- Create and list issues
- Search repositories
- Get file contents from any repo
- Create branches

---

## Prerequisites

- Node.js must be installed — follow `references/sops/nodejs-setup.md` first
- A GitHub Personal Access Token (PAT)

---

## Step 1 — Create a GitHub PAT

1. Go to: https://github.com/settings/tokens
   (Or navigate: github.com → Settings → Developer Settings → Personal access tokens → Fine-grained tokens)

2. Click "Generate new token"

3. Set:
   - **Token name:** Claude Code MCP (or anything descriptive)
   - **Expiration:** 90 days or No expiration (your call)
   - **Repository access:** All repositories, or specific ones

4. Under "Repository permissions", enable:
   - `Contents` — Read and write
   - `Issues` — Read and write
   - `Pull requests` — Read and write
   - `Metadata` — Read-only (required, auto-selected)

5. Click "Generate token" — copy it immediately, it won't show again

6. Save the token in `.env` under the key `GITHUB_PERSONAL_ACCESS_TOKEN`

---

## Step 2 — Test the server (optional)

In PowerShell:

```powershell
npx -y @modelcontextprotocol/server-github
```

Should print a startup message. Ctrl+C to exit.

---

## Step 3 — Add to `.mcp.json`

In your Claude Code `.mcp.json` (project-level or global), add the following inside `mcpServers`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-pat-here"
      }
    }
  }
}
```

Replace `"your-pat-here"` with the token you generated.

---

## Step 4 — Verify connection

Restart Claude Code, then say:

"List my GitHub repos"

Should return a list of your repositories. If it does, the MCP is live.

---

## Notes

- Never commit your PAT to git — keep it in `.env` or directly in `.mcp.json` (which should be gitignored if it contains secrets)
- If the token expires, regenerate and update `.mcp.json`
