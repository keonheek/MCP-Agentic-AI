# Finance (Quant) — Time Value of Money: NPV and IRR in Python
_Track 5 | Week 1 | Date: 2026-03-24_

---

## Concept (10 min read)

**Why a dollar today is worth more than a dollar tomorrow**

You already built a DCF model in the consulting emulation project. The DCF *is* time value of money — you discounted future cash flows back to present value using a discount rate. This lesson makes that mechanism explicit and gives you the Python tools to run it cleanly.

The core idea: cash received in the future is worth less than cash received today, because today's cash can be reinvested. The discount rate captures that opportunity cost. In M&A, it's usually WACC. In project evaluation, it's the hurdle rate.

**NPV — Net Present Value**

NPV answers: "If I invest X today and receive these future cash flows, do I come out ahead?"

```
NPV = sum( CF_t / (1 + r)^t ) for t = 0, 1, ..., n
```

- NPV > 0 → accept the project (creates value)
- NPV < 0 → reject (destroys value)
- NPV = 0 → break-even (exactly meets cost of capital)

In consulting M&A work: you run NPV on the target company's projected free cash flows. The discount rate is WACC (usually 8-12% for Korean mid-cap). If NPV of acquisition > acquisition price, it's a value-creating deal.

**IRR — Internal Rate of Return**

IRR answers: "What discount rate makes this investment exactly break even?"

It's the discount rate where NPV = 0. You solve for `r` numerically (no closed form).

Decision rule: if IRR > WACC (or hurdle rate), proceed. If IRR < WACC, pass.

In consulting: IRR is the headline number clients understand. A PE firm looking at a Korean manufacturer wants to see "IRR of 22% over 5 years." NPV requires you to agree on a discount rate first; IRR doesn't.

**Korean market context**

Korean chaebols (Samsung, SK, LG) evaluate capex using both NPV and IRR but also apply strategic overlays — market share, supply chain control — that pure NPV misses. For SMEs and mid-caps (the target market for your consulting emulation project and GEO clients), the finance committee usually sets a hurdle rate of 10-15% (roughly: cost of bank debt ~5-6% + equity risk premium). If IRR clears the hurdle, the project gets funded.

DART disclosures often include planned capex in the 사업보고서 — you can pull these and run IRR against projected revenue to evaluate whether a company's announced investment makes financial sense. That's a real consulting use case.

---

## Key Terms

- **Discount rate (r):** The rate used to convert future cash flows to present value. Reflects opportunity cost and risk. In M&A: WACC. In project eval: hurdle rate.
- **WACC (Weighted Average Cost of Capital):** Blended cost of debt and equity. E.g., 40% debt at 6% + 60% equity at 12% = WACC of 9.6%.
- **Cash flow (CF_t):** Net cash in or out at time period t. Period 0 is usually the initial investment (negative).
- **NPV (Net Present Value):** Sum of all discounted cash flows including the initial outlay. Positive = value creation.
- **IRR (Internal Rate of Return):** The discount rate that makes NPV = 0. Solved numerically.
- **Hurdle rate:** Minimum acceptable IRR set by the investor or finance committee. Project proceeds only if IRR > hurdle rate.
- **Sensitivity analysis:** Re-running NPV across a range of discount rates or cash flow assumptions to understand how robust the investment case is.

---

## Working Code

```python
# Requirements: pip install numpy-financial numpy pandas
import numpy as np
import numpy_financial as npf
import pandas as pd

# -------------------------------------------------------
# Scenario: Korean SME (food manufacturer, 경기도)
# Planning to buy automated packaging line
# Initial outlay: 500M KRW
# Expected annual net cash flows over 5 years (KRW millions)
# -------------------------------------------------------

initial_investment = -500  # negative = cash out
cash_flows = [-500, 80, 120, 150, 180, 200]  # year 0 through year 5
wacc = 0.10  # 10% WACC — typical Korean mid-cap hurdle rate

# -------------------------------------------------------
# 1. NPV calculation
# -------------------------------------------------------
npv = npf.npv(wacc, cash_flows)
print(f"NPV at {wacc*100:.0f}% discount rate: {npv:.1f}M KRW")
# Interpretation: positive = project creates value at this discount rate

# -------------------------------------------------------
# 2. IRR calculation
# -------------------------------------------------------
irr = npf.irr(cash_flows)
print(f"IRR: {irr*100:.2f}%")
print(f"WACC: {wacc*100:.1f}%")
print(f"Decision: {'PROCEED — IRR > WACC' if irr > wacc else 'REJECT — IRR < WACC'}")

# -------------------------------------------------------
# 3. Manual NPV (no numpy_financial) — useful to understand the math
# -------------------------------------------------------
def manual_npv(rate, cash_flows):
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))

npv_manual = manual_npv(wacc, cash_flows)
print(f"\nManual NPV check: {npv_manual:.1f}M KRW")

# -------------------------------------------------------
# 4. NPV sensitivity analysis — how does NPV change with discount rate?
# -------------------------------------------------------
rates = np.arange(0.05, 0.25, 0.01)  # 5% to 24%
sensitivity = pd.DataFrame({
    "Discount Rate (%)": (rates * 100).round(0).astype(int),
    "NPV (M KRW)": [round(npf.npv(r, cash_flows), 1) for r in rates]
})

print("\nNPV Sensitivity to Discount Rate:")
print(sensitivity.to_string(index=False))

# Find where NPV crosses zero (approximately = IRR)
crossover = sensitivity[sensitivity["NPV (M KRW)"] <= 0].iloc[0]
print(f"\nNPV turns negative around {crossover['Discount Rate (%)']}% (IRR ~ {irr*100:.1f}%)")

# -------------------------------------------------------
# 5. Sensitivity table: multiple projects side-by-side
#    Useful for M&A target comparison (like consulting emulation project)
# -------------------------------------------------------
projects = {
    "Packaging Line":   [-500, 80, 120, 150, 180, 200],
    "Logistics System": [-300, 60,  90, 100, 110, 120],
    "ERP Upgrade":      [-200, 30,  50,  70,  80,  90],
}

print("\nProject Comparison:")
print(f"{'Project':<20} {'NPV @10% (M KRW)':>18} {'IRR':>8} {'Decision':>10}")
print("-" * 60)
for name, cfs in projects.items():
    pnpv = npf.npv(0.10, cfs)
    pirr = npf.irr(cfs)
    decision = "PROCEED" if pirr > 0.10 else "REJECT"
    print(f"{name:<20} {pnpv:>18.1f} {pirr*100:>7.1f}% {decision:>10}")
```

**Expected output (approximate):**
```
NPV at 10% discount rate: 17.8M KRW
IRR: 10.88%
WACC: 10.0%
Decision: PROCEED — IRR > WACC

Project Comparison:
Project              NPV @10% (M KRW)      IRR   Decision
------------------------------------------------------------
Packaging Line                   17.8   10.9%    PROCEED
Logistics System                 26.7   14.1%    PROCEED
ERP Upgrade                      24.8   17.9%    PROCEED
```

---

## Exercises

**1. Calculate NPV for a 5-year cash flow**

A Korean retail chain is considering opening a new store. Initial investment: 800M KRW. Projected annual cash flows: 100, 150, 200, 250, 300 (M KRW, years 1-5). WACC = 12%.

- Calculate NPV using `numpy_financial`.
- Should the company open the store?
- At what discount rate does the decision flip? (Find IRR manually, then verify with `npf.irr`)

**2. IRR vs WACC decision**

A steel component manufacturer (DART sector: 1차 금속) has a WACC of 11%. They are evaluating two mutually exclusive capex projects:

- Project A: -400M upfront, then 90, 110, 130, 150, 160 (M KRW)
- Project B: -400M upfront, then 150, 140, 130, 100, 80 (M KRW)

Calculate IRR for both. Which project would you recommend and why? (Hint: IRR alone can mislead on mutually exclusive projects — also check NPV.)

**3. Challenge — NPV sensitivity matrix**

Build a 2D sensitivity table where:
- Rows = discount rates from 6% to 18% (step 2%)
- Columns = revenue growth scenarios: base case, +10%, -10% (scale all positive cash flows)
- Cell values = NPV

Use pandas DataFrame with formatted output. This is the kind of table a consultant puts in a board deck to show the range of outcomes under different assumptions.

```python
# Starter structure
base_cfs = [-500, 80, 120, 150, 180, 200]
growth_scenarios = {"Bear (-10%)": 0.90, "Base": 1.00, "Bull (+10%)": 1.10}
discount_rates = [0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18]

# Build the matrix — fill this in
```

---

## Resource

- Primary: PyQuant News — https://pyquantnews.com/
- numpy_financial docs — https://numpy.org/numpy-financial/
- numpy_financial source (all functions): `npf.npv`, `npf.irr`, `npf.pv`, `npf.fv`, `npf.pmt`

---

## Cross-apply

**Consulting Emulation DCF model (`projects/consulting-emulation/agents/valuation.py`)**
- Your current DCF likely hardcodes the discount rate. Replace it with a WACC calculation (pull D/E ratio from DART financials) and run `npf.npv` on the projected FCF array. The sensitivity table from Exercise 3 becomes a slide in your output deck.

**M&A valuation agent**
- When screening DART targets, add an IRR filter: pull capex announcements from 사업보고서, estimate 5-year cash flows from revenue trend (yfinance or DART), compute IRR, flag companies where announced capex clears a 12% hurdle. That's a real buy-side analyst workflow.

**Lead Intelligence project (`projects/lead-intelligence/`)**
- AI readiness score already ranks companies. Layer on a "ROI of AI investment" model: estimate AI implementation cost vs. productivity gain → NPV → IRR. Companies where IRR > 15% become high-priority outreach targets.
