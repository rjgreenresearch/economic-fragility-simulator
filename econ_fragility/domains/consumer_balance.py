"""
consumer_balance.py -- Domain 2: Consumer Balance Sheet

Measures household financial resilience -- the capacity to absorb
shocks (job loss, medical event, rate increase) without default.

Key metric: Consumer Resilience Index (CRI) combining savings rate,
debt service ratio, and delinquency trends.

Fragility rises when savings approach zero, debt service rises,
and delinquency rates increase simultaneously.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw"):
    """Compute consumer balance sheet fragility index."""
    
    # Load core series
    savings = load_series("PSAVERT", data_dir)        # Personal savings rate
    debt_svc = load_series("TDSP", data_dir)           # Debt service ratio
    delinq = load_series("DRALACBS", data_dir)         # Delinquency rate, all loans
    cpi = load_series("CPIAUCSL", data_dir)            # CPI for inflation context
    revolving = load_series("REVOLSL", data_dir)       # Revolving credit
    mortgage = load_series("MORTGAGE30US", data_dir)   # 30yr mortgage rate
    
    # Build quarterly DataFrame
    frames = {}
    for name, series in [("savings_rate", savings), ("debt_service", debt_svc),
                          ("delinquency", delinq), ("revolving_credit", revolving),
                          ("mortgage_rate", mortgage)]:
        s = series.copy()
        s.index = pd.to_datetime(s.index)
        frames[name] = s.resample("QS").mean()
    
    df = pd.DataFrame(frames).dropna(how="all")
    # Forward-fill for series with different start dates
    df = df.ffill().dropna()
    
    # Sub-scores (each 0-1, higher = more fragile)
    
    # Savings: below 3% = high fragility, above 10% = low fragility
    df["savings_fragility"] = np.clip(
        1.0 - (df["savings_rate"] - 2.0) / (10.0 - 2.0), 0.0, 1.0
    )
    
    # Debt service: above 13% = high fragility, below 9% = low fragility
    df["debt_fragility"] = np.clip(
        (df["debt_service"] - 9.0) / (14.0 - 9.0), 0.0, 1.0
    )
    
    # Delinquency: above 5% = high fragility, below 2% = low fragility
    df["delinq_fragility"] = np.clip(
        (df["delinquency"] - 2.0) / (5.0 - 2.0), 0.0, 1.0
    )
    
    # Mortgage rate stress: above 7% = high, below 4% = low
    df["mortgage_fragility"] = np.clip(
        (df["mortgage_rate"] - 4.0) / (8.0 - 4.0), 0.0, 1.0
    )
    
    # Composite: geometric mean of sub-scores
    components = ["savings_fragility", "debt_fragility", "delinq_fragility", "mortgage_fragility"]
    df["fragility_score"] = df[components].apply(
        lambda row: np.exp(np.mean(np.log(row.clip(0.01)))), axis=1
    ).clip(0.0, 1.0)
    
    return df[["savings_rate", "debt_service", "delinquency", "mortgage_rate", "fragility_score"]]
