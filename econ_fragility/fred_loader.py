"""
fred_loader.py -- FRED API data acquisition and caching.

Downloads all required FRED series for the Economic Fragility Simulator.

Usage:
    python -m econ_fragility.fred_loader --download-all
"""

import os
import time
import argparse
import pandas as pd

FRED_SERIES = {
    "COMPRNFB": "Real compensation per hour, nonfarm business",
    "OPHNFB": "Output per hour, nonfarm business",
    "MEHOINUSA672N": "Real median household income",
    "LES1252881600Q": "Median usual weekly real earnings",
    "PRS85006092": "Unit labour costs, nonfarm business",
    "LABSHPUSA156NRUG": "Labour share of GDP",
    "TDSP": "Household debt service ratio",
    "PSAVERT": "Personal savings rate",
    "REVOLSL": "Revolving consumer credit outstanding",
    "MORTGAGE30US": "30-year fixed mortgage rate",
    "FIXHAI": "Housing affordability index",
    "CPIAUCSL": "Consumer price index, all urban",
    "DRALACBS": "Delinquency rate, all loans",
    "DRSFRMACBS": "Delinquency rate, single-family mortgages",
    "TOTALSL": "Total consumer credit outstanding",
    "GFDEGDQ188S": "Federal debt as pct of GDP",
    "A091RC1Q027SBEA": "Federal interest payments",
    "FYFRGDA188S": "Federal receipts as pct of GDP",
    "MTSDS133FMS": "Monthly Treasury deficit/surplus",
    "FDHBFIN": "Federal debt held by foreign investors",
    "GFDEBTN": "Federal debt, total public",
    "W006RC1Q027SBEA": "Federal current expenditures",
    "CIVPART": "Civilian labour force participation rate",
    "U6RATE": "Broad unemployment rate (U-6)",
    "UNRATE": "Unemployment rate",
    "AWHNONAG": "Average weekly hours, nonfarm",
    "JTSJOL": "Job openings (JOLTS)",
    "JTSQUR": "Quits rate (JOLTS)",
    "CES0500000003": "Average hourly earnings, private",
    "LNS12032194": "Multiple jobholders, pct of employed",
    "LNU02032185": "Part-time for economic reasons",
    "BOPGSTB": "Trade balance, goods and services",
    "IR": "Import price index",
    "IQ": "Export price index",
    "DTWEXBGS": "Trade-weighted dollar index, broad",
    "PCUOMFGOMFG": "PPI, total manufacturing",
    "DGORDER": "Durable goods new orders",
    "FEDFUNDS": "Effective federal funds rate",
    "T10YIE": "10-year breakeven inflation",
    "T10Y2Y": "10yr minus 2yr Treasury spread",
    "WALCL": "Federal Reserve total assets",
    "BOGZ1FL073164003Q": "Household net worth",
    "BAMLH0A0HYM2": "High yield credit spread",
    "DCOILWTICO": "Crude oil price (WTI)",
    "VIXCLS": "CBOE Volatility Index",
}

DOMAIN_MAP = {
    1: ["COMPRNFB","OPHNFB","MEHOINUSA672N","LES1252881600Q","PRS85006092","LABSHPUSA156NRUG"],
    2: ["TDSP","PSAVERT","REVOLSL","MORTGAGE30US","FIXHAI","CPIAUCSL","DRALACBS","DRSFRMACBS","TOTALSL"],
    3: ["GFDEGDQ188S","A091RC1Q027SBEA","FYFRGDA188S","MTSDS133FMS","FDHBFIN","GFDEBTN","W006RC1Q027SBEA"],
    4: ["CIVPART","U6RATE","UNRATE","AWHNONAG","JTSJOL","JTSQUR","CES0500000003","LNS12032194","LNU02032185"],
    5: ["BOPGSTB","IR","IQ","DTWEXBGS","PCUOMFGOMFG","DGORDER"],
    6: ["FEDFUNDS","T10YIE","T10Y2Y","WALCL","BOGZ1FL073164003Q","BAMLH0A0HYM2","DCOILWTICO","VIXCLS"],
}


def download_all(api_key, output_dir="data/raw"):
    from fredapi import Fred
    fred = Fred(api_key=api_key)
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    for sid, desc in FRED_SERIES.items():
        csv_path = os.path.join(output_dir, f"{sid}.csv")
        if os.path.exists(csv_path):
            print(f"  [cached] {sid}: {desc}")
            results[sid] = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            continue
        for attempt in range(3):
            try:
                data = fred.get_series(sid)
                data.to_csv(csv_path, header=[sid])
                results[sid] = data
                print(f"  [downloaded] {sid}: {desc}")
                break
            except Exception as e:
                if attempt < 2 and "Internal Server Error" in str(e):
                    time.sleep(2 ** attempt)
                    continue
                print(f"  [ERROR] {sid}: {e}")
    print(f"\nDownloaded {len(results)}/{len(FRED_SERIES)} series to {output_dir}")
    return results


def load_series(series_id, data_dir="data/raw"):
    csv_path = os.path.join(data_dir, f"{series_id}.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found. Run --download-all first.")
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    return df.iloc[:, 0]


def load_domain(domain_num, data_dir="data/raw"):
    series_ids = DOMAIN_MAP.get(domain_num, [])
    return {sid: load_series(sid, data_dir) for sid in series_ids}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-all", action="store_true")
    parser.add_argument("--api-key", default=os.environ.get("FRED_API_KEY"))
    parser.add_argument("--output", default="data/raw")
    args = parser.parse_args()
    if not args.api_key:
        print("ERROR: Set FRED_API_KEY or use --api-key")
        exit(1)
    if args.download_all:
        download_all(args.api_key, args.output)
