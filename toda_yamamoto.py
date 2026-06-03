"""
toda_yamamoto.py -- Integration-robust Granger causality for the CFI domains.

Addresses the editorial concern (JPKE, May 2026) that the original Granger
results rested on "a mix of levels and first-difference specifications."

The Toda-Yamamoto (1995) procedure estimates a level-VAR augmented by d_max
extra lags (d_max = maximum integration order in the system) and Wald-tests
only the first p lags of the causing variable. The resulting chi-square
inference is valid whether each series is I(0), I(1), or cointegrated, so a
single specification applies uniformly to all ordered pairs -- no levels-vs-
differences choice is made pair by pair.

Usage:
    python -m econ_fragility.toda_yamamoto         # reads data/processed/compound_fragility_index.csv
"""
import itertools
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import VAR

warnings.filterwarnings("ignore")

DOMAIN_COLS = {
    "d1_Wage-Produ": "Wage", "d2_Consumer B": "Consumer", "d3_Fiscal Sus": "Fiscal",
    "d4_Labour Mar": "Labour", "d5_Trade Arch": "Trade", "d6_Monetary C": "Monetary",
}


def integration_order(series):
    """Return 1 if the ADF test fails to reject a unit root (I(1)), else 0."""
    return 1 if adfuller(series, autolag="AIC")[1] > 0.05 else 0


def toda_yamamoto_pair(df, cause, effect, d_max, pmax=8):
    """Toda-Yamamoto Granger test that `cause` does not Granger-cause `effect`."""
    sub = df[[effect, cause]].dropna()
    try:
        p = int(VAR(sub).select_order(maxlags=pmax).aic)
    except Exception:
        p = 2
    p = max(1, min(p, pmax))
    k = p + d_max  # lag-augmented order
    d = pd.DataFrame({"y": sub[effect], "x": sub[cause]})
    ylags, xlags = [], []
    for L in range(1, k + 1):
        d[f"y{L}"] = d["y"].shift(L); ylags.append(f"y{L}")
        d[f"x{L}"] = d["x"].shift(L); xlags.append(f"x{L}")
    d = d.dropna()
    Y = d["y"].values
    Xm = sm.add_constant(d[ylags + xlags].values)
    res = sm.OLS(Y, Xm).fit()
    names = ["const"] + ylags + xlags
    # Restrict ONLY the first p lags of the causing variable to zero
    R = np.zeros((p, len(names)))
    for i, L in enumerate(range(1, p + 1)):
        R[i, names.index(f"x{L}")] = 1.0
    wald = res.wald_test(R, use_f=False)
    return p, float(np.ravel(wald.statistic)[0]), float(wald.pvalue)


def run(path="data/processed/compound_fragility_index.csv"):
    cfi = pd.read_csv(path, index_col=0, parse_dates=True)
    X = cfi[list(DOMAIN_COLS)].rename(columns=DOMAIN_COLS).dropna()
    d_max = max(integration_order(X[c]) for c in X.columns)
    rows = []
    for cause, effect in itertools.permutations(X.columns, 2):
        p, chi2, pv = toda_yamamoto_pair(X, cause, effect, d_max)
        rows.append((cause, effect, p, chi2, pv))
    out = pd.DataFrame(rows, columns=["cause", "effect", "lag_p", "chi2", "pval"])
    out = out.sort_values("pval").reset_index(drop=True)
    bonf = 0.05 / len(out)
    out["sig_05"] = out.pval < 0.05
    out["sig_10"] = out.pval < 0.10
    out["bonferroni"] = out.pval < bonf
    print(f"Toda-Yamamoto Granger | n={len(X)} | d_max={d_max} | Bonferroni alpha={bonf:.5f}")
    print(out.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\np<.05: {out.sig_05.sum()} | p<.10: {out.sig_10.sum()} | Bonferroni: {out.bonferroni.sum()}")
    return out


if __name__ == "__main__":
    run()
