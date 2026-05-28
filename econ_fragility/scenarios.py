"""
scenarios.py -- Scenario stress-testing engine for the Economic Fragility Simulator.

Four scenarios parameterised with April 2026 real data:
  1. tariff_cascade     -- Trade stress cascading through consumer and labour domains
  2. ai_displacement    -- Structural labour displacement cascading through consumer
  3. fiscal_constraint  -- Fiscal buffer exhaustion constraining counter-cyclical response
  4. compound_stress    -- Simultaneous multi-domain shock (stagflation scenario)

Each scenario defines:
  - Domain-level shocks (additive increments to baseline fragility scores)
  - Interaction amplifiers (domain-to-domain cascade multipliers)
  - A quarterly time path over 1, 2, 4, and 8 year horizons
  - Sourced parameters calibrated to April 2026 data

Usage:
    from econ_fragility.scenarios import run_scenario, run_all_scenarios
    results = run_scenario("tariff_cascade", baseline_cfi)
    all_results = run_all_scenarios(baseline_cfi)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Scenario parameter definitions
# All shock magnitudes sourced and documented below.
# ---------------------------------------------------------------------------

SCENARIO_PARAMS = {

    # -----------------------------------------------------------------------
    # SCENARIO 1: TARIFF CASCADE
    # Sources:
    #   - Effective tariff rate 8.9-11.8% (PWBM April 15 2026; Yale Budget Lab April 8 2026)
    #   - Consumer price impact +0.7-1.1% short-run; $940-$1,500/household (Yale Budget Lab)
    #   - Manufacturing jobs lost: ~89,000 in 10 months (Axios April 2 2026)
    #   - Trade deficit $901.5B, barely changed despite tariffs (BEA/Census Feb 19 2026)
    #   - Pass-through to consumer prices: 72% at 12 months (Goldman Sachs)
    #   - Ag exports to China: soybean -78%, corn -99% (CFR April 2 2026)
    # -----------------------------------------------------------------------
    "tariff_cascade": {
        "label": "Tariff Cascade",
        "description": (
            "Section 122 10% across-the-board tariff persists and escalates to 15%. "
            "Import prices surge, manufacturing contracts, consumer prices rise ~1.1%. "
            "Agriculture exports collapse. Trade stress cascades into consumer balance "
            "and labour market as margin compression triggers layoffs."
        ),
        "horizon_quarters": 8,  # 2 years
        # Direct domain shocks at peak (additive to baseline score)
        "domain_shocks": {
            5: +0.25,   # Trade Architecture: import prices surge, mfg PPI spike
            2: +0.12,   # Consumer Balance: $1,500/yr household income loss reduces savings
            4: +0.10,   # Labour Market: 89k mfg jobs lost, ongoing manufacturing contraction
            3: +0.03,   # Fiscal Sustainability: tariff revenue partially offsets but deficit widens
            6: +0.08,   # Monetary Constraint: inflation prevents Fed from cutting
            1: +0.02,   # Wage-Productivity: margin compression suppresses wage growth
        },
        # Cascade path: shock ramps in over N quarters
        "ramp_quarters": {
            5: 2,   # Trade stress hits quickly
            2: 4,   # Consumer feels it after 4 quarters (savings depletion)
            4: 4,   # Labour market lags trade shock by ~1 year
            3: 6,   # Fiscal impact materialises slowly
            6: 2,   # Monetary constraint tightens fast (CPI already at 3.3%)
            1: 6,   # Wage suppression is slow-moving
        },
        # Cross-domain interaction amplifiers (beyond DEFAULT_WEIGHTS in compound_index.py)
        # multiplier applied to receiving domain's shock when source domain is stressed
        "cascade_amplifiers": {
            (5, 2): 1.4,   # Trade stress → consumer balance (import prices hit HH)
            (5, 4): 1.3,   # Trade stress → labour market (manufacturing layoffs)
            (2, 3): 1.2,   # Consumer stress → fiscal (defaults reduce revenue)
            (6, 2): 1.3,   # Monetary constraint → consumer (high rates hurt mortgages)
        },
        "sources": [
            "PWBM Effective Tariff Rates, April 15 2026",
            "Yale Budget Lab State of US Tariffs, April 8 2026",
            "Goldman Sachs US Inflation Monitor, April 2026",
            "BEA/Census Trade in Goods and Services, February 2026",
            "Axios Liberation Day one-year review, April 2 2026",
        ],
    },

    # -----------------------------------------------------------------------
    # SCENARIO 2: AI DISPLACEMENT WAVE
    # Sources:
    #   - Goldman Sachs: 6-7% of US workforce (~11M) displaced over 10 years
    #   - 2025 AI-attributed layoffs: ~55,000 direct (Challenger Gray Christmas)
    #   - Entry-level workers aged 22-25: -16% employment in AI-exposed roles (Goldman)
    #   - McKinsey: 57% of US work hours involve AI-capable tasks
    #   - IMF: 60% of advanced-economy jobs have AI exposure
    #   - WIOA Title I FY26 enacted: $2.919B (vs $5.67B FY25 before cuts)
    #   - Retraining pipeline: 2-4 year degree cycle vs. weeks-to-months displacement
    # -----------------------------------------------------------------------
    "ai_displacement": {
        "label": "AI Displacement Wave",
        "description": (
            "Accelerating AI adoption displaces 6-7% of the US workforce (~11M workers) "
            "over 8 quarters. Entry-level hiring collapses first. Retraining pipeline "
            "(WIOA $2.9B, 2-4yr degree cycle) cannot absorb displacement rate. "
            "Labour income loss cascades to consumer balance sheet and tax revenues."
        ),
        "horizon_quarters": 12,  # 3 years
        "domain_shocks": {
            4: +0.22,   # Labour Market: participation falls, U-6 rises, involuntary PT surges
            2: +0.15,   # Consumer Balance: income loss → savings drawdown → delinquency rise
            1: +0.08,   # Wage-Productivity: labour surplus suppresses wage growth further
            3: +0.06,   # Fiscal: reduced payroll tax revenue, increased safety net spending
            6: +0.05,   # Monetary Constraint: Fed can't cut (inflation) or raise (recession)
            5: +0.02,   # Trade: reduced consumer demand for imports; minor effect
        },
        "ramp_quarters": {
            4: 4,    # Labour market stress builds over ~1 year
            2: 6,    # Consumer follows labour with ~2 quarter lag
            1: 8,    # Wage suppression is slow structural shift
            3: 8,    # Fiscal impact materialises as automatic stabilisers kick in
            6: 4,    # Monetary dilemma tightens as stagflation signals mount
            5: 8,    # Trade impact is diffuse and slow
        },
        "cascade_amplifiers": {
            (4, 2): 1.5,   # Labour → consumer (primary cascade: job loss hits savings)
            (4, 1): 1.3,   # Labour → wages (surplus labour suppresses compensation)
            (2, 3): 1.4,   # Consumer defaults → fiscal (revenue falls, transfers rise)
            (1, 2): 1.2,   # Wage stagnation → consumer (chronic income shortfall)
        },
        "sources": [
            "Goldman Sachs: AI and the Labor Market, 2024-2026",
            "Challenger Gray Christmas: 2025 Job Cuts Report",
            "McKinsey Global Institute: AI and the Future of Work, 2025",
            "IMF World Economic Outlook, April 2026",
            "NAWB WIOA Funding Analysis, 2026",
        ],
    },

    # -----------------------------------------------------------------------
    # SCENARIO 3: FISCAL CONSTRAINT
    # Sources:
    #   - Debt/GDP (public): 101% in FY2026 -> 120% by 2036 (CBO Jan 2026)
    #   - Total federal debt: $38.5T (~122-123% of GDP) (Treasury)
    #   - FY2026 deficit: $1.9T (~6% of GDP) (CBO)
    #   - FY2026 net interest: ~$1T (CBO); Q1 FY26 interest $270.3B > defense $266.9B
    #   - Interest > defense since FY2024 (Treasury, EPIC)
    #   - CBO: interest as % revenue reaches 28% by 2055
    #   - 1pp rate increase = $3.2T additional interest over 10 years (CBO)
    #   - Moody's downgraded US to Aa1 May 2025
    # -----------------------------------------------------------------------
    "fiscal_constraint": {
        "label": "Fiscal Constraint",
        "description": (
            "Federal debt/GDP reaches 110% as interest payments crowd out discretionary "
            "spending. At $1T+ in annual interest (Q1 FY26: $270B vs $267B defense), "
            "the government cannot mount a counter-cyclical fiscal response when a recession "
            "arrives. The COVID stimulus playbook is unavailable. Bond market pressure "
            "forces austerity at the worst moment."
        ),
        "horizon_quarters": 16,  # 4 years
        "domain_shocks": {
            3: +0.04,   # Fiscal Sustainability: already at 0.95; another 4pp closes buffer
            6: +0.12,   # Monetary Constraint: bond market forces rates up (crowding out)
            2: +0.08,   # Consumer Balance: austerity cuts transfer payments, raises costs
            4: +0.06,   # Labour Market: public sector employment cuts (federal DOGE-style)
            1: +0.03,   # Wage-Productivity: public sector wage freeze spreads
            5: +0.02,   # Trade Architecture: reduced government procurement
        },
        "ramp_quarters": {
            3: 1,    # Fiscal already near threshold — shock is immediate
            6: 3,    # Bond market repricing takes ~3 quarters
            2: 6,    # Consumer feels austerity cuts after 6 quarters
            4: 4,    # Federal employment contraction is already underway
            1: 10,   # Wage effects are very slow
            5: 10,   # Trade effects minimal and slow
        },
        "cascade_amplifiers": {
            (3, 6): 1.6,   # Fiscal stress → monetary (bond market forces rate increases)
            (6, 2): 1.4,   # Higher rates → consumer (mortgage, credit card costs)
            (6, 3): 1.3,   # Higher rates → fiscal (debt service spiral: each 1pp = $320B/yr)
            (3, 4): 1.2,   # Fiscal → labour (government layoffs, contractor cuts)
        },
        "sources": [
            "CBO Budget and Economic Outlook 2026 to 2036, January 2026",
            "CBO Long-Term Budget Outlook 2025 to 2055, March 2025",
            "CRFB Analysis of CBO March 2025 Long-Term Budget Outlook",
            "EPIC for America: Interest Spending Tracker Q1 FY2026",
            "Treasury Monthly Statement, January 2026",
        ],
    },

    # -----------------------------------------------------------------------
    # SCENARIO 4: COMPOUND STRESS (STAGFLATION)
    # Sources:
    #   - Fed funds: 3.50-3.75% held March 2026 FOMC (Federal Reserve)
    #   - CPI March 2026: 3.3% headline / 2.6% core (BLS April 10 2026)
    #   - Core PCE Feb 2026: 3.0% (BEA)
    #   - Q4 2025 GDP: +0.5% annualised; Q1 2026 GDPNow: ~1.2% (BEA, Atlanta Fed)
    #   - Unemployment March 2026: 4.3%; U-6: 8.0% (BLS April 3 2026)
    #   - NY Fed recession probability: ~25% (NY Fed)
    #   - Moody's AI model recession probability: ~49%
    #   - Stanford SIEPR: stagflation as central 2026 macro risk
    #   - Iran war (Feb 28 2026): gasoline +21.2% in March; CPI peak ~3.6-4.0% projected
    #   - Goldman Sachs raised recession probability to 30%
    # -----------------------------------------------------------------------
    "compound_stress": {
        "label": "Compound Stress / Stagflation",
        "description": (
            "Simultaneous shocks across all six domains: tariffs sustain 3.3%+ CPI "
            "while GDP slows to ~1.2% (Q1 2026 nowcast). Fed holds at 3.50-3.75% "
            "unable to cut (inflation) or raise (recession risk). Iran war adds "
            "energy shock. Fiscal domain (at 0.95) cannot buffer. Consumer domain "
            "absorptive capacity exhausted as savings fall and delinquency rises. "
            "NY Fed recession probability 25%, Moody's AI model 49%."
        ),
        "horizon_quarters": 8,  # 2 years
        "domain_shocks": {
            5: +0.20,   # Trade: tariff cascade + Iran oil shock (gasoline +21.2% March)
            6: +0.18,   # Monetary: Fed paralysed — inflation above target, growth slowing
            3: +0.04,   # Fiscal: deficit widens; already at 0.95 baseline
            2: +0.14,   # Consumer: energy costs + tariffs + rate freeze hit household balance
            4: +0.12,   # Labour: slowdown, Feb -133k payrolls, rising long-term unemployment
            1: +0.03,   # Wage-Productivity: structural (small marginal shock on top of 0.80)
        },
        "ramp_quarters": {
            5: 1,    # Trade/energy shock already in data
            6: 2,    # Monetary constraint tightening immediately
            3: 4,    # Fiscal deteriorates as automatic stabilisers kick in
            2: 3,    # Consumer balance deteriorates within 3 quarters
            4: 3,    # Labour market cools within 3 quarters
            1: 8,    # Structural wage effect is slow
        },
        "cascade_amplifiers": {
            (5, 6): 1.4,   # Trade/energy → monetary (inflation forces Fed's hand)
            (5, 2): 1.5,   # Trade → consumer (energy + tariff cost squeeze)
            (6, 2): 1.4,   # Monetary → consumer (mortgage/debt service at 3.75%)
            (6, 3): 1.5,   # Monetary → fiscal (rate hold raises debt service)
            (2, 3): 1.3,   # Consumer defaults → fiscal (revenue fall + transfer rise)
            (4, 2): 1.4,   # Labour → consumer (job losses reduce income and savings)
        },
        "sources": [
            "BLS CPI Summary April 10 2026",
            "BLS Employment Situation April 3 2026",
            "BEA GDP Third Estimate Q4 2025, April 9 2026",
            "Federal Reserve FOMC Statement March 18 2026",
            "Atlanta Fed GDPNow April 21 2026",
            "NY Fed Yield Curve Model April 2026",
            "Stanford SIEPR US Economy in 2026 Policy Brief",
        ],
    },
}


# ---------------------------------------------------------------------------
# Scenario execution engine
# ---------------------------------------------------------------------------

def _apply_ramp(shock_value: float, quarter: int, ramp_quarters: int) -> float:
    """Linearly ramp a shock from 0 to full magnitude over ramp_quarters."""
    if ramp_quarters <= 0:
        return shock_value
    fraction = min(quarter / ramp_quarters, 1.0)
    return shock_value * fraction


def run_scenario(
    scenario_name: str,
    baseline_domain_scores: Dict[int, float],
    baseline_cfi_normalised: float,
) -> pd.DataFrame:
    """
    Run a single scenario against the current baseline domain scores.

    Args:
        scenario_name: Key from SCENARIO_PARAMS
        baseline_domain_scores: {domain_num: current fragility score} from latest data
        baseline_cfi_normalised: current normalised CFI (0-1)

    Returns:
        DataFrame with columns:
            quarter, [domain_1..6 shocked scores], CFI_raw, CFI_normalised,
            delta_vs_baseline, assessment
    """
    params = SCENARIO_PARAMS[scenario_name]
    horizons = params["horizon_quarters"]
    domain_shocks = params["domain_shocks"]
    ramp_q = params.get("ramp_quarters", {k: horizons for k in domain_shocks})
    amplifiers = params.get("cascade_amplifiers", {})

    from .compound_index import DEFAULT_WEIGHTS

    rows = []

    for q in range(0, horizons + 1):
        # Start from current baseline
        scores = dict(baseline_domain_scores)

        # Apply direct domain shocks (ramped)
        for domain, shock in domain_shocks.items():
            ramp = ramp_q.get(domain, horizons)
            delta = _apply_ramp(shock, q, ramp)
            scores[domain] = min(scores[domain] + delta, 1.0)

        # Apply cascade amplifiers
        for (src, dst), amp in amplifiers.items():
            if src in scores and dst in scores:
                # Additional stress on dst proportional to src shock above baseline
                src_excess = max(scores[src] - baseline_domain_scores.get(src, 0), 0)
                cascade_increment = src_excess * (amp - 1.0) * 0.15  # 15% of amplified excess
                scores[dst] = min(scores[dst] + cascade_increment, 1.0)

        # Compute CFI
        cfi_raw = 1.0
        for domain, score in scores.items():
            w = DEFAULT_WEIGHTS.get(domain, 1.0)
            cfi_raw *= (1 + score * w)

        max_cfi = 1.0
        for w in DEFAULT_WEIGHTS.values():
            max_cfi *= (1 + w)
        cfi_norm = max((cfi_raw - 1.0) / (max_cfi - 1.0), 0.0)

        row = {
            "quarter": q,
            "d1_wage_productivity": round(scores.get(1, 0), 4),
            "d2_consumer_balance": round(scores.get(2, 0), 4),
            "d3_fiscal_sustainability": round(scores.get(3, 0), 4),
            "d4_labour_market": round(scores.get(4, 0), 4),
            "d5_trade_architecture": round(scores.get(5, 0), 4),
            "d6_monetary_constraint": round(scores.get(6, 0), 4),
            "CFI_raw": round(cfi_raw, 4),
            "CFI_normalised": round(cfi_norm, 4),
            "delta_vs_baseline": round(cfi_norm - baseline_cfi_normalised, 4),
        }

        # Assessment
        if cfi_norm > 0.18:
            row["assessment"] = "CRITICAL — exceeds GFC peak (0.175)"
        elif cfi_norm > 0.15:
            row["assessment"] = "SEVERE — at or above GFC level"
        elif cfi_norm > 0.12:
            row["assessment"] = "ELEVATED — above COVID level (0.125)"
        elif cfi_norm > 0.08:
            row["assessment"] = "MODERATE — above pre-GFC baseline"
        else:
            row["assessment"] = "RESILIENT"

        rows.append(row)

    return pd.DataFrame(rows).set_index("quarter")


def run_all_scenarios(
    baseline_domain_scores: Dict[int, float],
    baseline_cfi_normalised: float,
    output_dir: str = "data/scenarios",
) -> Dict[str, pd.DataFrame]:
    """
    Run all four scenarios and save CSVs.

    Returns dict of {scenario_name: DataFrame}
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    results = {}
    for name, params in SCENARIO_PARAMS.items():
        df = run_scenario(name, baseline_domain_scores, baseline_cfi_normalised)
        results[name] = df
        outpath = os.path.join(output_dir, f"scenario_{name}.csv")
        df.to_csv(outpath)

    return results


def print_scenario_summary(results: Dict[str, pd.DataFrame], baseline_cfi: float):
    """Print a comparative summary table of all scenario outcomes."""
    print("\n" + "=" * 72)
    print("  SCENARIO ANALYSIS — COMPOUND FRAGILITY INDEX PROJECTIONS")
    print(f"  Baseline CFI (current): {baseline_cfi:.3f}")
    print("=" * 72)
    print(f"\n  {'Scenario':<28} {'Q4':>7} {'Q8':>7} {'Q12':>7} {'Peak':>7}  {'Assessment at Peak'}")
    print(f"  {'-'*27} {'-'*7} {'-'*7} {'-'*7} {'-'*7}  {'-'*25}")

    for name, df in results.items():
        label = SCENARIO_PARAMS[name]["label"]
        q4  = df.loc[min(4,  len(df)-1), "CFI_normalised"] if len(df) > 4  else df["CFI_normalised"].iloc[-1]
        q8  = df.loc[min(8,  len(df)-1), "CFI_normalised"] if len(df) > 8  else df["CFI_normalised"].iloc[-1]
        q12 = df.loc[min(12, len(df)-1), "CFI_normalised"] if len(df) > 12 else df["CFI_normalised"].iloc[-1]
        peak = df["CFI_normalised"].max()
        peak_assessment = df.loc[df["CFI_normalised"].idxmax(), "assessment"]
        print(f"  {label:<28} {q4:>7.3f} {q8:>7.3f} {q12:>7.3f} {peak:>7.3f}  {peak_assessment}")

    print(f"\n  Reference points:")
    print(f"    Pre-GFC (2007):    0.061")
    print(f"    GFC (2009):        0.155")
    print(f"    Post-GFC peak:     0.175")
    print(f"    COVID (2020):      0.125")
    print(f"    Current baseline:  {baseline_cfi:.3f}")
    print("=" * 72)
