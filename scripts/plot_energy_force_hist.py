"""
Distribution plot of energy and force,
We can change the values accordingly

python plot_energy_force_hist.py \
        --energy-xlim -950 -600 \
        --force-xlim -0.2 0.2 \
        --energy-bins 50 \
        --force-bins 0.01
"""

#!/usr/bin/env python3
import argparse
import os
import json
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter

def style_axes(ax):
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_linewidth(1.3)
    ax.tick_params(width=1.3, length=6, direction="out")
    # Bold tick labels
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontweight("bold")

def parse_force_components(forces_series):
    Fx, Fy, Fz = [], [], []
    for s in forces_series.dropna():
        try:
            arr = json.loads(s)
        except Exception:
            continue
        if not isinstance(arr, list):
            continue
        for vec in arr:
            if isinstance(vec, (list, tuple)) and len(vec) >= 3:
                try:
                    fx, fy, fz = float(vec[0]), float(vec[1]), float(vec[2])
                except Exception:
                    continue
                Fx.append(fx); Fy.append(fy); Fz.append(fz)
    return Fx, Fy, Fz

def bins_from_width(xmin, xmax, width):
    if width is None or width <= 0:
        return 50  # fallback
    span = xmax - xmin
    n = max(1, int(math.ceil(span / width)))
    return n

def main():
    ap = argparse.ArgumentParser(description="Publication-style histograms for Energy and component-wise Forces.")
    ap.add_argument("--csv", default="consolidated_data_10th_step_filtered_E-1050_to_-500__F-100_to_100.csv",
                    help="Input CSV with 'Energy' and JSON 'Forces' columns.")
    ap.add_argument("--energy-col", default="Energy", help="Energy column name.")
    ap.add_argument("--forces-col", default="Forces", help="Forces JSON column name.")
    # Energy display controls
    ap.add_argument("--energy-xlim", nargs=2, type=float, default=[-1050.0, -500.0],
                    help="Energy axis limits, e.g. --energy-xlim -1050 -500")
    ap.add_argument("--energy-bins", type=int, default=80, help="Number of energy bins (count, not width).")
    ap.add_argument("--energy-ticks", type=int, default=6, help="Max number of x ticks for energy.")
    # Force display controls
    ap.add_argument("--force-xlim", nargs=2, type=float, default=[-0.2, 0.2],
                    help="Force component axis limits, e.g. --force-xlim -0.2 0.2")
    ap.add_argument("--force-bin-width", type=float, default=0.01,
                    help="Force histogram BIN WIDTH (eV/Å). Example: 0.01")
    ap.add_argument("--force-ticks", type=int, default=5, help="Max number of x ticks for forces.")
    # Output files
    ap.add_argument("--energy-out", default="energy_hist.png", help="Energy figure filename.")
    ap.add_argument("--forces-out", default="forces_hist.png", help="Forces figure filename.")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise FileNotFoundError(f"No such file: {args.csv}")

    # Global typography
    plt.rcParams.update({
        "font.size": 14,
        "font.weight": "bold",
        "axes.labelsize": 16,
        "axes.labelweight": "bold",
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "legend.fontsize": 13,
    })

    df = pd.read_csv(args.csv)

    # ---------- Energy ----------
    if args.energy_col not in df.columns:
        raise ValueError(f"Column '{args.energy_col}' not found. Available: {list(df.columns)}")
    energies = pd.to_numeric(df[args.energy_col], errors="coerce").dropna()
    if energies.empty:
        raise ValueError("No numeric energy values found to plot.")

    fig = plt.figure(figsize=(6.2, 4.6))
    ax = plt.gca()
    ax.hist(energies, bins=args.energy_bins, range=(args.energy_xlim[0], args.energy_xlim[1]))
    ax.set_title("Energy Distribution")
    ax.set_xlabel("Energy (eV)")
    ax.set_ylabel("Count")
    ax.set_xlim(args.energy_xlim[0], args.energy_xlim[1])
    # De-clutter x ticks
    ax.xaxis.set_major_locator(MaxNLocator(nbins=args.energy_ticks, prune=None))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # whole eV steps typically best
    style_axes(ax)
    plt.tight_layout()
    plt.savefig(args.energy_out, dpi=600)
    plt.close(fig)
    print(f"Saved energy histogram to {args.energy_out}")

    # ---------- Forces (Fx, Fy, Fz) ----------
    if args.forces_col not in df.columns:
        raise ValueError(f"Column '{args.forces_col}' not found. Available: {list(df.columns)}")
    Fx, Fy, Fz = parse_force_components(df[args.forces_col])
    if not (Fx or Fy or Fz):
        raise ValueError("No parseable force components found to plot.")

    # Compute number of bins from bin WIDTH and x-limits
    f_bins = bins_from_width(args.force_xlim[0], args.force_xlim[1], args.force_bin_width)

    fig = plt.figure(figsize=(6.2, 4.6))
    ax = plt.gca()
    for comp, label in [(Fx, "Fx"), (Fy, "Fy"), (Fz, "Fz")]:
        if comp:
            ax.hist(
                comp,
                bins=f_bins,
                range=(args.force_xlim[0], args.force_xlim[1]),
                histtype="step",
                linewidth=2,
                label=label
            )
    ax.set_title("Force Component Distributions")
    ax.set_xlabel("Force component (eV/Å)")
    ax.set_ylabel("Count")
    ax.set_xlim(args.force_xlim[0], args.force_xlim[1])

    # De-clutter x ticks for forces
    ax.xaxis.set_major_locator(MaxNLocator(nbins=args.force_ticks, prune=None))
    # For small range like [-0.2, 0.2], show one decimal place
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    style_axes(ax)
    leg = ax.legend(loc="upper right", frameon=False)
    for txt in leg.get_texts():
        txt.set_fontweight("bold")
    plt.tight_layout()
    plt.savefig(args.forces_out, dpi=600)
    plt.close(fig)
    print(f"Saved force components histogram to {args.forces_out}")

if __name__ == "__main__":
    main()