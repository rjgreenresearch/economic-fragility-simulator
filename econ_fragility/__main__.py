"""
Main entry point for the Economic Fragility Simulator.

Usage:
    python -m econ_fragility                        # Full analysis + scenarios + figures
    python -m econ_fragility --no-scenarios         # Baseline only
    python -m econ_fragility --no-figures           # Skip figure generation
    python -m econ_fragility --interactions         # Run interaction analysis
    python -m econ_fragility --scenario tariff_cascade
    python -m econ_fragility --domain 1
"""

import os, sys, argparse

from .compound_index import (
    compute_all_domains, compute_cfi, print_summary, DOMAIN_MODULES, DOMAIN_NAMES
)
from .scenarios import (
    run_scenario, run_all_scenarios, print_scenario_summary, SCENARIO_PARAMS
)


def main():
    parser = argparse.ArgumentParser(description="Economic Fragility Simulator")
    parser.add_argument("--data-dir",       default="data/raw")
    parser.add_argument("--output",         default="data/processed")
    parser.add_argument("--scenarios-dir",  default="data/scenarios")
    parser.add_argument("--figures-dir",    default="figures")
    parser.add_argument("--start",          default="2000-01-01")
    parser.add_argument("--domain",         type=int)
    parser.add_argument("--scenario",       help=f"One of: {list(SCENARIO_PARAMS.keys())}")
    parser.add_argument("--no-scenarios",   action="store_true")
    parser.add_argument("--no-figures",     action="store_true")
    parser.add_argument("--interactions",   action="store_true",
                        help="Run Granger causality and cross-correlation analysis")
    args = parser.parse_args()

    os.makedirs(args.output,        exist_ok=True)
    os.makedirs(args.scenarios_dir, exist_ok=True)

    # --- Single domain ---
    if args.domain:
        if args.domain not in DOMAIN_MODULES:
            print(f"Invalid domain. Valid: 1-6"); sys.exit(1)
        name = DOMAIN_NAMES[args.domain]
        print(f"Computing Domain {args.domain}: {name}")
        df = DOMAIN_MODULES[args.domain].compute_index(args.data_dir)
        out = os.path.join(args.output, f"domain_{args.domain}_{name.lower().replace(' ','_')}.csv")
        df.to_csv(out)
        print(f"  Latest: {df['fragility_score'].iloc[-1]:.3f}  →  {out}")
        return

    print("=" * 72)
    print("  ECONOMIC FRAGILITY SIMULATOR")
    print("  MTS Pillar 4 — Compound Domestic Resilience Analysis")
    print("=" * 72)
    print(f"\n  Data: {args.data_dir}  |  Start: {args.start}\n")

    # --- Domain computation ---
    print("Computing domain fragility indices...")
    domain_results = compute_all_domains(args.data_dir)
    for num, df in domain_results.items():
        name = DOMAIN_NAMES[num].lower().replace(" ", "_").replace("-", "_")
        df.to_csv(os.path.join(args.output, f"domain_{num}_{name}.csv"))

    # --- Compound index ---
    print("\nComputing Compound Fragility Index...")
    combined = compute_cfi(domain_results, start_date=args.start)
    cfi_path = os.path.join(args.output, "compound_fragility_index.csv")
    combined.to_csv(cfi_path)

    print_summary(combined)
    print(f"\n  Historical range (2000–present):")
    print(f"    Min:     {combined['CFI_normalised'].min():.3f}  "
          f"({combined['CFI_normalised'].idxmin().strftime('%Y-%m')})")
    print(f"    Max:     {combined['CFI_normalised'].max():.3f}  "
          f"({combined['CFI_normalised'].idxmax().strftime('%Y-%m')})")
    print(f"    Mean:    {combined['CFI_normalised'].mean():.3f}")
    print(f"    Current: {combined['CFI_normalised'].iloc[-1]:.3f}")

    # Extract baseline domain scores
    latest = combined.iloc[-1]
    baseline_scores = {}
    domain_col_map = {1: "d1_", 2: "d2_", 3: "d3_", 4: "d4_", 5: "d5_", 6: "d6_"}
    for num, prefix in domain_col_map.items():
        match = next((c for c in combined.columns if c.startswith(prefix)), None)
        if match:
            baseline_scores[num] = float(latest[match])
    baseline_cfi = float(latest["CFI_normalised"])

    # --- Scenarios ---
    if not args.no_scenarios:
        if args.scenario:
            if args.scenario not in SCENARIO_PARAMS:
                print(f"Unknown scenario. Valid: {list(SCENARIO_PARAMS.keys())}"); sys.exit(1)
            print(f"\nRunning scenario: {args.scenario}")
            df = run_scenario(args.scenario, baseline_scores, baseline_cfi)
            out = os.path.join(args.scenarios_dir, f"scenario_{args.scenario}.csv")
            df.to_csv(out)
            print(df.to_string())
        else:
            print("\nRunning all four scenarios...")
            all_results = run_all_scenarios(
                baseline_scores, baseline_cfi, args.scenarios_dir)
            print_scenario_summary(all_results, baseline_cfi)

    # --- Interaction analysis ---
    if args.interactions:
        print("\nRunning domain interaction analysis...")
        from .interactions import run_interaction_analysis
        run_interaction_analysis(cfi_path, args.output)

    # --- Figures ---
    if not args.no_figures:
        print("\nGenerating publication figures...")
        try:
            from .visualisation import generate_all_figures
            generate_all_figures(
                cfi_path=cfi_path,
                scenarios_dir=args.scenarios_dir,
                output_dir=args.figures_dir,
            )
        except Exception as e:
            print(f"  [!] Figure generation failed: {e}")
            print("  Run with --no-figures to skip, or check matplotlib install")


if __name__ == "__main__":
    main()
