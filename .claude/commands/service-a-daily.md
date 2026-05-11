---
description: Daily Service A lead-gen pipeline, email digest via Gmail MCP
---

# /service-a-daily

Execute the full Service A lead-gen pipeline for Korean skincare D2C prospects:

1. Run `python agents/service_a_leadgen/a1_meta_ad_scanner.py` to find new brands running Meta ads
2. Run `python agents/service_a_leadgen/a2_response_time_tester.py` to estimate response time (read-only mode)
3. Run `python agents/service_a_leadgen/a3_platform_detector.py` to detect e-commerce platform
4. Run `python agents/service_a_leadgen/a4_decision_maker_finder.py` to find CMO / 마케팅 팀장 / 대표
5. A5: For each prospect with score >= 70, generate Korean IG DM draft in-session. Use the brand context (name, platform, response time, recent ad) to write a 3-sentence DM that mentions one specific signal. NO em dashes. Peer-to-peer tone, not salesy.
6. A6: Pick top 5 prospects by score with status="New". Mark them "Ready to DM" in the Sheet.

Sheet ID: `1w8X2uzo0ARrspp00Tpz8CL3LCXOF4RXIMp_tCemTqSI`. Write back via available means (gws CLI may not be installed in cloud; if not, skip Sheet write and include data inline in email).

After pipeline:

Send via Gmail MCP:
- To: `keonhee3337@gmail.com`
- Subject: `[Service A Daily] YYYY-MM-DD - Top 5 Skincare D2C Prospects`
- Body: per-prospect block (brand, IG handle, score, signal one-liner, platform, decision maker, full Korean DM draft ready to copy-paste) + link to Sheet at the end

If Gmail MCP unavailable, print to session output as fallback.
