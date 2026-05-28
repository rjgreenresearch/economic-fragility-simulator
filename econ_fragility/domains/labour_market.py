"""
labour_market.py -- Domain 4: Labour Market Structural Transformation

Measures the labour market's capacity to absorb shocks, including
AI displacement, gig economy growth, and participation decline.

Key metric: Labour Market Absorption Capacity (LMAC) combining
participation rate, broad unemployment, involuntary part-time,
and multiple jobholder rates.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw"):
    """Compute labour market fragility index."""
    
    participation = load_series("CIVPART", data_dir)
    u6 = load_series("U6RATE", data_dir)
    unrate = load_series("UNRATE", data_dir)
    hours = load_series("AWHNONAG", data_dir)
    part_time = load_series("LNU02032185", data_dir)  # Part-time for econ reasons (thousands)
    
    frames = {}
    for name, series in [("participation", participation), ("u6", u6),
                          ("unemployment", unrate), ("weekly_hours", hours),
                          ("part_time_econ", part_time)]:
        s = series.copy()
        s.index = pd.to_datetime(s.index)
        frames[name] = s.resample("QS").mean()
    
    df = pd.DataFrame(frames).dropna(how="all").ffill().dropna()
    
    # Participation: below 60% = high fragility, above 66% = low
    df["participation_fragility"] = np.clip(
        1.0 - (df["participation"] - 58.0) / (67.0 - 58.0), 0.0, 1.0
    )
    
    # U-6 broad unemployment: above 12% = high, below 7% = low
    if "u6" in df.columns and df["u6"].notna().any():
        df["u6_fragility"] = np.clip(
            (df["u6"] - 7.0) / (15.0 - 7.0), 0.0, 1.0
        )
    else:
        df["u6_fragility"] = np.clip(
            (df["unemployment"] - 4.0) / (10.0 - 4.0), 0.0, 1.0
        )
    
    # Weekly hours declining: below 33.5 = high, above 34.5 = low
    df["hours_fragility"] = np.clip(
        1.0 - (df["weekly_hours"] - 33.0) / (35.0 - 33.0), 0.0, 1.0
    )
    
    # Involuntary part-time: above 6000 (thousands) = high, below 3000 = low
    df["parttime_fragility"] = np.clip(
        (df["part_time_econ"] - 3000) / (7000 - 3000), 0.0, 1.0
    )
    
    # Composite: weighted average
    df["fragility_score"] = (
        df["participation_fragility"] * 0.30 +
        df["u6_fragility"] * 0.30 +
        df["hours_fragility"] * 0.15 +
        df["parttime_fragility"] * 0.25
    ).clip(0.0, 1.0)
    
    return df[["participation", "u6", "weekly_hours", "part_time_econ", "fragility_score"]]
