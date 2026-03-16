# Node.js Setup — Windows 10

## Why this matters

Node.js is required for:
- GitHub MCP server (`@modelcontextprotocol/server-github`)
- n8n MCP server (`@n8n/mcp-server`)
- Any tool that runs via `npx` or `npm`

Without it, both GitHub MCP and n8n integration are blocked.

---

## Installation steps

### 1. Download Node.js

Go to: https://nodejs.org

Download the **LTS version** (long-term support — more stable than Current).

File will be something like: `node-v20.x.x-x64.msi`

### 2. Run the installer

- Double-click the `.msi` file
- Accept defaults throughout — no custom configuration needed
- The installer adds Node.js and npm to your system PATH automatically

### 3. Restart your terminal

Close PowerShell (or VS Code terminal) completely and reopen it.

This is required — the PATH update does not apply to already-open terminals.

### 4. Verify the install

In a new PowerShell window:

```powershell
node --version
npm --version
```

Expected output (version numbers will vary):
```
v20.11.0
10.2.4
```

If you see version numbers, the install is complete.

---

## What's unlocked after install

- `npx` is available — required to run MCP servers without a global install
- GitHub MCP — follow `references/sops/github-mcp-setup.md`
- n8n MCP — follow `projects/n8n-integration/README.md`

---

## Troubleshooting

**`node: command not found` after install**
- Make sure you fully closed and reopened the terminal
- If still not working: search "Environment Variables" in Windows → Edit system PATH → confirm `C:\Program Files\nodejs\` is listed

**Installer asks about "native modules" / build tools**
- Optional — skip unless you hit errors later
