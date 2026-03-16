# SDC Application Auto-Grader

Automatically grades SDC consulting club applications using Claude AI.
Emails with PDF attachments sent to `skku.sdc.recruiting@gmail.com` are graded 0-100 and logged to Google Sheets.

## Architecture

```
Gmail (new email with PDF)
  → Google Apps Script trigger (every 15 min)
  → PDF text extraction (Drive API → Google Doc conversion)
  → Claude API (Haiku) → structured JSON score
  → Google Sheets row appended (color-coded by result)
```

Runs entirely in Google's cloud. No local server needed. Works 24/7.

## Grading Rubric

| Section | Points | What Claude evaluates |
|---------|--------|-----------------------|
| Q4 Business Case | 35 | Structured thinking, MECE, strategy quality |
| Q1 Motivation | 20 | Fit, clarity, specificity |
| Q3 Strengths | 20 | Concreteness, consulting relevance |
| Q2 Collaboration | 15 | Role clarity, learning articulated |
| Activities | 10 | Relevance, leadership, diversity |
| **Total** | **100** | |

Availability flag: auto-flagged if Wed 6-8pm session unavailable.

Recommendations: **Strong Pass** / **Pass** / **Borderline** / **Reject** (color-coded in sheet).

## Setup (one-time, ~15 minutes)

### Step 1 — Create the Google Sheet

1. Go to [sheets.google.com](https://sheets.google.com) → New spreadsheet
2. Name it `SDC Applications 2026`
3. Copy the spreadsheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/`**THIS_PART**`/edit`
4. Rename the first tab to `Applications`

### Step 2 — Create the Apps Script

1. Go to [script.google.com](https://script.google.com) → New project
2. Name it `SDC Grader`
3. Delete the default `myFunction` code
4. Paste the full contents of `grader.gs`
5. Save (Ctrl+S)

### Step 3 — Enable Drive API

1. In the Apps Script editor → left sidebar → **Services** (+)
2. Find **Google Drive API** → Add
3. Also enable **Gmail API** if not already listed

### Step 4 — Set API keys

1. Left sidebar → **Project Settings** (gear icon)
2. Scroll to **Script Properties** → **Add script property**
3. Add two properties:
   - Key: `CLAUDE_API_KEY` → Value: your Anthropic API key (from [console.anthropic.com](https://console.anthropic.com))
   - Key: `SHEET_ID` → Value: the spreadsheet ID from Step 1

### Step 5 — Install the trigger

1. In the editor, select function `setupTrigger` from the dropdown
2. Click **Run**
3. Grant all permissions when prompted (Gmail, Sheets, Drive)
4. Trigger is now installed — runs every 15 minutes

### Step 6 — Test it

1. Send a test email to `skku.sdc.recruiting@gmail.com` with the SDC PDF attached
2. Wait up to 15 minutes, or manually run `processNewApplications` from the editor
3. Check your Google Sheet — a new row should appear with scores

## Output Columns

| Column | Description |
|--------|-------------|
| Timestamp | When the email was received |
| Name | Extracted from 성명 field |
| Sender Email | Applicant's email |
| Major | 전공/복수전공 |
| Total Score | 0–100 |
| Q1–Q4, Activities | Section scores |
| Recommendation | Strong Pass / Pass / Borderline / Reject |
| Strengths | 2-3 key positives |
| Weaknesses | 2-3 areas to probe in interview |
| Availability Flag | ⚠️ FLAG if Wed session unavailable |
| Summary | 2-sentence applicant summary |

## Cost

- Claude Haiku: ~$0.001 per application (essentially free)
- Google Apps Script: free tier is sufficient (6 min/day execution limit, well within budget)

## Notes

- The script labels processed emails as `SDC-Applications` to avoid double-grading
- PDF text extraction works via Drive API's PDF→Google Doc conversion — no OCR library needed
- If an applicant submits twice, both will be graded (filter by name in sheet)
- Grading is AI-assisted, not final — use scores to triage, not to auto-reject
