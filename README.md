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

## Ticket groups (v5.5)

The **📌 Ticket groups** tab follows specific Jira tickets day by day.

- **＋ New group** → bulk-paste ticket keys (Excel column, Jira links, email text — keys are extracted automatically). **✎ Edit / add tickets** adds, replaces or removes keys.
- **↻ Refresh all groups** reads the current status from Jira (or from loaded / imported tickets) and stores a **daily snapshot** in this browser (45 days). *Auto-refresh daily* runs it the first time you open the tab each day.
- **Compare with** an earlier snapshot shows status moves, newly resolved tickets, assignee / priority / due-date changes and a status trail.
- **★ Close watch** pins a ticket. **Attention** flags: reopened / rejected, blocked / on hold, overdue, highest priority, no update for N days.
- Views: by group, by account, by status. **Copy daily update** produces a text summary for Teams / email; table, keys, JQL and Excel exports are also available.
- From **🔎 Ticket search**, *Add shown tickets to group…* moves search results into a group.

Groups live in the browser. **🔐 Save groups to private config** writes them into your private config as `ticketGroups` and downloads it — load that file on another PC to get the same groups. Format:

```json
"ticketGroups": [
  { "name": "Group 1", "color": "#2563eb", "note": "why I follow these",
    "tickets": ["DQ-101", "DQ-102"], "closeWatch": ["DQ-102"], "notes": { "DQ-101": "waiting for client" } }
]
```

## Updating the site from a local folder

1. One-time: install Git, `git clone https://github.com/<user>/retailerhealthcheck.git`, sign in on the first `git push` (browser sign-in or a fine-grained token with *Contents: Read and write*).
2. Each iteration: replace the changed files in the folder → run `publish.bat` (or `git add -A && git commit -m "msg" && git push`).
3. Keep `config.private.json` **outside** the repo folder. `.gitignore` and `publish.bat` both block private files.

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
  "tracker": { "vendorOwnerHeader": "Vendor Owner", "clientOwnerHeader": "Client Owner" },  // tracker column headers
  "ticketGroups": [ { "name": "Group 1", "tickets": ["DEMO-101"], "closeWatch": [] } ]  // optional, see Ticket groups
}
```
