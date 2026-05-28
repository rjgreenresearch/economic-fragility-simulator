# Economic Fragility Simulator

**Compound Domestic Resilience Analysis Using Federal Reserve Economic Data**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![FRED Series: 45](https://img.shields.io/badge/FRED%20series-45-blue.svg)](https://fred.stlouisfed.org/)
[![Domains: 6](https://img.shields.io/badge/domains-6-orange.svg)]()
[![Scenarios: 4](https://img.shields.io/badge/scenarios-4-brightgreen.svg)]()

The Economic Fragility Simulator applies the Mutual Threshold Saturation (MTS) framework to the U.S. domestic economy. It measures compound vulnerability across six interacting economic domains using Federal Reserve Economic Data (FRED), computes a Compound Fragility Index (CFI) that rises multiplicatively when domains are simultaneously stressed, and models four parameterised stress scenarios calibrated to April 2026 real-world data.

**Author:** Robert J. Green · [robert@rjgreenresearch.org](mailto:robert@rjgreenresearch.org) · [ORCID: 0009-0002-9097-1021](https://orcid.org/0009-0002-9097-1021) · [www.rjgreenresearch.org](https://www.rjgreenresearch.org)

---

## Why This Tool Exists

Standard macroeconomic analysis examines individual indicators in isolation: the unemployment rate, the debt-to-GDP ratio, the savings rate. This approach misses the compound interaction that makes economic crises catastrophic. The 2008 financial crisis was not caused by the housing market alone — it was caused by the simultaneous stress of mortgage defaults, credit market seizure, consumer balance sheet collapse, and the exhaustion of monetary policy space all happening at once. Each domain individually looked manageable. The compound interaction was not.

The MTS framework, developed across a companion research programme on material supply chains, human capital dependencies, and warfare economics, argues that compound vulnerabilities interact multiplicatively rather than additively. When six economic domains are each partially stressed, the system as a whole may be near a threshold where a single-domain shock cascades through all others because absorptive capacity in each domain has been independently depleted.

This simulator operationalises that framework using the most rigorous public economic dataset available: 45 time series from the Federal Reserve Economic Database covering U.S. economic conditions from 1947 to the present.

---

## How This Tool Supports the Research

The Economic Fragility Simulator is the primary computational instrument for Paper 7 of the MTS research programme: *"Compound Economic Fragility: A Mutual Threshold Saturation Analysis of U.S. Domestic Resilience."*

Every empirical finding in that paper — the current CFI of 0.131, the domain-level scores, the historical comparison to GFC and COVID, the scenario projections — is produced by this tool running against federal primary-source FRED data. The results are fully reproducible (see [Reproducing the Paper's Results](#reproducing-the-papers-results) below).

**The central finding:** The U.S. economy is not near collapse — but not because the structural problems are not real. The wage-productivity gap (Domain 1: 0.801) and fiscal sustainability (Domain 3: 0.947) are both critical. The system retains resilience because the transmission domains (Consumer Balance Sheet: 0.211; Labour Market: 0.294) still have absorptive capacity. The danger scenario is compound stress that exhausts those transmission domains simultaneously — tariffs hitting consumer purchasing power while AI displacement hits labour income — at which point the fiscal domain, already at 0.947, has no remaining counter-cyclical capacity to buffer the cascade. The COVID response proved this mechanism: stimulus cheques pushed consumer fragility to 0.02, absorbing the cascade. That move is no longer available.

**Companion papers:**
- Green, R.J. (2026d). "Mapping Critical Supply Chain Dependencies Affecting the United States." [SSRN](https://doi.org/10.2139/ssrn.6454618).
- Green, R.J. (2026e). "Human Capital Threshold Saturation." Working Paper.
- Green, R.J. (2026f). "The Cost Curve as Deterrent: Compound Warfare Economics." Working Paper.
- Green, R.J. (2026g). "Compound Economic Fragility: A Mutual Threshold Saturation Analysis of U.S. Domestic Resilience." Working Paper (target: *Journal of Post-Keynesian Economics*).

---

## What It Does

| Capability | Description |
|-----------|-------------|
| **FRED Data Acquisition** | Downloads and caches all 45 required time series via FRED API; no data files included in repository |
| **Domain 1: Wage-Productivity Gap** | Wage-Productivity Ratio (COMPRNFB/OPHNFB indexed to 1973=1.00); labour share of GDP validation |
| **Domain 2: Consumer Balance Sheet** | Composite of savings rate, debt service ratio, delinquency rates, mortgage rate stress |
| **Domain 3: Fiscal Sustainability** | Debt-to-GDP, interest burden as % of expenditure, deficit trajectory |
| **Domain 4: Labour Market Transformation** | Participation rate, U-6 broad unemployment, average weekly hours, involuntary part-time |
| **Domain 5: Trade Architecture Stress** | Import price YoY change, manufacturing PPI, trade balance trajectory, durable goods orders |
| **Domain 6: Monetary Policy Constraint** | Fed funds rate space, yield curve slope, Fed balance sheet capacity, VIX stress |
| **Compound Fragility Index** | CFI = product of (1 + D_k × w_k) for k=1..6; normalised 0–1 against theoretical maximum |
| **Historical Benchmarking** | Full time series from 2000; comparison to pre-GFC (0.061), GFC (0.155), COVID (0.125) |
| **Scenario Engine** | Four parameterised stress scenarios with domain shocks, cascade amplifiers, and quarterly time paths |
| **Scenario 1: Tariff Cascade** | 10–15% across-the-board tariff; $940–$1,500/household income loss; +0.089 CFI at peak |
| **Scenario 2: AI Displacement Wave** | Goldman Sachs 6–7% workforce displacement (~11M); retraining gap; +0.083 CFI at peak |
| **Scenario 3: Fiscal Constraint** | Debt/GDP reaches 110%; interest crowds out counter-cyclical capacity; +0.046 CFI at peak |
| **Scenario 4: Compound Stress** | Simultaneous tariff + energy + monetary paralysis + labour cooling; +0.113 CFI at peak |

---

## Quick Start

### Installation

```bash
git clone https://github.com/rjgreenresearch/economic-fragility-simulator.git
cd economic-fragility-simulator
pip install -e .

# Or with full dependencies
pip install -r requirements.txt
```

Requires Python 3.10+.

### FRED API Key

All data is sourced from the Federal Reserve Economic Database (FRED). A free API key is required:

1. Register at [research.stlouisfed.org/useraccount/apikeys](https://research.stlouisfed.org/useraccount/apikeys)
2. Set the environment variable:

```bash
export FRED_API_KEY=your_key_here          # macOS/Linux
set FRED_API_KEY=your_key_here             # Windows
```

### Download Data

```bash
# Download all 45 FRED series (one-time; cached locally after first run)
python -m econ_fragility.fred_loader --download-all

# Output: data/raw/<SERIES_ID>.csv for each of the 45 series
```

### Run Full Analysis

```bash
# Baseline analysis + all four scenarios
python -m econ_fragility

# Baseline analysis only (no scenarios)
python -m econ_fragility --no-scenarios

# Single domain
python -m econ_fragility --domain 3

# Single scenario
python -m econ_fragility --scenario compound_stress

# Custom output directory
python -m econ_fragility --output results/
```

### Expected Output (April 2026 Data)

```
COMPOUND FRAGILITY INDEX — LATEST VALUES
================================================================
  Date: 2026-04-01
  Compound CFI (normalised 0-1): 0.131

  Wage-Produ     0.801  |################################
  Consumer B     0.211  |########
  Fiscal Sus     0.947  |#####################################
  Labour Mar     0.294  |###########
  Trade Arch     0.274  |##########
  Monetary C     0.501  |####################

  Assessment: RESILIENT — absorptive capacity adequate

SCENARIO ANALYSIS — COMPOUND FRAGILITY INDEX PROJECTIONS
  Baseline CFI (current): 0.131
================================================================
  Scenario                      Q4      Q8    Peak   Assessment at Peak
  Tariff Cascade              0.218   0.220   0.220  CRITICAL
  AI Displacement Wave        0.196   0.214   0.214  CRITICAL
  Fiscal Constraint           0.169   0.176   0.177  SEVERE
  Compound Stress/Stagflation 0.242   0.244   0.244  CRITICAL
================================================================
```

---

## The Compound Fragility Finding

The CFI is calibrated against historical episodes:

| Period | CFI | Interpretation |
|--------|-----|---------------|
| Pre-GFC (2007) | 0.061 | All domains moderate. System had full absorptive capacity. |
| GFC (2009) | 0.155 | All six domains stressed simultaneously. Compound cascade. |
| Post-GFC peak (2011) | 0.175 | Highest recorded. Slow multi-domain recovery. |
| COVID (2020) | 0.125 | Fiscal (0.97) maxed; consumer at 0.02 due to stimulus. System absorbed cascade. |
| **Current (April 2026)** | **0.131** | Two domains critical; four provide cushion. **Fiscal buffer exhausted.** |

The critical insight: COVID was survived because the government could borrow $5 trillion in stimulus, pushing consumer fragility to near zero. At fiscal fragility of 0.947, that move is no longer available. The next compound shock will arrive in a system with no fiscal buffer.

---

## FRED Data Series

All 45 series download automatically. Register for a free API key at research.stlouisfed.org.

| Domain | Series | Description |
|--------|--------|-------------|
| **1. Wage-Productivity** | COMPRNFB | Real compensation per hour, nonfarm business (1947–) |
| | OPHNFB | Output per hour, nonfarm business (1947–) |
| | MEHOINUSA672N | Real median household income (1984–) |
| | LES1252881600Q | Median usual weekly real earnings (1979–) |
| | PRS85006092 | Unit labour costs, nonfarm business (1947–) |
| | LABSHPUSA156NRUG | Labour share of GDP (1950–) |
| **2. Consumer Balance** | TDSP | Household debt service ratio (1980–) |
| | PSAVERT | Personal savings rate (1959–) |
| | REVOLSL | Revolving consumer credit outstanding (1968–) |
| | MORTGAGE30US | 30-year fixed mortgage rate (1971–) |
| | FIXHAI | Housing affordability index (2025–) |
| | CPIAUCSL | Consumer price index, all urban (1947–) |
| | DRALACBS | Delinquency rate, all loans (1985–) |
| | DRSFRMACBS | Delinquency rate, single-family mortgages (1991–) |
| | TOTALSL | Total consumer credit outstanding (1943–) |
| **3. Fiscal Space** | GFDEGDQ188S | Federal debt as % of GDP (1966–) |
| | A091RC1Q027SBEA | Federal government interest payments (1947–) |
| | FYFRGDA188S | Federal receipts as % of GDP (1929–) |
| | MTSDS133FMS | Monthly Treasury deficit/surplus (1981–) |
| | FDHBFIN | Federal debt held by foreign investors (1970–) |
| | GFDEBTN | Federal debt, total public (1966–) |
| | W006RC1Q027SBEA | Federal government current expenditures (1947–) |
| **4. Labour Market** | CIVPART | Civilian labour force participation rate (1948–) |
| | U6RATE | Broad unemployment rate U-6 (1994–) |
| | UNRATE | Unemployment rate (1948–) |
| | AWHNONAG | Average weekly hours, nonfarm (1964–) |
| | JTSJOL | Job openings (JOLTS) (2000–) |
| | JTSQUR | Quits rate (JOLTS) (2000–) |
| | CES0500000003 | Average hourly earnings, private sector (2006–) |
| | LNS12032194 | Multiple jobholders as % of employed (1955–) |
| | LNU02032185 | Part-time for economic reasons (1948–) |
| **5. Trade Architecture** | BOPGSTB | Trade balance, goods and services (1992–) |
| | IR | Import price index (1982–) |
| | IQ | Export price index (1983–) |
| | DTWEXBGS | Trade-weighted US dollar index, broad (2006–) |
| | PCUOMFGOMFG | PPI: total manufacturing (1984–) |
| | DGORDER | Manufacturers' new orders, durable goods (1958–) |
| **6. Monetary Constraint** | FEDFUNDS | Effective federal funds rate (1954–) |
| | T10YIE | 10-year breakeven inflation rate (2003–) |
| | T10Y2Y | 10-year minus 2-year Treasury spread (1976–) |
| | WALCL | Federal Reserve total assets (2002–) |
| | BOGZ1FL073164003Q | Household net worth (1945–) |
| | BAMLH0A0HYM2 | ICE BofA high yield credit spread (2023–) |
| | DCOILWTICO | Crude oil price, WTI (1986–) |
| | VIXCLS | CBOE Volatility Index (1990–) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Economic Fragility Simulator Pipeline              │
│                                                                 │
│  ┌──────────┐   ┌──────────────────────────────────────────┐   │
│  │   FRED   │   │              Domain Modules               │   │
│  │   API    │──▶│  ┌──────────┐  ┌──────────┐  ┌────────┐ │   │
│  │  Loader  │   │  │ Domain 1 │  │ Domain 2 │  │  ...   │ │   │
│  │  + Cache │   │  │  Wage-   │  │Consumer  │  │        │ │   │
│  └──────────┘   │  │  Prod.   │  │ Balance  │  │  D3-D6 │ │   │
│                 │  └────┬─────┘  └────┬─────┘  └───┬────┘ │   │
│                 └───────┼─────────────┼─────────────┼──────┘   │
│                         │             │             │           │
│                         ▼             ▼             ▼           │
│                 ┌──────────────────────────────────────────┐   │
│                 │         Normalisation Engine             │   │
│                 │  Each domain → fragility score 0.0–1.0   │   │
│                 │  0.0 = fully resilient                    │   │
│                 │  1.0 = at threshold                       │   │
│                 └───────────────────┬──────────────────────┘   │
│                                     │                           │
│                                     ▼                           │
│                 ┌──────────────────────────────────────────┐   │
│                 │         Compound Index (CFI)             │   │
│                 │                                           │   │
│                 │  CFI = ∏(1 + D_k × w_k)  for k=1..6     │   │
│                 │                                           │   │
│                 │  Domain interaction weights:              │   │
│                 │  D1(1.0) D2(1.2) D3(1.1)                 │   │
│                 │  D4(1.2) D5(1.0) D6(1.3)                 │   │
│                 │                                           │   │
│                 │  Normalised CFI: (raw-1)/(max-1)          │   │
│                 └───────────────────┬──────────────────────┘   │
│                                     │                           │
│                         ┌───────────┴────────────┐             │
│                         ▼                        ▼             │
│              ┌───────────────────┐   ┌───────────────────────┐ │
│              │  Baseline Output  │   │    Scenario Engine    │ │
│              │                   │   │                       │ │
│              │  • Historical CFI │   │  1. Tariff Cascade    │ │
│              │  • Domain scores  │   │  2. AI Displacement   │ │
│              │  • CSV time series│   │  3. Fiscal Constraint │ │
│              │  • Assessment     │   │  4. Compound Stress   │ │
│              └───────────────────┘   │                       │ │
│                                      │  Each scenario:        │ │
│                                      │  • Domain shocks       │ │
│                                      │  • Ramp paths          │ │
│                                      │  • Cascade amplifiers  │ │
│                                      │  • Quarterly time path │ │
│                                      └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Module Reference

| Module | Lines | Purpose |
|--------|-------|---------|
| **Data Acquisition** | | |
| `fred_loader.py` | 123 | FRED API client; downloads and caches all 45 series; domain mapping; CLI interface |
| **Domain Modules** | | |
| `domains/wage_productivity.py` | 76 | Wage-Productivity Ratio indexed to 1973=1.00; labour share validation |
| `domains/consumer_balance.py` | 71 | Composite savings/debt-service/delinquency/mortgage fragility |
| `domains/fiscal_space.py` | 52 | Debt-to-GDP and interest burden fragility |
| `domains/labour_market.py` | 69 | Participation, U-6, weekly hours, involuntary part-time |
| `domains/trade_cascade.py` | 76 | Import prices YoY, manufacturing PPI, trade balance trajectory |
| `domains/monetary_constraint.py` | 74 | Rate cutting room, yield curve, Fed balance sheet, VIX |
| **Index & Scenarios** | | |
| `compound_index.py` | 145 | CFI computation, domain alignment, historical normalisation, summary output |
| `scenarios.py` | 400 | Four parameterised stress scenarios with sourced calibration, cascade amplifiers, quarterly time paths |
| `__main__.py` | 122 | CLI entry point; wires data → domains → CFI → scenarios → output |

---

## Scenario Engine

Each scenario defines domain shocks (additive increments to baseline scores), ramp paths (how fast each domain is stressed), and cascade amplifiers (domain-to-domain interaction multipliers). All parameters are calibrated to April 2026 sourced data.

### Scenario 1: Tariff Cascade

Section 122 10% across-the-board tariff persists and escalates to 15%. Import prices surge, manufacturing contracts, consumer prices rise ~1.1% (Yale Budget Lab, April 8 2026). Agriculture exports collapse (soybeans –78%, corn –99% to China). Trade stress cascades into consumer balance and labour market as margin compression triggers layoffs.

| Domain | Shock | Ramp | Source |
|--------|-------|------|--------|
| Trade Architecture (5) | +0.25 | 2Q | Yale Budget Lab; PWBM April 15 2026 |
| Consumer Balance (2) | +0.12 | 4Q | Yale: $940–$1,500/household income loss |
| Labour Market (4) | +0.10 | 4Q | Axios: 89,000 mfg jobs lost post-Liberation Day |
| Monetary Constraint (6) | +0.08 | 2Q | Goldman Sachs: 72% tariff pass-through to CPI |
| Fiscal Sustainability (3) | +0.03 | 6Q | Deficit widens despite tariff revenue |

Peak CFI: **0.220** (+0.089 vs baseline). Exceeds GFC peak (0.175) by Q4.

### Scenario 2: AI Displacement Wave

Accelerating AI adoption displaces 6–7% of the U.S. workforce (~11 million workers) over 8 quarters (Goldman Sachs Research). Entry-level hiring collapses first — workers aged 22–25 in AI-exposed roles saw a 16% employment decline through September 2025. Retraining pipeline (WIOA $2.919B, 2–4 year degree cycle) cannot absorb displacement rate.

| Domain | Shock | Ramp | Source |
|--------|-------|------|--------|
| Labour Market (4) | +0.22 | 4Q | Goldman Sachs: 6–7% workforce, 10-year horizon |
| Consumer Balance (2) | +0.15 | 6Q | Income loss → savings drawdown → delinquency |
| Wage-Productivity (1) | +0.08 | 8Q | Labour surplus suppresses compensation further |
| Fiscal Sustainability (3) | +0.06 | 8Q | Reduced payroll tax; increased safety net spending |

Peak CFI: **0.214** (+0.083 vs baseline). Exceeds GFC peak by Q8.

### Scenario 3: Fiscal Constraint

Federal debt/GDP reaches 110% (CBO projects 120% by 2036). At $1T+ in annual interest payments — Q1 FY2026: $270.3B vs $266.9B defense, first time interest exceeded defense since FY2024 — the government cannot mount a counter-cyclical fiscal response when recession arrives. Bond market pressure forces higher rates, creating a debt-service spiral: each additional 1 percentage point in rates adds $320B/year in interest (CBO).

| Domain | Shock | Ramp | Source |
|--------|-------|------|--------|
| Monetary Constraint (6) | +0.12 | 3Q | Bond market repricing as debt/GDP rises |
| Consumer Balance (2) | +0.08 | 6Q | Austerity cuts transfer payments, raises costs |
| Labour Market (4) | +0.06 | 4Q | Federal employment contraction (DOGE-style cuts) |
| Fiscal Sustainability (3) | +0.04 | 1Q | Already at 0.947; shock closes remaining buffer |

Peak CFI: **0.177** (+0.046 vs baseline). Reaches GFC-equivalent level.

### Scenario 4: Compound Stress / Stagflation

Simultaneous shocks across all six domains. Fed holds at 3.50–3.75% (March 2026 FOMC), unable to cut (3.3% CPI) or raise (1.2% GDP growth, Q1 2026 GDPNow). Iran war (commenced February 28, 2026) drives gasoline up 21.2% in March — the proximate cause of the 0.9% monthly CPI surge. NY Fed recession probability: 25%; Moody's AI model: 49%.

| Domain | Shock | Ramp | Source |
|--------|-------|------|--------|
| Trade Architecture (5) | +0.20 | 1Q | Iran war oil spike + tariff cascade, already in data |
| Monetary Constraint (6) | +0.18 | 2Q | Fed paralysed by dual-mandate conflict |
| Consumer Balance (2) | +0.14 | 3Q | Energy + tariffs + rate freeze hit household balance |
| Labour Market (4) | +0.12 | 3Q | Feb –133K payrolls; rising long-term unemployment |
| Fiscal Sustainability (3) | +0.04 | 4Q | Automatic stabilisers widen deficit |

Peak CFI: **0.244** (+0.113 vs baseline). CRITICAL within Q1. Highest projected outcome across all scenarios.

---

## Domain Interaction Matrix

The compound fragility thesis rests on domain interactions being multiplicative, not additive. These are the primary cascade pathways modelled in the scenario engine:

| Stress in... | Amplifies... | Mechanism |
|-------------|-------------|-----------|
| Wage-Productivity (1) | Consumer Balance (2) | Stagnant wages force credit-financed consumption |
| Consumer Balance (2) | Fiscal Space (3) | Consumer defaults reduce tax revenue, increase safety net costs |
| Fiscal Space (3) | Monetary Constraint (6) | High debt constrains fiscal response, shifts burden to Fed |
| Fiscal Space (3) | Monetary Constraint (6) | Bond market forces higher rates; debt-service spiral |
| Labour Market (4) | Wage-Productivity (1) | AI displacement suppresses wages through surplus labour |
| Labour Market (4) | Consumer Balance (2) | Job loss triggers savings drawdown and default cascades |
| Trade Architecture (5) | Consumer Balance (2) | Higher import prices reduce purchasing power |
| Trade Architecture (5) | Labour Market (4) | Manufacturing contraction triggers layoffs |
| Monetary Constraint (6) | Consumer Balance (2) | Rate increases raise mortgage and credit card costs |
| Monetary Constraint (6) | Fiscal Space (3) | Rate increases raise federal debt service costs |

---

## Known Limitations

This simulator is a research instrument. These limitations are documented because transparency about boundaries increases credibility.

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| **FRED series coverage varies** | FIXHAI (housing affordability) has only 13 values (2025–present); BAMLH0A0HYM2 starts 2023. Sparse series reduce domain precision. | Consumer domain uses four sub-scores; sparse series fall back to forward-fill from nearest available. Domain scores carry implicit coverage annotation. |
| **Quarterly normalisation loses intra-quarter dynamics** | Monthly or daily series are aggregated to quarterly means, losing information about intra-quarter volatility spikes | For high-frequency analysis, domain modules can be called directly without resampling |
| **Fragility threshold calibration is theory-driven** | The min/max bounds for normalising domain scores (e.g., savings rate: 2–10%) are calibrated to historical norms and theoretical priors, not estimated from data | All threshold parameters are documented inline in each domain module and are configurable |
| **Interaction weights are fixed** | The domain interaction matrix uses fixed weights (1.0–1.3); cross-domain amplification is not empirically estimated | Weights can be overridden via the `weights` parameter in `compute_cfi()`; Granger causality tests are a planned extension |
| **Scenario shocks are additive to baseline** | Scenarios add incremental domain shocks to the current baseline; they do not recompute the full FRED time series | This is intentional — the scenario engine models forward-looking stress from the current state, not a historical backtest |
| **Compound index is unit-free** | The normalised CFI (0–1) is calibrated to historical range, not a probability or economic loss measure | The CFI is explicitly labelled as a fragility index, not a recession probability. Recession probability comparison is for interpretive context only. |
| **AI displacement parameterisation is projection-based** | The AI displacement scenario draws on Goldman Sachs/McKinsey projections, not observed labour data | Scenario parameters are fully documented and sourced; users can override domain shock magnitudes |

---

## Reproducing the Paper's Results

To reproduce the findings in Green (2026g), *"Compound Economic Fragility: A Mutual Threshold Saturation Analysis of U.S. Domestic Resilience"*:

### Step 1: Download Data

```bash
export FRED_API_KEY=your_key
python -m econ_fragility.fred_loader --download-all
# Expected: 45 CSV files in data/raw/
```

### Step 2: Run Baseline Analysis

```bash
python -m econ_fragility --no-scenarios --output data/processed/
# Expected outputs:
#   domain_1_wage_productivity_gap.csv    (316 quarterly observations)
#   domain_2_consumer_balance_sheet.csv   (86 quarterly observations)
#   domain_3_fiscal_sustainability.csv    (240 quarterly observations)
#   domain_4_labour_market.csv            (129 quarterly observations)
#   domain_5_trade_architecture.csv       (137 quarterly observations)
#   domain_6_monetary_constraint.csv      (95 quarterly observations)
#   compound_fragility_index.csv          (CFI from 2000-01-01)
```

### Step 3: Verify Key Findings

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/processed/compound_fragility_index.csv', index_col=0, parse_dates=True)
latest = df.iloc[-1]
print(f'Current CFI: {latest[\"CFI_normalised\"]:.3f}')         # Expected: ~0.131
print(f'Fiscal domain: {latest[\"d3_Fiscal Sus\"]:.3f}')        # Expected: ~0.947
print(f'Wage domain: {latest[\"d1_Wage-Produ\"]:.3f}')          # Expected: ~0.801
peak = df['CFI_normalised'].max()
peak_date = df['CFI_normalised'].idxmax()
print(f'Historical peak: {peak:.3f} ({peak_date.strftime(\"%Y-%m\")})')  # Expected: ~0.175 (2011)
"
```

### Step 4: Run Scenario Analysis

```bash
python -m econ_fragility --scenarios-dir data/scenarios/
# Expected: four CSV files in data/scenarios/
#   scenario_tariff_cascade.csv       (peak CFI ~0.220)
#   scenario_ai_displacement.csv      (peak CFI ~0.214)
#   scenario_fiscal_constraint.csv    (peak CFI ~0.177)
#   scenario_compound_stress.csv      (peak CFI ~0.244)
```

### Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--data-dir` | `data/raw` | Directory containing FRED CSV files |
| `--output` | `data/processed` | Directory for domain and CFI output |
| `--scenarios-dir` | `data/scenarios` | Directory for scenario output |
| `--start` | `2000-01-01` | Start date for CFI computation |
| `--domain` | (all) | Compute single domain only (1–6) |
| `--scenario` | (all) | Run single scenario only |
| `--no-scenarios` | False | Skip scenario analysis |

---

## Data Sources

All data is sourced from publicly available U.S. government databases. No data files are included in this repository. Users download directly from authoritative sources.

| Data | Source | URL | API Key |
|------|--------|-----|---------|
| All 45 FRED series | Federal Reserve Bank of St. Louis | fred.stlouisfed.org | Free registration required |

**Note on FRED API access:** Registration is free at research.stlouisfed.org/useraccount/apikeys. The API supports up to 120 requests per minute. All 45 series download in under two minutes on a standard connection and are cached locally for all subsequent runs.

---

## Citation

If you use the Economic Fragility Simulator in research, policy analysis, or publications, please cite:

```bibtex
@software{green_econ_fragility_2026,
  author       = {Green, Robert J.},
  title        = {{Economic Fragility Simulator}: {MTS} Pillar 4 — Compound Domestic Resilience Analysis},
  version      = {0.1.0},
  year         = {2026},
  url          = {https://github.com/rjgreenresearch/economic-fragility-simulator},
  license      = {Apache-2.0}
}
```

And the companion working paper:

```bibtex
@unpublished{green_compound_fragility_2026,
  author = {Green, Robert J.},
  title  = {Compound Economic Fragility: {A} Mutual Threshold Saturation Analysis of {U.S.} Domestic Resilience},
  year   = {2026},
  note   = {Working paper, target: \textit{Journal of Post-Keynesian Economics}}
}
```

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

---

## Research Context

The Economic Fragility Simulator is Pillar 4 of the Mutual Threshold Saturation (MTS) research programme:

| Pillar | Paper | Domain | Simulator |
|--------|-------|--------|-----------|
| 1 | Paper 4 (MTS Supply Chain) | Material dependencies | [mts-doctrine-simulator](https://github.com/rjgreenresearch/mts-doctrine-simulator) |
| 2 | Paper 5 (HCTS) | Human capital key-person dependencies | [hcts-simulator](https://github.com/rjgreenresearch/hcts-simulator) |
| 3 | Paper 6 (Cost Asymmetry) | Compound warfare economics | [cost-asymmetry-simulator](https://github.com/rjgreenresearch/cost-asymmetry-simulator) |
| **4** | **Paper 7 (This paper)** | **Compound domestic economic resilience** | **economic-fragility-simulator** |
| 5 | Paper 8 (Aquifer Depletion) | Irreversible natural resource depletion | [aquifer-depletion-simulator](https://github.com/rjgreenresearch/aquifer-depletion-simulator) |

The research programme spans national security economics (Papers 1–3: foreign agricultural land surveillance), strategic studies (Papers 4–6: supply chains, human capital, warfare costs), and political economy (Papers 7–8: domestic economic fragility and natural resource depletion). The connecting thesis is that compound threshold saturation — the condition in which simultaneous stress across multiple domains exhausts absorptive capacity multiplicatively — is the structural mechanism underlying both economic crises and national security failures.

---

## License

Apache 2.0. See [LICENSE](LICENSE) for full terms.

Government agencies may use, modify, and distribute this software without fee under the terms of the Apache 2.0 license.
