"""
trade_cascade.py -- Domain 5: Trade Architecture Stress

Measures tariff and trade policy stress as cost cascades through
the domestic supply chain.

Key metric: Trade Cascade Index combining import price changes,
manufacturing input costs, and trade balance trajectory.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw"):
    """Compute trade architecture stress fragility index."""
    
    trade_bal = load_series("BOPGSTB", data_dir)     # Trade balance
    import_px = load_series("IR", data_dir)           # Import price index
    mfg_ppi = load_series("PCUOMFGOMFG", data_dir)   # Manufacturing PPI
    durable = load_series("DGORDER", data_dir)        # Durable goods orders
    
    frames = {}
    for name, series in [("trade_balance", trade_bal), ("import_prices", import_px),
                          ("mfg_ppi", mfg_ppi), ("durable_orders", durable)]:
        s = series.copy()
        s.index = pd.to_datetime(s.index)
        frames[name] = s.resample("QS").mean()
    
    df = pd.DataFrame(frames).dropna(how="all").ffill().dropna()
    
    # Import price year-over-year change
    df["import_px_yoy"] = df["import_prices"].pct_change(4) * 100  # 4 quarters
    
    # Manufacturing PPI year-over-year change
    df["mfg_ppi_yoy"] = df["mfg_ppi"].pct_change(4) * 100
    
    # Trade balance deterioration (more negative = worse)
    df["trade_bal_ma"] = df["trade_balance"].rolling(4).mean()
    trade_worst = df["trade_balance"].quantile(0.05)  # 5th percentile
    trade_best = df["trade_balance"].quantile(0.75)   # 75th percentile
    
    # Sub-scores
    # Import price surge: above 10% yoy = high fragility, below 0% = low
    df["import_fragility"] = np.clip(
        df["import_px_yoy"].fillna(0) / 12.0, 0.0, 1.0
    )
    
    # Manufacturing cost surge: above 8% yoy = high, below 0% = low
    df["mfg_fragility"] = np.clip(
        df["mfg_ppi_yoy"].fillna(0) / 10.0, 0.0, 1.0
    )
    
    # Trade balance: normalise to historical range
    if trade_best != trade_worst:
        df["trade_fragility"] = np.clip(
            1.0 - (df["trade_balance"] - trade_worst) / (trade_best - trade_worst),
            0.0, 1.0
        )
    else:
        df["trade_fragility"] = 0.5
    
    # Durable goods orders declining: yoy decline = fragility
    df["durable_yoy"] = df["durable_orders"].pct_change(4) * 100
    df["durable_fragility"] = np.clip(-df["durable_yoy"].fillna(0) / 15.0, 0.0, 1.0)
    
    # Composite
    df["fragility_score"] = (
        df["import_fragility"] * 0.30 +
        df["mfg_fragility"] * 0.25 +
        df["trade_fragility"] * 0.25 +
        df["durable_fragility"] * 0.20
    ).clip(0.0, 1.0)
    
    return df[["trade_balance", "import_px_yoy", "mfg_ppi_yoy", "fragility_score"]]
