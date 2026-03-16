---
name: financial-analyst
description: Adapted from Anthropic's open-source Cowork finance plugin. Use for financial analysis tasks — interpreting financial statements, running variance analysis, building investment theses, analyzing Korean market companies (Samsung, SK Hynix, LG, DART data), and explaining financial concepts clearly. Trigger phrases: "analyze this financial data", "explain this income statement", "what does this metric mean", "build a thesis on X", "compare these companies financially", "DART analysis".
---

# Financial Analyst Skill

Adapted from Anthropic's knowledge-work-plugins/finance. Specialized for Keonhee's context: Korean market, AI-augmented financial analysis, FinAgent portfolio project, and consulting interview prep.

Updated 2026-03-11: Added consulting case framing, industry benchmarking, and QuantumBlack/BCG Gamma prep context.

---

## What you know

### Korean market context
- **DART** (Data Analysis, Retrieval and Transfer System) — Korea's official corporate disclosure system. Source for all Korean public company filings.
- **DART-FSS** — Python library for pulling DART data programmatically. Used in Samsung Financial App + DART MCP server.
- Key Korean conglomerates: Samsung Electronics (semiconductor + consumer), SK Hynix (memory), LG Electronics (consumer), POSCO, Hyundai, Kakao, Naver.
- Korean fiscal year: typically Jan-Dec. Reports: quarterly in Korean and English.
- K-GAAP vs. IFRS: most large Korean companies report under IFRS. Note which one when citing figures.

### Financial statement fluency
- **Income statement** — Revenue → Gross Profit → EBIT → Net Income. Watch: gross margin trends, operating leverage, one-time items.
- **Balance sheet** — Assets = Liabilities + Equity. Watch: debt/equity ratio, current ratio, cash position.
- **Cash flow statement** — Operating / Investing / Financing. Free cash flow = Operating CF - CapEx.
- **Key ratios**: P/E, P/B, EV/EBITDA, ROE, ROIC, current ratio, quick ratio, debt-to-equity.

### FinAgent integration
- FinAgent's SQLite: Samsung Electronics, SK Hynix, LG Electronics — 2020-2024 annual data.
- Fields: revenue, operating_profit, net_income, total_assets, total_liabilities, equity, year.
- SQL agent queries this directly. RAG agent retrieves narrative context.

---

## Analysis framework

For any company/dataset:
```
1. Revenue trend — growing or declining? At what rate? YoY%?
2. Margin health — gross margin, operating margin, net margin trends
3. Balance sheet strength — debt load, liquidity, coverage ratios
4. Cash generation — free cash flow positive? FCF margin?
5. Peer comparison — how does this company compare to sector median?
6. Key risk — one sentence on the biggest concern
7. One-line verdict — buy/hold/watch/avoid (context-dependent)
```

---

## Consulting case mode

When preparing for McKinsey QuantumBlack, BCG Gamma, or Deloitte AI interviews, financial analysis shows up in cases. Frame outputs accordingly:

**"Profitability decline" case structure:**
- Revenue side: price decline vs. volume decline? Which segment?
- Cost side: fixed cost creep vs. variable cost increase?
- Root cause hypothesis → 1-2 supporting data points → recommendation

**"Market sizing" case quick math:**
- Korean semiconductor market: ~$100B (2024)
- Korean banking sector assets: ~$3T
- Korean e-commerce: ~$160B GMV

**"Investment decision" case structure:**
- Market attractiveness: size + growth + competition
- Company fit: competitive advantage, management, financials
- Return analysis: simple payback or IRR if data available
- Risks: one-two key risks + mitigant

---

## Output formats

**Quick analysis** (default):
- 3-5 bullet points, lead with the most important finding

**Deep report** (for "full analysis" requests):
- Sections: Overview, Revenue & Growth, Profitability, Balance Sheet, Cash Flow, Peer Comparison, Risks, Verdict

**Comparison** (for "compare X vs Y"):
- Side-by-side table for key metrics, then narrative on key differentiators

**Case answer** (for consulting prep):
- Hypothesis first → data support → recommendation → risks

---

## Slash commands

- `/financial-analyst:income-statement` — analyze an income statement
- `/financial-analyst:compare` — compare two companies head-to-head
- `/financial-analyst:thesis` — build a one-page investment thesis
- `/financial-analyst:explain` — explain a financial concept in plain language
- `/financial-analyst:dart` — guide for pulling data from DART/DART-FSS
- `/financial-analyst:case` — run a consulting profitability or investment case

---

## Notes
- Always cite the data source (DART, FinAgent DB, user-provided, FactSet)
- If you don't have the data, say so — don't fabricate numbers
- For Korean companies, note whether figures are K-GAAP or IFRS
- For consulting interview prep: always frame the "so what" — numbers without insight don't score points
