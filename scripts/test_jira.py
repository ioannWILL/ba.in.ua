#!/usr/bin/env python3
"""Quick JIRA connectivity test — run this locally before deploying."""

import os, sys, json, requests
from requests.auth import HTTPBasicAuth

JIRA_BASE_URL   = os.environ.get("JIRA_BASE_URL",   "https://businessanalysislearning.atlassian.net")
JIRA_EMAIL      = os.environ.get("JIRA_EMAIL",      "vilchdeveloper@gmail.com")
JIRA_API_TOKEN  = os.environ.get("JIRA_API_TOKEN",  "")
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "BIU")
JIRA_TRIGGER_STATUS = os.environ.get("JIRA_TRIGGER_STATUS", "To Review")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

# ── 1. Check a specific issue ──────────────────────────────────────────────────
issue_key = sys.argv[1] if len(sys.argv) > 1 else "BIU-208"
print(f"\n── Issue {issue_key} ──")
r = requests.get(
    f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}",
    params={"fields": "summary,status,assignee,attachment,description"},
    auth=auth, headers=headers,
)
r.raise_for_status()
d = r.json()["fields"]
print(f"  Summary  : {d.get('summary')}")
print(f"  Status   : {d['status']['name']}")
assignee = d.get("assignee") or {}
print(f"  Assignee : {assignee.get('displayName', '(none)')}")
atts = d.get("attachment", [])
print(f"  Attachments ({len(atts)}):")
for a in atts:
    print(f"    - {a['filename']}  [{a['mimeType']}]  {a['size']} bytes")

# ── 2. JQL query used by the daily workflow ────────────────────────────────────
print(f"\n── Issues in '{JIRA_TRIGGER_STATUS}' ──")
jql = f'project = "{JIRA_PROJECT_KEY}" AND status = "{JIRA_TRIGGER_STATUS}" ORDER BY updated ASC'
r2 = requests.get(
    f"{JIRA_BASE_URL}/rest/api/3/search",
    params={"jql": jql, "maxResults": 10, "fields": "summary,status,assignee"},
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
