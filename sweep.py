"""
OrbitOrEarth - parameter sweep and tornado sensitivity.

ILLUSTRATIVE ONLY. This script runs on the PLACEHOLDER values in params.yaml
(several reverse-engineered to reproduce the brief). Every output is watermarked
and must NOT be reported as a result until params.yaml is sourced.

What is informative here vs not:
  - the TORNADO ranking reflects the [low, high] ranges you assign (a real input
    judgement) -> use it to prioritise sourcing, coarsely;
  - the break-even MAP position is placeholder-driven (launch factors are fitted
    to the brief) -> use it only to validate the figure DESIGN, not the numbers.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import model as m

FIG = Path("figures")
TAB = Path("tables")
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)

WATERMARK = "ILLUSTRATIVE - placeholder inputs, not sourced"
REFERENCE_GRIDS = {"clean": 0.05, "US avg": 0.37, "gas": 0.50}  # kgCO2/kWh


def _add_watermark(ax) -> None:
    ax.text(
        0.5, 0.5, WATERMARK, transform=ax.transAxes, fontsize=18,
        color="red", alpha=0.18, ha="center", va="center", rotation=20,
        weight="bold", zorder=10,
    )


# --------------------------------------------------------------------------
# Tornado: one-at-a-time sensitivity of I* to each parameter's [low, high]
# --------------------------------------------------------------------------
def tornado(params, accounting: str = "embodied_included"):
    base = m.resolve(params, accounting)
    base_istar = m.break_even_intensity(base)
    active_lf = f"launch_factor_{accounting}"

    varied = [
        "system_mass_per_kw",
        active_lf,
        "gpu_lifetime_years",
        "pue",
        "utilization",
        "orbital_embodied_per_kw",
        "dc_construction_avoided_per_kw",
    ]

    rows = []
    for name in varied:
        p = params[name]
        lo_p, hi_p = dict(base), dict(base)
        key = "launch_emission_factor" if name == active_lf else name
        lo_p[key], hi_p[key] = p.low, p.high
        lo = m.break_even_intensity(lo_p)
        hi = m.break_even_intensity(hi_p)
        rows.append((name, lo, hi, abs(hi - lo)))

    rows.sort(key=lambda r: r[3], reverse=True)
    return base_istar, rows


def plot_tornado(base_istar, rows, path: Path) -> None:
    labels = [r[0] for r in rows][::-1]   # widest at top
    los = np.array([r[1] for r in rows][::-1])
    his = np.array([r[2] for r in rows][::-1])
    left = np.minimum(los, his)
    width = np.abs(his - los)

    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(labels))
    ax.barh(y, width, left=left, color="#3b6ea5", alpha=0.85, zorder=3)
    ax.axvline(base_istar, color="black", lw=1.2, ls="--", zorder=4,
               label=f"base I* = {base_istar:.3f}")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("break-even grid intensity I*  [kgCO2/kWh]")
    ax.set_title("Tornado: sensitivity of the break-even intensity (embodied accounting)")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.3, zorder=0)
    _add_watermark(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def write_tornado_csv(base_istar, rows, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["parameter", "I*_at_low", "I*_at_high", "swing", "base_I*"])
        for name, lo, hi, swing in rows:
            w.writerow([name, f"{lo:.4f}", f"{hi:.4f}", f"{swing:.4f}", f"{base_istar:.4f}"])


# --------------------------------------------------------------------------
# Break-even contour: mass (y) vs threshold grid intensity I*(mass) (x)
# --------------------------------------------------------------------------
def contour(params, masses, accounting: str):
    base = m.resolve(params, accounting)
    out = []
    for mass in masses:
        p = dict(base)
        p["system_mass_per_kw"] = float(mass)
        out.append((float(mass), m.break_even_intensity(p)))
    return out


def plot_break_even_map(params, path: Path) -> None:
    masses = np.linspace(40, 160, 60)
    fig, ax = plt.subplots(figsize=(8, 5.5))

    for acc, color in [("combustion_only", "#d08c34"), ("embodied_included", "#3b6ea5")]:
        pts = contour(params, masses, acc)
        x = [istar for _, istar in pts]
        y = [mass for mass, _ in pts]
        ax.plot(x, y, color=color, lw=2.2, label=f"break-even ({acc})")

    for name, g in REFERENCE_GRIDS.items():
        ax.axvline(g, color="grey", ls=":", lw=1.2)
        ax.text(g, 158, f" {name}\n {g}", color="grey", fontsize=8, va="top")

    ax.set_xlabel("displaced grid carbon intensity  [kgCO2/kWh]")
    ax.set_ylabel("launched system mass  [kg/kW]")
    ax.set_title("Break-even map (DESIGN CHECK)\norbit wins to the right of each curve")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(40, 160)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    _add_watermark(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> None:
    params = m.load_params("params.yaml")
    settings = m.load_settings("params.yaml")
    accounting = settings.get("launch_accounting", "embodied_included")

    base_istar, rows = tornado(params, accounting)
    plot_tornado(base_istar, rows, FIG / "tornado.png")
    write_tornado_csv(base_istar, rows, TAB / "tornado.csv")
    plot_break_even_map(params, FIG / "break_even_map.png")

    print(f"Base I* = {base_istar:.3f} kgCO2/kWh ({accounting} accounting)\n")
    print("Lever ranking (widest swing in I* first):")
    print(f"  {'parameter':<34} {'I*@low':>8} {'I*@high':>8} {'swing':>8}")
    for name, lo, hi, swing in rows:
        print(f"  {name:<34} {lo:>8.3f} {hi:>8.3f} {swing:>8.3f}")
    print("\nWrote figures/tornado.png, figures/break_even_map.png, tables/tornado.csv")
    print("ILLUSTRATIVE: placeholder inputs. Do not report. See params.yaml.")


if __name__ == "__main__":
    main()
