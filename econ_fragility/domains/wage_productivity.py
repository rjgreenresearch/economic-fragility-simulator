"""
wage_productivity.py -- Domain 1: Wage-Productivity Gap

Measures the decoupling of real wages from productivity growth.
When workers produce more but earn proportionally less, the gap
is filled by credit (compounding Domain 2).

Key metric: Wage-Productivity Ratio (WPR) = COMPRNFB / OPHNFB
indexed to 1973 = 1.00. Labour share of GDP provides validation.

Fragility rises as WPR falls below historical norms.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw", base_year=1973):
    """Compute wage-productivity gap fragility index.
    
    Returns DataFrame with columns: date, wpr, labour_share,
    real_earnings_growth, fragility_score
    """
    # Load series
    comp = load_series("COMPRNFB", data_dir)    # Real compensation/hour
    output = load_series("OPHNFB", data_dir)     # Output/hour
    
    # Align to common quarterly index
    comp.index = pd.to_datetime(comp.index)
    output.index = pd.to_datetime(output.index)
    
    df = pd.DataFrame({"compensation": comp, "output": output}).dropna()
    
    # Compute WPR indexed to base_year
    base_mask = df.index.year == base_year
    if base_mask.any():
        comp_base = df.loc[base_mask, "compensation"].mean()
        out_base = df.loc[base_mask, "output"].mean()
        base_ratio = comp_base / out_base
    else:
        # Fallback: use earliest available
        base_ratio = df["compensation"].iloc[0] / df["output"].iloc[0]
    
    df["wpr"] = (df["compensation"] / df["output"]) / base_ratio
    
    # Load labour share for validation
    try:
        labour_share = load_series("LABSHPUSA156NRUG", data_dir)
        labour_share.index = pd.to_datetime(labour_share.index)
        # Resample annual to quarterly via forward fill
        labour_share = labour_share.resample("QS").ffill()
        df["labour_share"] = labour_share.reindex(df.index, method="ffill")
    except Exception:
        df["labour_share"] = np.nan
    
    # Load real earnings for additional context
    try:
        earnings = load_series("LES1252881600Q", data_dir)
        earnings.index = pd.to_datetime(earnings.index)
        df["real_earnings"] = earnings.reindex(df.index, method="nearest")
    except Exception:
        df["real_earnings"] = np.nan
    
    # Compute fragility score (0 = resilient, 1 = threshold)
    # Threshold hypothesis: WPR below 0.60 indicates structural decoupling
    # Map WPR from [0.60, 1.00] to fragility [1.0, 0.0]
    wpr_floor = 0.55   # Below this = maximum fragility
    wpr_ceiling = 1.00  # At or above this = zero fragility
    
    df["fragility_score"] = np.clip(
        1.0 - (df["wpr"] - wpr_floor) / (wpr_ceiling - wpr_floor),
        0.0, 1.0
    )
    
    return df[["wpr", "labour_share", "real_earnings", "fragility_score"]]
