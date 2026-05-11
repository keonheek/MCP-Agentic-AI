# Cron Routine Setup

Run these slash commands in a Claude Code session to register the 3 automated routines.
Check CronList first to avoid duplicates.

## M1 Morning Brief (daily 6:30am KST = 21:30 UTC)

```
/schedule
```

When prompted, set up a custom schedule with:
- Cron: `30 21 * * *`
- Prompt: "Run the M1 morning brief. First execute: `python agents/m1_orientation/m1.py` to collect fresh data. Then run `/m1-brief` to synthesize and post to Discord."

## M2 Blindspot Scanner (Sundays 10pm KST = 13:00 UTC Sunday)

```
/schedule
```

When prompted, set up a custom schedule with:
- Cron: `0 13 * * 0`
- Prompt: "Run the M2 blindspot scan. First execute: `python agents/m2_blindspot/m2.py` to collect fresh data. Then run `/m2-blindspot` to synthesize, create Google Doc, and post to Discord."

## Service A Daily Pipeline (daily 5am KST = 20:00 UTC)

```
/schedule
```

When prompted, set up a custom schedule with:
- Cron: `0 20 * * *`
- Prompt: "Run /service-a-daily to execute the full Service A lead-gen pipeline: A1 through A6, with in-session DM draft generation."

## Notes

- Cron jobs only fire while Claude Code (VS Code) is open and idle.
- Jobs expire after 7 days. Run /schedule again to renew.
- LLM eval (/llm-eval-judge) is on-demand only. No cron needed.
