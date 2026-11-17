# Retailer Data Health Monitor

Browser-only tool that flags week-over-week score drops per retailer × module, links Critical rows to open Jira blockers, and reconciles an issue-tracker workbook against Jira.

**Everything runs in the browser.** Uploaded reports, the tracker, Jira tickets and your token never leave your machine (Jira calls go from your browser → your Jira, optionally through a local proxy).

## What is (and isn't) in this repo

| In the repo (public) | Kept private (not in the repo) |
|---|---|
| `index.html` – the app, no client data | `config.json` – account registry, business units, Jira URL / JQL, dashboard link |
| `config.example.json` – demo config with fake accounts | Jira Personal Access Token (stored in your browser only) |
| `tools/jira_proxy.py` – local CORS proxy | `tools/jira_host.local.txt` – your Jira host (created on first proxy run) |

`.gitignore` already blocks `config.json`, `*.private.json`, `*.xlsx`, `*.csv` and the proxy host file.

## Deploy to GitHub Pages

1. Create a new repository on GitHub (e.g. `retailer-health-monitor`).
2. Upload **the contents of this folder** (not the folder itself) so `index.html` is at the repo root. Include the hidden files `.gitignore` and `.nojekyll`.
3. Repo → **Settings → Pages** → *Build and deployment* → Source: **Deploy from a branch** → Branch: `main` / `(root)` → **Save**.
4. After ~1 minute the site is live at `https://<your-user>.github.io/<repo-name>/`.

> On a free account, GitHub Pages sites are public even if the repo is private. That's fine here because the site contains no client data, but check your company's policy on hosting internal tools.

## First use

1. Open the site → **⚙ Workspace config** → drop your private `config.json`. It is saved in this browser only (use *Remove* on shared PCs).
   - No config yet? Copy `config.example.json`, fill in your accounts, and save it **outside** the repo.
2. Upload the weekly report files (filename must contain a business-unit keyword from your config).
3. *(Optional)* **Connect Jira** → Base URL, Personal Access Token (Bearer), JQL or a pasted filter URL.

## Jira from GitHub Pages (CORS)

Most corporate Jira servers block calls from other websites. Run the local proxy:

```bash
cd tools
python jira_proxy.py --origin https://<your-user>.github.io
# Windows: double-click start_jira_proxy.bat
```

The first run asks for your Jira host and saves it to `tools/jira_host.local.txt` (git-ignored). In the site set **CORS proxy prefix** to `http://127.0.0.1:8787/?url=`.

| Message | Fix |
|---|---|
| `CERTIFICATE_VERIFY_FAILED` | start with `--insecure` (company SSL inspection) |
| Proxy not reachable | proxy window closed, or wrong port |
| "Jira returned a web page" / 401 | token not accepted — create a PAT in Jira → Profile → Personal Access Tokens, use Bearer |

No proxy allowed? Use **Import Jira export** (Jira issue search → Export → CSV, all fields).

## Config format

```jsonc
{
  "workspaceName": "Retailer Data Health Monitor",
  "clientLabel": "client",                       // shown in "… with <label> account"
  "businessUnits": [ { "name": "Unit A", "match": "unit[-_ ]?a" } ],  // match = regex on the report filename
  "accounts": [
    { "n": "Display name", "i": "AU", "b": "Unit A", "l": "", "a": "9001", "d": "1001" }
    // i = ISO code (UK, not GB) · b = business unit · l = optional language (dutch/french)
    // d = primary account ID (matched to the Jira Account field) · a = alternate ID
  ],
  "jira":   { "baseUrl": "https://jira.example.com", "defaultJql": "project = DEMO AND statusCategory != Done" },
  "links":  { "issueTrackerDashboard": "" },     // optional "Open Customer Issue Tracker" button
  "tracker": { "vendorOwnerHeader": "Vendor Owner", "clientOwnerHeader": "Client Owner" }  // tracker column headers
}
```
