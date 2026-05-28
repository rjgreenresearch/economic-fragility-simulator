"""
visualisation.py -- Publication-quality figure generation for Paper 7.

Produces three figures required for submission to the Journal of
Post-Keynesian Economics:

  Figure 1: Domain fragility time series (2000–2026)
             Six panels, one per domain, with shaded recession bands
             and a 2026 assessment annotation.

  Figure 2: Compound Fragility Index historical record (2000–2026)
             Single panel; GFC, COVID, and current reference lines;
             historical episode annotations.

  Figure 3: Scenario comparison (compound stress projections)
             Four scenario trajectories from current baseline over
             eight quarters, with GFC threshold reference line.

All figures use a consistent journal-ready style: Times New Roman,
grayscale-compatible, 300 dpi, single-column width (3.5 in) or
double-column width (7.0 in) as appropriate.

Usage:
    from econ_fragility.visualisation import generate_all_figures
    generate_all_figures(
        cfi_path="data/processed/compound_fragility_index.csv",
        scenarios_dir="data/scenarios/",
        output_dir="figures/"
    )

    # Or from CLI:
    python -m econ_fragility --figures --figures-dir figures/
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

# --- Journal style constants ---
FONT_FAMILY   = "DejaVu Serif"  # Fallback if Times New Roman unavailable
FONT_SIZE_SM  = 7
FONT_SIZE_MD  = 8
FONT_SIZE_LG  = 9
FONT_SIZE_XL  = 10
COL_SINGLE    = 3.5   # inches — single column
COL_DOUBLE    = 7.2   # inches — double column (text width)
DPI           = 300

# Grayscale-safe palette (distinguishable in print)
COLORS = {
    "d1": "#1a1a1a",   # near-black
    "d2": "#4d4d4d",   # dark grey
    "d3": "#808080",   # mid grey
    "d4": "#b3b3b3",   # light grey
    "d5": "#333333",   # charcoal (dashed)
    "d6": "#666666",   # medium (dotted)
    "cfi": "#000000",  # black for compound index
    "gfc": "#d62728",  # red annotation
    "covid": "#ff7f0e",
    "current": "#2ca02c",
    "shading": "#f0f0f0",
}

LINESTYLES = {
    "d1": "-", "d2": "-", "d3": "-",
    "d4": "--", "d5": "--", "d6": ":"
}

# NBER recession quarters (start, end) — post-2000
RECESSIONS = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

DOMAIN_LABELS = {
    "d1_Wage-Produ": "Domain 1: Wage-Productivity Gap",
    "d2_Consumer B": "Domain 2: Consumer Balance Sheet",
    "d3_Fiscal Sus": "Domain 3: Fiscal Sustainability",
    "d4_Labour Mar": "Domain 4: Labour Market",
    "d5_Trade Arch": "Domain 5: Trade Architecture",
    "d6_Monetary C": "Domain 6: Monetary Constraint",
}

DOMAIN_SHORT = {
    "d1_Wage-Produ": "Wage-Productivity",
    "d2_Consumer B": "Consumer Balance",
    "d3_Fiscal Sus": "Fiscal Sustainability",
    "d4_Labour Mar": "Labour Market",
    "d5_Trade Arch": "Trade Architecture",
    "d6_Monetary C": "Monetary Constraint",
}

SCENARIO_LABELS = {
    "scenario_tariff_cascade":     "Scenario 1: Tariff Cascade",
    "scenario_ai_displacement":    "Scenario 2: AI Displacement",
    "scenario_fiscal_constraint":  "Scenario 3: Fiscal Constraint",
    "scenario_compound_stress":    "Scenario 4: Compound Stress",
}

SCENARIO_LINESTYLES = {
    "scenario_tariff_cascade":    "-",
    "scenario_ai_displacement":   "--",
    "scenario_fiscal_constraint": "-.",
    "scenario_compound_stress":   ":",
}

SCENARIO_COLORS = {
    "scenario_tariff_cascade":    "#333333",
    "scenario_ai_displacement":   "#555555",
    "scenario_fiscal_constraint": "#777777",
    "scenario_compound_stress":   "#000000",
}


def _set_journal_style():
    """Apply consistent journal-ready matplotlib style."""
    plt.rcParams.update({
        "font.family":        "serif",
        "font.serif":         [FONT_FAMILY, "Times New Roman", "Georgia"],
        "font.size":          FONT_SIZE_MD,
        "axes.titlesize":     FONT_SIZE_MD,
        "axes.labelsize":     FONT_SIZE_MD,
        "xtick.labelsize":    FONT_SIZE_SM,
        "ytick.labelsize":    FONT_SIZE_SM,
        "legend.fontsize":    FONT_SIZE_SM,
        "figure.dpi":         DPI,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.linewidth":     0.6,
        "xtick.major.width":  0.6,
        "ytick.major.width":  0.6,
        "lines.linewidth":    1.0,
        "grid.linewidth":     0.4,
        "grid.alpha":         0.4,
        "grid.color":         "#bbbbbb",
        "savefig.bbox":       "tight",
        "savefig.pad_inches": 0.05,
    })


def _add_recession_bands(ax, df_index):
    """Shade NBER recession quarters in light grey."""
    for start, end in RECESSIONS:
        s = pd.Timestamp(start)
        e = pd.Timestamp(end)
        if s >= df_index.min() and s <= df_index.max():
            ax.axvspan(s, min(e, df_index.max()),
                       color=COLORS["shading"], alpha=0.7, zorder=0)


def _find_domain_cols(df):
    """Return ordered list of domain columns present in DataFrame."""
    prefixes = ["d1_", "d2_", "d3_", "d4_", "d5_", "d6_"]
    found = []
    for p in prefixes:
        matches = [c for c in df.columns if c.startswith(p)]
        if matches:
            found.append(matches[0])
    return found


# ---------------------------------------------------------------------------
# Figure 1: Domain Fragility Time Series
# ---------------------------------------------------------------------------

def figure_1_domain_timeseries(cfi_df, output_dir):
    """
    Six-panel time series: one panel per domain fragility score, 2000–2026.
    Includes recession shading and threshold reference line at 0.5.
    Double-column width for journal submission.
    """
    _set_journal_style()

    domain_cols = _find_domain_cols(cfi_df)
    if not domain_cols:
        print("  [!] No domain columns found in CFI data")
        return

    n = len(domain_cols)
    n_cols = 2
    n_rows = (n + 1) // 2

    fig, axes = plt.subplots(n_rows, n_cols,
                              figsize=(COL_DOUBLE, COL_DOUBLE * 0.75),
                              sharex=True)
    axes = axes.flatten()

    dk_colors = ["d1","d2","d3","d4","d5","d6"]
    dk_ls     = ["-","-","-","--","--",":"]

    for i, col in enumerate(domain_cols):
        ax = axes[i]
        label = DOMAIN_SHORT.get(col, col)
        color = COLORS[dk_colors[i]]
        ls    = dk_ls[i]

        _add_recession_bands(ax, cfi_df.index)

        ax.plot(cfi_df.index, cfi_df[col],
                color=color, linestyle=ls, linewidth=1.0,
                label=label)

        # Threshold reference at 0.5
        ax.axhline(0.5, color="#999999", linestyle=":", linewidth=0.6,
                   label="Threshold (0.5)")

        # Mark current value
        latest_val = cfi_df[col].iloc[-1]
        latest_date = cfi_df.index[-1]
        ax.annotate(
            f"{latest_val:.2f}",
            xy=(latest_date, latest_val),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=FONT_SIZE_SM - 1,
            color=color,
            va="center",
        )

        ax.set_title(label, fontsize=FONT_SIZE_SM, pad=3)
        ax.set_ylim(0, 1.05)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
        ax.grid(True, axis="y")

        # Only show x-axis label on bottom row
        if i >= n - n_cols:
            ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter("'%y"))
            ax.xaxis.set_major_locator(
                matplotlib.dates.YearLocator(4))
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    # Hide unused panel if odd number of domains
    if n % 2 != 0:
        axes[-1].set_visible(False)

    # Shared y-axis label
    fig.text(0.01, 0.5, "Fragility Score (0 = Resilient, 1 = Threshold)",
             va="center", rotation="vertical", fontsize=FONT_SIZE_SM)

    # Recession legend patch
    recession_patch = mpatches.Patch(
        facecolor=COLORS["shading"], edgecolor="none",
        label="NBER recession")
    fig.legend(handles=[recession_patch],
               loc="lower center", ncol=1,
               frameon=False, fontsize=FONT_SIZE_SM,
               bbox_to_anchor=(0.5, -0.01))

    fig.suptitle(
        "Figure 1. Domain Fragility Scores, 2000–2026\n"
        r"$\it{Note}$: Shaded bands = NBER recessions. "
        "Dashed line = fragility threshold (0.5).",
        fontsize=FONT_SIZE_SM, y=1.01)

    plt.tight_layout(rect=[0.04, 0.03, 1, 1])

    path = os.path.join(output_dir, "figure_1_domain_timeseries.pdf")
    fig.savefig(path, format="pdf", dpi=DPI)
    path_png = os.path.join(output_dir, "figure_1_domain_timeseries.png")
    fig.savefig(path_png, format="png", dpi=DPI)
    plt.close(fig)
    print(f"  Figure 1 saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Figure 2: Compound Fragility Index Historical Record
# ---------------------------------------------------------------------------

def figure_2_cfi_history(cfi_df, output_dir):
    """
    Single-panel CFI time series with episode annotations.
    Single-column width for journal submission.
    """
    _set_journal_style()

    if "CFI_normalised" not in cfi_df.columns:
        print("  [!] CFI_normalised column not found")
        return

    fig, ax = plt.subplots(figsize=(COL_DOUBLE, 2.8))

    _add_recession_bands(ax, cfi_df.index)

    # Main CFI line
    ax.plot(cfi_df.index, cfi_df["CFI_normalised"],
            color=COLORS["cfi"], linewidth=1.2, label="CFI (normalised)")

    # Historical reference thresholds
    ref_lines = [
        (0.061, "Pre-GFC (2007): 0.061",  "--", "#888888"),
        (0.155, "GFC (2009): 0.155",       "--", "#555555"),
        (0.175, "Post-GFC peak (2011): 0.175", "-.", "#333333"),
        (0.125, "COVID (2020): 0.125",      ":",  "#777777"),
    ]
    for val, lbl, ls, col in ref_lines:
        ax.axhline(val, linestyle=ls, linewidth=0.7,
                   color=col, alpha=0.8, label=lbl)

    # Annotate current value
    latest_val  = cfi_df["CFI_normalised"].iloc[-1]
    latest_date = cfi_df.index[-1]
    ax.annotate(
        f"Current\n{latest_val:.3f}",
        xy=(latest_date, latest_val),
        xytext=(-48, 8),
        textcoords="offset points",
        fontsize=FONT_SIZE_SM,
        arrowprops=dict(arrowstyle="->", lw=0.6, color="#333333"),
        color=COLORS["cfi"],
    )

    # Annotate GFC peak
    peak_idx  = cfi_df["CFI_normalised"].idxmax()
    peak_val  = cfi_df["CFI_normalised"].max()
    ax.annotate(
        f"Peak\n{peak_val:.3f}",
        xy=(peak_idx, peak_val),
        xytext=(6, 4),
        textcoords="offset points",
        fontsize=FONT_SIZE_SM,
        color="#333333",
    )

    # Shaded "danger zone" above GFC peak
    ax.axhspan(0.175, 0.35, color="#f0f0f0", alpha=0.5, zorder=0)
    ax.text(pd.Timestamp("2003-01-01"), 0.185,
            "Exceeds GFC peak", fontsize=FONT_SIZE_SM - 1,
            color="#888888", style="italic")

    ax.set_ylim(0, 0.30)
    ax.set_ylabel("CFI (normalised, 0–1)", fontsize=FONT_SIZE_MD)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("'%y"))
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(3))
    ax.grid(True, axis="y")

    legend = ax.legend(
        loc="upper left", frameon=False,
        fontsize=FONT_SIZE_SM, ncol=1)

    recession_patch = mpatches.Patch(
        facecolor=COLORS["shading"], edgecolor="none", label="NBER recession")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [recession_patch],
              labels=labels + ["NBER recession"],
              loc="upper left", frameon=False,
              fontsize=FONT_SIZE_SM, ncol=1)

    ax.set_title(
        "Figure 2. Compound Fragility Index, 2000–2026\n"
        r"$\it{Note}$: " +
        "CFI = $\\prod_{k=1}^{6}(1 + D_k \\cdot w_k)$, normalised to [0,1]. "
        "Shaded bands = NBER recessions.",
        fontsize=FONT_SIZE_SM, pad=6)

    plt.tight_layout()

    path = os.path.join(output_dir, "figure_2_cfi_history.pdf")
    fig.savefig(path, format="pdf", dpi=DPI)
    path_png = os.path.join(output_dir, "figure_2_cfi_history.png")
    fig.savefig(path_png, format="png", dpi=DPI)
    plt.close(fig)
    print(f"  Figure 2 saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Figure 3: Scenario Comparison
# ---------------------------------------------------------------------------

def figure_3_scenarios(scenarios_dir, baseline_cfi, output_dir):
    """
    Four scenario CFI trajectories from current baseline over
    the full scenario horizon with GFC threshold reference.
    Double-column width for clarity.
    """
    _set_journal_style()

    # Load scenario CSVs
    scenario_data = {}
    for fname in sorted(os.listdir(scenarios_dir)):
        if fname.startswith("scenario_") and fname.endswith(".csv"):
            key = fname.replace(".csv", "")
            df = pd.read_csv(os.path.join(scenarios_dir, fname), index_col=0)
            scenario_data[key] = df

    if not scenario_data:
        print(f"  [!] No scenario CSVs found in {scenarios_dir}")
        return

    fig, ax = plt.subplots(figsize=(COL_DOUBLE, 3.2))

    # Baseline horizontal line
    ax.axhline(baseline_cfi, color="#aaaaaa", linewidth=0.8,
               linestyle="-", label=f"Baseline (current): {baseline_cfi:.3f}")

    # GFC peak threshold
    ax.axhline(0.175, color="#555555", linewidth=0.7, linestyle="--",
               label="GFC post-peak threshold: 0.175")

    # GFC period level
    ax.axhline(0.155, color="#888888", linewidth=0.7, linestyle=":",
               label="GFC (2009) level: 0.155")

    # Shaded zone above GFC peak
    ax.axhspan(0.175, 0.28, color="#f5f5f5", alpha=0.8, zorder=0)
    ax.text(0.2, 0.180, "Exceeds GFC peak",
            fontsize=FONT_SIZE_SM - 1, color="#888888", style="italic")

    # Plot each scenario
    for key, df in scenario_data.items():
        label = SCENARIO_LABELS.get(key, key)
        ls    = SCENARIO_LINESTYLES.get(key, "-")
        color = SCENARIO_COLORS.get(key, "#333333")

        quarters = df.index.astype(float)
        cfi_vals = df["CFI_normalised"].values

        ax.plot(quarters, cfi_vals,
                color=color, linestyle=ls, linewidth=1.2,
                label=label, zorder=3)

        # Annotate peak value
        peak_q   = df["CFI_normalised"].idxmax()
        peak_val = df["CFI_normalised"].max()
        ax.annotate(
            f"{peak_val:.3f}",
            xy=(float(peak_q), peak_val),
            xytext=(2, 2),
            textcoords="offset points",
            fontsize=FONT_SIZE_SM - 1,
            color=color,
        )

    ax.set_xlabel("Quarters from current baseline (Q0 = April 2026)",
                  fontsize=FONT_SIZE_MD)
    ax.set_ylabel("CFI (normalised, 0–1)", fontsize=FONT_SIZE_MD)
    ax.set_xlim(0, max(len(df) - 1
                       for df in scenario_data.values()) + 0.5)
    ax.set_ylim(max(0, baseline_cfi - 0.02), 0.28)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, axis="y")

    ax.legend(loc="upper left", frameon=False,
              fontsize=FONT_SIZE_SM, ncol=1)

    ax.set_title(
        "Figure 3. Scenario Compound Fragility Index Projections\n"
        r"$\it{Note}$: " +
        "Each scenario applies domain-specific shocks with cascade amplifiers "
        "to current Q1 2026 baseline. Sourced parameters — see Section 6.",
        fontsize=FONT_SIZE_SM, pad=6)

    plt.tight_layout()

    path = os.path.join(output_dir, "figure_3_scenarios.pdf")
    fig.savefig(path, format="pdf", dpi=DPI)
    path_png = os.path.join(output_dir, "figure_3_scenarios.png")
    fig.savefig(path_png, format="png", dpi=DPI)
    plt.close(fig)
    print(f"  Figure 3 saved: {path}")
    return path


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_all_figures(
    cfi_path="data/processed/compound_fragility_index.csv",
    scenarios_dir="data/scenarios/",
    output_dir="figures/",
):
    """Generate all three publication figures."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nGenerating publication figures → {output_dir}")

    # Load CFI data
    cfi_df = pd.read_csv(cfi_path, index_col=0, parse_dates=True)
    baseline_cfi = float(cfi_df["CFI_normalised"].iloc[-1])

    figure_1_domain_timeseries(cfi_df, output_dir)
    figure_2_cfi_history(cfi_df, output_dir)
    figure_3_scenarios(scenarios_dir, baseline_cfi, output_dir)

    print(f"\nAll figures saved to {output_dir}")
    print("  Format: PDF (submission) + PNG (preview)")
