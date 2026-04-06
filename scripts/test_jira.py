#!/usr/bin/env python3
"""Quick JIRA connectivity test — run this locally before deploying."""

import os, sys, json, requests
from requests.auth import HTTPBasicAuth

JIRA_BASE_URL        = os.environ.get("JIRA_BASE_URL",   "https://businessanalysislearning.atlassian.net")
JIRA_EMAIL           = os.environ.get("JIRA_EMAIL",      "vilchdeveloper@gmail.com")
JIRA_API_TOKEN       = os.environ.get("JIRA_API_TOKEN",  "")
JIRA_PROJECT_KEY     = os.environ.get("JIRA_PROJECT_KEY", "BIU")
JIRA_TRIGGER_STATUS  = os.environ.get("JIRA_TRIGGER_STATUS", "TO REVIEW")

auth    = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

# ── 1. Fetch field name map ────────────────────────────────────────────────────
print("\n── Fetching field definitions ──")
rf = requests.get(f"{JIRA_BASE_URL}/rest/api/3/field", auth=auth, headers=headers)
rf.raise_for_status()
field_names = {f["id"]: f["name"] for f in rf.json()}
custom_fields = {f["id"]: f["name"] for f in rf.json() if f.get("custom")}
print(f"  Total fields: {len(field_names)}  Custom fields: {len(custom_fields)}")
for fid, fname in sorted(custom_fields.items()):
    print(f"  {fid}  →  {fname}")

# ── 2. Fetch issue with all fields ────────────────────────────────────────────
issue_key = sys.argv[1] if len(sys.argv) > 1 else "BIU-210"
print(f"\n── Issue {issue_key} (all non-null custom fields) ──")
r = requests.get(
    f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}",
    params={"fields": "*all"},
    auth=auth, headers=headers,
)
r.raise_for_status()
fields = r.json().get("fields", {})
print(f"  Summary  : {fields.get('summary')}")
print(f"  Status   : {fields['status']['name']}")
print(f"  Assignee : {(fields.get('assignee') or {}).get('displayName', '(none)')}")
atts = fields.get("attachment", [])
print(f"  Attachments ({len(atts)}):")
for a in atts:
    print(f"    - {a['filename']}  [{a['mimeType']}]")

print(f"\n  Custom fields with values:")
for key, val in sorted(fields.items()):
    if key.startswith("customfield_") and val is not None:
        name = field_names.get(key, "(unknown)")
        print(f"  {key}  [{name}]  =  {json.dumps(val)[:150]}")

# ── 3. JQL query ──────────────────────────────────────────────────────────────
print(f"\n── Issues in '{JIRA_TRIGGER_STATUS}' ──")
jql = f'project = "{JIRA_PROJECT_KEY}" AND status = "{JIRA_TRIGGER_STATUS}" ORDER BY updated ASC'
r2 = requests.post(
    f"{JIRA_BASE_URL}/rest/api/3/search/jql",
    json={"jql": jql, "maxResults": 10, "fields": ["summary", "status", "assignee"]},
    auth=auth, headers=headers,
)
r2.raise_for_status()
issues = r2.json().get("issues", [])
print(f"  Found {len(issues)} issue(s):")
for i in issues:
    f = i["fields"]
    assignee = (f.get("assignee") or {}).get("displayName", "(none)")
    print(f"  - {i['key']}: {f['summary']}  [{f['status']['name']}]  assignee: {assignee}")

print("\nDone.")
