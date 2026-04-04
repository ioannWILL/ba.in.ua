# ba.in.ua — JIRA → WordPress translation workflow

Automated daily workflow that picks up translated articles from JIRA and publishes them as WordPress drafts.

## What it does

1. Checks JIRA for issues with status **To Review**
2. Downloads the `.docx` translation attachment
3. Extracts the Ukrainian title and article body
4. Finds the attached image; if multiple images, matches the original article's main image
5. Generates 3–4 English + 3–4 Ukrainian tags via Claude
6. Creates a **WordPress draft post** with title, body, featured image, tags, and attribution footer
7. Adds a comment on the JIRA issue with the WordPress draft link
8. Transitions the JIRA issue to **In Review**
9. Sends an email notification to `vilchdeveloper@gmail.com`

---

## Setup

### 1. JIRA

- Create an API token at <https://id.atlassian.com/manage-profile/security/api-tokens>
- Find your **"Translated by" custom field ID**:
  ```
  GET https://yourteam.atlassian.net/rest/api/3/field
  ```
  Search the response for your field name and note its `id` (e.g. `customfield_10100`).

### 2. WordPress

- Enable the REST API (on by default in WP 5+)
- Create an **Application Password**: WP Admin → Users → Your Profile → Application Passwords

### 3. Anthropic API key

- Get one at <https://console.anthropic.com>

### 4. Gmail App Password

- Enable 2-Step Verification on your Google account
- Go to **Google Account → Security → App passwords**, create one for "Mail"

### 5. GitHub Actions secrets & variables

Go to **Settings → Secrets and variables → Actions** in this repo.

**Secrets** (sensitive values):

| Secret | Value |
|---|---|
| `JIRA_BASE_URL` | `https://yourteam.atlassian.net` |
| `JIRA_EMAIL` | Your Atlassian account email |
| `JIRA_API_TOKEN` | JIRA API token |
| `JIRA_PROJECT_KEY` | e.g. `TRANS` |
| `WP_BASE_URL` | `https://ba.in.ua` |
| `WP_USERNAME` | WordPress username |
| `WP_APP_PASSWORD` | WordPress application password |
| `ANTHROPIC_API_KEY` | Claude API key |
| `SMTP_USER` | Gmail address |
| `SMTP_PASSWORD` | Gmail app password |

**Variables** (non-sensitive, can be plain text):

| Variable | Default | Notes |
|---|---|---|
| `JIRA_TRIGGER_STATUS` | `To Review` | Status that triggers the workflow |
| `JIRA_NEXT_STATUS` | `In Review` | Status to move issue to after processing |
| `JIRA_TRANSLATOR_FIELD` | *(empty)* | Custom field ID for "Translated by" |
| `JIRA_ORIGINAL_URL_FIELD` | *(empty)* | Custom field ID for original article URL (optional — auto-detected from description if empty) |
| `NOTIFY_EMAIL` | `vilchdeveloper@gmail.com` | Notification recipient |

### 6. Local testing

```bash
cp .env.example .env
# Fill in .env with your real values

pip install -r requirements.txt
python scripts/sync.py
```

---

## Schedule

The workflow runs daily at **08:00 UTC (11:00 Kyiv time)** via GitHub Actions.  
You can also trigger it manually from the **Actions** tab → **JIRA → WordPress translation sync** → **Run workflow**.

---

## Article structure expected in .docx

- **First Heading 1** (or first paragraph if no Heading 1) → WordPress post title
- **Remaining paragraphs/headings** → WordPress post body
- Formatting preserved: bold, italic, underline, heading levels

## Attribution footer added automatically

> Оригінальна стаття — [Original Title](original_url), переклад — Translator Name, ревью — [Іван Вільчавський](https://www.linkedin.com/in/ivan-vilchavskyi). Зображення з оригінальної статті.
