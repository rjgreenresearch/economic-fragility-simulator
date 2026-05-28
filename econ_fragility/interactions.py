"""
interactions.py -- Cross-domain correlation and Granger causality analysis.

Provides empirical grounding for the domain interaction weights used in
compound_index.py. Two analyses:

  1. Rolling cross-correlations between domain pairs at lags 1-4 quarters.
     Identifies which domain leads which, and at what strength.

  2. Pairwise Granger causality tests (F-test, OLS, lag order 1-4).
     Tests H0: "domain X does NOT Granger-cause domain Y."
     Rejection supports the directional interaction weights.

Results are used in Paper 7, Section 4 (Methodology) to defend the
interaction weight structure rather than asserting it.

Usage:
    from econ_fragility.interactions import run_interaction_analysis
    results = run_interaction_analysis(
        cfi_path="data/processed/compound_fragility_index.csv",
        output_dir="data/processed/"
    )
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests


DOMAIN_SHORT = {
    "d1_Wage-Produ": "Wage-Prod",
    "d2_Consumer B": "Consumer",
    "d3_Fiscal Sus": "Fiscal",
    "d4_Labour Mar": "Labour",
    "d5_Trade Arch": "Trade",
    "d6_Monetary C": "Monetary",
}

# Theoretical interaction structure from compound_index.py DEFAULT_WEIGHTS
# and the domain interaction matrix.  Listed as (cause, effect) pairs.
THEORETICAL_LINKS = [
    ("d1_Wage-Produ", "d2_Consumer B"),   # Wage stagnation → consumer credit
    ("d2_Consumer B", "d3_Fiscal Sus"),   # Consumer defaults → fiscal revenue
    ("d3_Fiscal Sus", "d6_Monetary C"),   # Fiscal stress → monetary constraint
    ("d4_Labour Mar", "d2_Consumer B"),   # Job loss → consumer defaults
    ("d4_Labour Mar", "d1_Wage-Produ"),   # Labour surplus → wage suppression
    ("d5_Trade Arch", "d2_Consumer B"),   # Import costs → purchasing power
    ("d5_Trade Arch", "d4_Labour Mar"),   # Trade shock → manufacturing layoffs
    ("d6_Monetary C", "d2_Consumer B"),   # High rates → mortgage/debt costs
    ("d6_Monetary C", "d3_Fiscal Sus"),   # High rates → debt service spiral
]


def _find_domain_cols(df):
    """Return ordered list of domain columns in the CFI DataFrame."""
    prefixes = ["d1_", "d2_", "d3_", "d4_", "d5_", "d6_"]
    found = []
    for p in prefixes:
        matches = [c for c in df.columns if c.startswith(p)]
        if matches:
            found.append(matches[0])
    return found


def rolling_cross_correlations(df, domain_cols, max_lag=4):
    """
    Compute Pearson cross-correlations between all domain pairs
    at lags 0 through max_lag quarters.

    Returns a dict: {(col_i, col_j): {lag: (r, p_value)}}
    """
    results = {}
    n = len(domain_cols)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ci, cj = domain_cols[i], domain_cols[j]
            pair_results = {}
            for lag in range(0, max_lag + 1):
                xi = df[ci].iloc[lag:].values
                xj = df[cj].iloc[:len(df)-lag].values if lag > 0 else df[cj].values
                # Align lengths
                min_len = min(len(xi), len(xj))
                xi = xi[:min_len]
                xj = xj[:min_len]
                if len(xi) < 10:
                    continue
                r, p = stats.pearsonr(xi, xj)
                pair_results[lag] = (round(r, 4), round(p, 4))
            results[(ci, cj)] = pair_results
    return results


def granger_causality_tests(df, domain_cols, max_lag=4):
    """
    Pairwise Granger causality tests for all ordered domain pairs.
    H0: column X does NOT Granger-cause column Y.
    Rejection (p < 0.10) supports directional interaction.

    Returns a dict: {(cause, effect): {lag: {'f_stat': ..., 'p_value': ...}}}
    """
    results = {}
    n = len(domain_cols)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            cause  = domain_cols[i]
            effect = domain_cols[j]

            # Build bivariate DataFrame, drop NaNs
            pair = df[[effect, cause]].dropna()
            if len(pair) < 20:
                continue

            try:
                gc = grangercausalitytests(
                    pair, maxlag=max_lag, verbose=False
                )
                lag_results = {}
                for lag in range(1, max_lag + 1):
                    if lag in gc:
                        # statsmodels returns (test_dict, ols_results_dict)
                        test_dict = gc[lag][0]
                        # Use F-test ('ssr_ftest')
                        f_stat = round(test_dict["ssr_ftest"][0], 4)
                        p_val  = round(test_dict["ssr_ftest"][1], 4)
                        lag_results[lag] = {
                            "f_stat":  f_stat,
                            "p_value": p_val,
                            "significant_10pct": p_val < 0.10,
                            "significant_5pct":  p_val < 0.05,
                        }
                results[(cause, effect)] = lag_results
            except Exception:
                pass

    return results


def summarise_interaction_weights(corr_results, granger_results,
                                   domain_cols):
    """
    Produce a summary table comparing:
      - Theoretical weight from compound_index.py
      - Empirical support from Granger causality tests
      - Maximum lag-1 cross-correlation

    Returns a DataFrame suitable for Table 1 of Paper 7.
    """
    from .compound_index import DEFAULT_WEIGHTS

    # Map column prefix to domain number
    col_to_num = {}
    for col in domain_cols:
        for num in range(1, 7):
            if col.startswith(f"d{num}_"):
                col_to_num[col] = num

    rows = []

    for cause_col, effect_col in THEORETICAL_LINKS:
        # Match to available columns
        cause_match  = next((c for c in domain_cols if c.startswith(cause_col[:5])),  None)
        effect_match = next((c for c in domain_cols if c.startswith(effect_col[:5])), None)

        if cause_match is None or effect_match is None:
            continue

        cause_num  = col_to_num.get(cause_match)
        effect_num = col_to_num.get(effect_match)

        cause_short  = DOMAIN_SHORT.get(cause_match,  cause_match)
        effect_short = DOMAIN_SHORT.get(effect_match, effect_match)

        # Theoretical weight for the effect domain
        theo_weight = DEFAULT_WEIGHTS.get(effect_num, 1.0)

        # Granger: best (lowest) p-value across lags
        gc_key = (cause_match, effect_match)
        best_gc_p = None
        best_gc_lag = None
        if gc_key in granger_results:
            for lag, res in granger_results[gc_key].items():
                if best_gc_p is None or res["p_value"] < best_gc_p:
                    best_gc_p   = res["p_value"]
                    best_gc_lag = lag

        # Correlation: lag-1 r value
        corr_key = (cause_match, effect_match)
        lag1_r = None
        if corr_key in corr_results and 1 in corr_results[corr_key]:
            lag1_r = corr_results[corr_key][1][0]

        rows.append({
            "Cause Domain":    cause_short,
            "Effect Domain":   effect_short,
            "Theoretical Weight": theo_weight,
            "Lag-1 Correlation (r)": lag1_r,
            "Best Granger p-value": best_gc_p,
            "Best Granger Lag": best_gc_lag,
            "Granger Sig (10%)": (best_gc_p < 0.10) if best_gc_p is not None else False,
            "Granger Sig (5%)":  (best_gc_p < 0.05) if best_gc_p is not None else False,
        })

    return pd.DataFrame(rows)


def print_interaction_report(summary_df, granger_results, domain_cols):
    """Print a readable report of the interaction analysis."""
    print("\n" + "=" * 72)
    print("  DOMAIN INTERACTION ANALYSIS")
    print("  Granger Causality and Cross-Correlation Summary")
    print("=" * 72)

    print("\nTheoretical vs. Empirical Interaction Structure:")
    print(f"  {'Cause':<18} {'→  Effect':<18} {'Weight':>8} "
          f"{'Lag-1 r':>10} {'Granger p':>12} {'Sig':>6}")
    print(f"  {'-'*17} {'-'*17} {'-'*8} {'-'*10} {'-'*12} {'-'*6}")

    confirmed = 0
    for _, row in summary_df.iterrows():
        sig = "***" if row["Granger Sig (5%)"] else \
              "*"   if row["Granger Sig (10%)"] else ""
        r_str = f"{row['Lag-1 Correlation (r)']:.3f}" \
                if row["Lag-1 Correlation (r)"] is not None else "  n/a"
        p_str = f"{row['Best Granger p-value']:.3f}" \
                if row["Best Granger p-value"] is not None else "   n/a"
        print(f"  {row['Cause Domain']:<18} {row['Effect Domain']:<18} "
              f"{row['Theoretical Weight']:>8.1f} {r_str:>10} {p_str:>12} {sig:>6}")
        if row["Granger Sig (10%)"]:
            confirmed += 1

    total = len(summary_df)
    print(f"\n  {confirmed}/{total} theoretical links confirmed at 10% significance")
    print(f"  (*** = 5%, * = 10%)")

    print("\n  Strongest empirical links (lowest Granger p-value):")
    if not summary_df.empty and summary_df["Best Granger p-value"].notna().any():
        top = summary_df.dropna(subset=["Best Granger p-value"]) \
                        .nsmallest(3, "Best Granger p-value")
        for _, row in top.iterrows():
            print(f"    {row['Cause Domain']} → {row['Effect Domain']}: "
                  f"p={row['Best Granger p-value']:.4f} "
                  f"(lag {row['Best Granger Lag']})")
    print("=" * 72)


def run_interaction_analysis(
    cfi_path="data/processed/compound_fragility_index.csv",
    output_dir="data/processed/",
    max_lag=4,
):
    """
    Run full interaction analysis and save results.

    Returns:
        summary_df: DataFrame for Table 1 of the paper
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(cfi_path, index_col=0, parse_dates=True)
    domain_cols = _find_domain_cols(df)

    if len(domain_cols) < 2:
        print("  Insufficient domain columns for interaction analysis")
        return None

    print(f"  Running cross-correlations (lags 0–{max_lag})...")
    corr_results = rolling_cross_correlations(df, domain_cols, max_lag)

    print(f"  Running Granger causality tests (lags 1–{max_lag})...")
    granger_results = granger_causality_tests(df, domain_cols, max_lag)

    print("  Building summary table...")
    summary_df = summarise_interaction_weights(
        corr_results, granger_results, domain_cols
    )

    # Save outputs
    summary_path = os.path.join(output_dir, "interaction_analysis.csv")
    summary_df.to_csv(summary_path, index=False)

    # Build full Granger results table
    granger_rows = []
    for (cause, effect), lag_results in granger_results.items():
        cause_s  = DOMAIN_SHORT.get(cause,  cause)
        effect_s = DOMAIN_SHORT.get(effect, effect)
        for lag, res in lag_results.items():
            granger_rows.append({
                "cause":    cause_s,
                "effect":   effect_s,
                "lag":      lag,
                "f_stat":   res["f_stat"],
                "p_value":  res["p_value"],
                "sig_10":   res["significant_10pct"],
                "sig_5":    res["significant_5pct"],
            })
    granger_df = pd.DataFrame(granger_rows)
    granger_path = os.path.join(output_dir, "granger_causality_full.csv")
    granger_df.to_csv(granger_path, index=False)

    print_interaction_report(summary_df, granger_results, domain_cols)

    return summary_df
