"""
compound_index.py -- Compound Fragility Index (CFI) computation.

Integrates six domain fragility scores into a single compound metric
using the MTS multiplicative interaction framework.

CFI = product of (1 + D_k * w_k) for k = 1..6

When all domains are at 0.0, CFI = 1.0 (fully resilient).
When multiple domains are simultaneously stressed, CFI rises
multiplicatively -- capturing the compound threshold dynamic.
"""

import pandas as pd
import numpy as np
from .domains import wage_productivity, consumer_balance, fiscal_space
from .domains import labour_market, trade_cascade, monetary_constraint


DOMAIN_NAMES = {
    1: "Wage-Productivity Gap",
    2: "Consumer Balance Sheet",
    3: "Fiscal Sustainability",
    4: "Labour Market",
    5: "Trade Architecture",
    6: "Monetary Constraint",
}

# Default interaction weights (1.0 = no amplification)
# Values > 1.0 indicate amplification from cross-domain stress
DEFAULT_WEIGHTS = {
    1: 1.0,   # Wage-productivity
    2: 1.2,   # Consumer balance (amplified by wage stagnation)
    3: 1.1,   # Fiscal (amplified by consumer defaults)
    4: 1.2,   # Labour market (amplified by trade stress)
    5: 1.0,   # Trade architecture
    6: 1.3,   # Monetary constraint (amplified by fiscal + consumer)
}

DOMAIN_MODULES = {
    1: wage_productivity,
    2: consumer_balance,
    3: fiscal_space,
    4: labour_market,
    5: trade_cascade,
    6: monetary_constraint,
}


def compute_all_domains(data_dir="data/raw"):
    """Compute fragility indices for all six domains.
    
    Returns dict of {domain_num: DataFrame with fragility_score column}
    """
    results = {}
    for num, module in DOMAIN_MODULES.items():
        name = DOMAIN_NAMES[num]
        try:
            df = module.compute_index(data_dir)
            results[num] = df
            latest = df["fragility_score"].iloc[-1]
            n_obs = len(df)
            print(f"  Domain {num} ({name}): {latest:.3f} (n={n_obs})")
        except Exception as e:
            print(f"  Domain {num} ({name}): ERROR - {e}")
    return results


def compute_cfi(domain_results, weights=None, start_date="2000-01-01"):
    """Compute Compound Fragility Index from domain results.
    
    Args:
        domain_results: dict from compute_all_domains()
        weights: dict of {domain_num: weight}, defaults to DEFAULT_WEIGHTS
        start_date: align all domains from this date forward
    
    Returns:
        DataFrame with domain scores and compound CFI
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Extract fragility_score from each domain and align to common quarterly index
    scores = {}
    for num, df in domain_results.items():
        s = df["fragility_score"].copy()
        s.index = pd.to_datetime(s.index)
        s = s.resample("QS").mean()
        scores[f"d{num}_{DOMAIN_NAMES[num][:10]}"] = s
    
    combined = pd.DataFrame(scores)
    combined = combined.loc[start_date:].ffill().dropna()
    
    # Compute CFI: product of (1 + D_k * w_k)
    cfi = pd.Series(1.0, index=combined.index)
    for num in domain_results:
        col = f"d{num}_{DOMAIN_NAMES[num][:10]}"
        if col in combined.columns:
            w = weights.get(num, 1.0)
            cfi = cfi * (1 + combined[col] * w)
    
    combined["CFI"] = cfi
    
    # Normalise CFI to 0-1 scale based on theoretical range
    # Min CFI = 1.0 (all domains at 0), Max theoretical = product of (1 + 1.0 * w_k)
    max_cfi = 1.0
    for w in weights.values():
        max_cfi *= (1 + w)
    combined["CFI_normalised"] = ((combined["CFI"] - 1.0) / (max_cfi - 1.0)).clip(0, 1)
    
    return combined


def print_summary(combined):
    """Print human-readable summary of compound fragility."""
    latest = combined.iloc[-1]
    
    print("\n" + "=" * 65)
    print("  COMPOUND FRAGILITY INDEX — LATEST VALUES")
    print("=" * 65)
    print(f"  Date: {combined.index[-1].strftime('%Y-%m-%d')}")
    print(f"  Compound CFI (raw): {latest['CFI']:.3f}")
    print(f"  Compound CFI (normalised 0-1): {latest['CFI_normalised']:.3f}")
    print()
    
    for col in combined.columns:
        if col.startswith("d") and "_" in col:
            domain_name = col.split("_", 1)[1]
            val = latest[col]
            bar = "#" * int(val * 40)
            print(f"  {domain_name:<25} {val:.3f} |{bar}")
    
    print()
    cfi_n = latest["CFI_normalised"]
    if cfi_n > 0.7:
        assessment = "CRITICAL — compound stress near threshold"
    elif cfi_n > 0.5:
        assessment = "ELEVATED — multiple domains under stress"
    elif cfi_n > 0.3:
        assessment = "MODERATE — some domains showing strain"
    else:
        assessment = "RESILIENT — absorptive capacity adequate"
    
    print(f"  Assessment: {assessment}")
    print("=" * 65)
