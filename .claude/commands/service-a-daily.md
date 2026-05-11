---
description: Orchestrate the full Service A lead-gen daily pipeline including in-session DM draft generation
---

# /service-a-daily

Run the full Service A lead-gen pipeline for today. Execute each step in order.

## Step 1: Run pure data scripts

Run these Python scripts sequentially. Use the shell (Bash tool or subprocess). Each is in `agents/service_a_leadgen/`:

```
cd agents/service_a_leadgen
python a1_meta_ad_scanner.py
python a2_response_time_tester.py
python a3_platform_detector.py
python a4_decision_maker_finder.py
python a5_dm_draft_writer.py
```

If any script fails, log the error and continue to the next step. Do not abort.

## Step 2: Generate DM drafts in-session

Read `agents/service_a_leadgen/data/pending_drafts.json`.

For each prospect in the list, generate a Korean IG DM draft using this structure (3 sentences max):

**Sentence 1:** Specific observation referencing their recent ad or platform.
- If `running_ads` = "Y": reference their active Meta ad
- If `platform` is Cafe24 or Imweb: reference their e-commerce setup

**Sentence 2:** Specific problem (response time or platform friction).
- If `response_time` is a number > 2: mention the approximate response delay
- If `platform` in Cafe24/Imweb: mention lead response automation opportunity

**Sentence 3:** Soft ask. Use: "혹시 관련 데모 짧게 보내드려도 될까요?" or "혹시 짧게 통화 가능하실까요?"

Tone rules:
- Casual but professional. Like a peer, not a salesperson.
- No em dashes. No excessive emojis. No aggressive sales language.
- Korean only (this is for Korean skincare D2C brands)
- Under 3 sentences total

## Step 3: Write DM drafts back to Google Sheet

For each prospect with a generated draft, call `sheet_utils.update_row_fields(row_sheet_index, {"dm_draft": <draft_text>})`.

Do this by running a small Python helper script. Write the updates as a JSON file to `agents/service_a_leadgen/data/dm_drafts_written.json` (brand: draft pairs) for confirmation.

Alternatively, run a quick Python snippet in the shell:
```python
import sys, json
sys.path.insert(0, 'agents/service_a_leadgen')
import sheet_utils
drafts = json.load(open('agents/service_a_leadgen/data/pending_drafts.json'))
# ... iterate and update
```

## Step 4: Run A6 digest

```
python agents/service_a_leadgen/a6_telegram_digest.py
```

This sends the top 5 scored prospects to Telegram.

## Completion

Report:
- How many prospects were scored
- How many DM drafts were generated
- Whether Telegram digest was sent successfully
- Any errors per step
