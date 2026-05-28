"""
monetary_constraint.py -- Domain 6: Monetary Policy Constraint

Measures the Federal Reserve's remaining absorptive capacity --
its ability to cushion shocks through rate cuts and balance sheet tools.

Key metric: Monetary Space Index combining rate cutting room,
yield curve shape, balance sheet capacity, and inflation expectations.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw"):
    """Compute monetary policy constraint fragility index."""
    
    fed_funds = load_series("FEDFUNDS", data_dir)
    yield_curve = load_series("T10Y2Y", data_dir)    # 10yr - 2yr spread
    fed_assets = load_series("WALCL", data_dir)       # Fed balance sheet (millions)
    oil = load_series("DCOILWTICO", data_dir)         # Oil price
    vix = load_series("VIXCLS", data_dir)             # Volatility index
    
    frames = {}
    for name, series in [("fed_funds", fed_funds), ("yield_curve", yield_curve),
                          ("fed_assets", fed_assets), ("oil_price", oil),
                          ("vix", vix)]:
        s = series.copy()
        s.index = pd.to_datetime(s.index)
        frames[name] = s.resample("QS").mean()
    
    df = pd.DataFrame(frames).dropna(how="all").ffill().dropna()
    
    # Try to add breakeven inflation
    try:
        breakeven = load_series("T10YIE", data_dir)
        breakeven.index = pd.to_datetime(breakeven.index)
        df["breakeven_inflation"] = breakeven.resample("QS").mean().reindex(df.index, method="ffill")
    except Exception:
        df["breakeven_inflation"] = np.nan
    
    # Rate cutting room: higher rates = more room = less fragility
    # Below 1% = no room (high fragility), above 5% = ample room (low)
    df["rate_fragility"] = np.clip(
        1.0 - (df["fed_funds"] - 0.5) / (5.5 - 0.5), 0.0, 1.0
    )
    
    # Yield curve: inverted (negative) = high fragility, steep positive = low
    # Below -0.5 = high, above 1.5 = low
    df["curve_fragility"] = np.clip(
        1.0 - (df["yield_curve"] - (-0.5)) / (2.0 - (-0.5)), 0.0, 1.0
    )
    
    # Balance sheet as % of peak: closer to peak = less room
    peak_assets = df["fed_assets"].max()
    df["balance_fragility"] = np.clip(
        df["fed_assets"] / peak_assets, 0.0, 1.0
    ) if peak_assets > 0 else 0.5
    
    # VIX: above 30 = high stress, below 15 = low
    df["vix_fragility"] = np.clip(
        (df["vix"] - 12) / (35 - 12), 0.0, 1.0
    )
    
    # Composite
    df["fragility_score"] = (
        df["rate_fragility"] * 0.30 +
        df["curve_fragility"] * 0.25 +
        df["balance_fragility"] * 0.20 +
        df["vix_fragility"] * 0.25
    ).clip(0.0, 1.0)
    
    return df[["fed_funds", "yield_curve", "fed_assets", "vix", "fragility_score"]]
