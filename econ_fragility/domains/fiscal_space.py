"""
fiscal_space.py -- Domain 3: Fiscal Sustainability

Measures the federal government's capacity for counter-cyclical response.

Key metric: Fiscal Space Index combining debt-to-GDP, interest burden,
and deficit trajectory.

Fragility rises when interest payments consume a large share of revenue
and debt-to-GDP exceeds historical norms.
"""

import pandas as pd
import numpy as np
from ..fred_loader import load_series


def compute_index(data_dir="data/raw"):
    """Compute fiscal sustainability fragility index."""
    
    debt_gdp = load_series("GFDEGDQ188S", data_dir)   # Debt as % of GDP
    interest = load_series("A091RC1Q027SBEA", data_dir) # Interest payments (billions)
    revenue_gdp = load_series("FYFRGDA188S", data_dir)  # Revenue as % of GDP
    expenditure = load_series("W006RC1Q027SBEA", data_dir)  # Expenditures (billions)
    
    frames = {}
    for name, series in [("debt_to_gdp", debt_gdp), ("interest_payments", interest),
                          ("expenditure", expenditure)]:
        s = series.copy()
        s.index = pd.to_datetime(s.index)
        frames[name] = s.resample("QS").mean()
    
    df = pd.DataFrame(frames).dropna(how="all").ffill().dropna()
    
    # Interest as % of expenditure (proxy for interest-to-revenue)
    df["interest_burden"] = (df["interest_payments"] / df["expenditure"]) * 100
    
    # Sub-scores
    # Debt-to-GDP: above 120% = high fragility, below 60% = low
    df["debt_fragility"] = np.clip(
        (df["debt_to_gdp"] - 60.0) / (130.0 - 60.0), 0.0, 1.0
    )
    
    # Interest burden: above 20% of expenditure = high, below 8% = low
    df["interest_fragility"] = np.clip(
        (df["interest_burden"] - 8.0) / (22.0 - 8.0), 0.0, 1.0
    )
    
    # Composite
    df["fragility_score"] = (df["debt_fragility"] * 0.5 + df["interest_fragility"] * 0.5).clip(0.0, 1.0)
    
    return df[["debt_to_gdp", "interest_burden", "fragility_score"]]
