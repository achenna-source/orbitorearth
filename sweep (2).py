"""
OrbitOrEarth - figure generation
================================
High-quality, modern figures for the decision paper, on sourced inputs.

Figure 1 (tornado):  lever ranking by the swing each parameter induces on the
                     break-even grid intensity I*.
Figure 2 (map):      the C1 spine. Break-even contours for the two launch-
                     accounting choices (combustion-only vs embodied) vs system
                     mass. The band between them is the region where the verdict
                     depends ONLY on the accounting choice -- the paper's thesis.

Run:  python sweep.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import model as m

FIGDIR = Path("figures")
FIGDIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# Modern style
# --------------------------------------------------------------------------
INK      = "#1A2A3A"   # near-black slate for text/axes
SUBINK   = "#5B6B7B"   # muted grey for secondary text
ORBIT    = "#2A9D8F"   # teal  -> orbit wins
GROUND   = "#E76F51"   # coral -> ground wins
DEPEND   = "#E9C46A"   # amber -> depends on accounting choice
BAR      = "#3D6B8E"   # muted steel blue for bars
BARNEG   = "#9DB4C4"   # light steel for the unfavourable side
GRIDCOL  = "#EAEDF0"
REFCOL   = "#8A97A4"


def set_style() -> None:
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "text.color": INK,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.titlepad": 16,
        "axes.labelsize": 12,
        "axes.labelcolor": INK,
        "axes.labelpad": 9,
        "axes.edgecolor": "#C7CFD6",
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRIDCOL,
        "grid.linewidth": 1.0,
        "xtick.color": SUBINK,
        "ytick.color": SUBINK,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.fontsize": 10.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


# Reference grids, kgCO2/kWh (illustrative anchors)
REF_GRIDS = [
    ("Clean grid", 0.05),
    ("US average", 0.37),
    ("Gas",        0.50),
]

STATUS_NOTE = ("Levers sourced: launch factor, system mass, GPU lifetime.  "
               "PUE and utilization still preliminary.")


def _base(params):
    return {k: v.value for k, v in params.items()}


# --------------------------------------------------------------------------
# Figure 1 - tornado
# --------------------------------------------------------------------------
def tornado(params, accounting: str = "embodied_included") -> Path:
    base = m.resolve(params, accounting)
    base_I = m.break_even_intensity(base)

    levers = [
        ("system_mass_per_kw",     "System mass / kW"),
        ("launch_factor_" + accounting, "Launch emission factor"),
        ("gpu_lifetime_years",     "GPU lifetime"),
        ("utilization",            "Utilization"),
        ("pue",                    "Terrestrial PUE"),
    ]

    rows = []
    for key, label in levers:
        p = params[key]
        lo_p, hi_p = dict(base), dict(base)
        lo_p[key] = p.low
        hi_p[key] = p.high
        if key.startswith("launch_factor_"):
            lo_p["launch_emission_factor"] = p.low
            hi_p["launch_emission_factor"] = p.high
        I_lo = m.break_even_intensity(lo_p)
        I_hi = m.break_even_intensity(hi_p)
        rows.append((label, I_lo, I_hi, abs(I_hi - I_lo)))

    rows.sort(key=lambda r: r[3])  # smallest swing at bottom

    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    y = np.arange(len(rows))

    for i, (label, I_lo, I_hi, swing) in enumerate(rows):
        left, right = min(I_lo, I_hi), max(I_lo, I_hi)
        # favourable (lower I*) half in strong colour, unfavourable in light
        ax.barh(i, base_I - left, left=left, height=0.62,
                color=BAR, edgecolor="white", linewidth=1.2, zorder=3)
        ax.barh(i, right - base_I, left=base_I, height=0.62,
                color=BARNEG, edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(right + 0.012, i, f"\u0394 {swing:.2f}", va="center", ha="left",
                fontsize=10, color=SUBINK, zorder=4)

    ax.axvline(base_I, color=INK, linewidth=1.6, zorder=5)
    ax.text(base_I, len(rows) - 0.35, f"  base I* = {base_I:.2f}",
            ha="left", va="bottom", fontsize=10.5, color=INK, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel("Break-even grid intensity  I*  (kgCO\u2082 / kWh)")
    ax.set_title("Which assumptions move the orbital break-even most",
                 loc="left")
    ax.set_xlim(left=0)
    ax.margins(y=0.10)
    ax.grid(axis="y", visible=False)

    legend = [
        Patch(facecolor=BAR, label="Toward orbit (lower I*)"),
        Patch(facecolor=BARNEG, label="Toward ground (higher I*)"),
    ]
    ax.legend(handles=legend, loc="lower right", ncol=1)

    fig.text(0.005, -0.02, STATUS_NOTE + f"   Accounting: {accounting.replace('_', ' ')}.",
             fontsize=8.5, color=SUBINK, ha="left")

    out = FIGDIR / "tornado.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# Figure 2 - break-even map (the C1 spine)
# --------------------------------------------------------------------------
def break_even_map(params) -> Path:
    base = _base(params)
    masses = np.linspace(10, 150, 240)

    def curve(accounting):
        f = base[f"launch_factor_{accounting}"]
        out = []
        for M in masses:
            p = dict(base)
            p["system_mass_per_kw"] = M
            p["launch_emission_factor"] = f
            out.append(m.break_even_intensity(p))
        return np.array(out)

    I_comb = curve("combustion_only")   # left  (optimistic accounting)
    I_emb  = curve("embodied_included") # right (pessimistic accounting)

    x_max = max(0.8, float(I_emb.max()) * 1.05)
    fig, ax = plt.subplots(figsize=(9.6, 6.0))

    # Region shading: ground-wins (left of combustion curve),
    # accounting-dependent (between curves), orbit-wins (right of embodied curve)
    ax.fill_betweenx(masses, 0, I_comb, color=GROUND, alpha=0.16, zorder=1)
    ax.fill_betweenx(masses, I_comb, I_emb, color=DEPEND, alpha=0.30, zorder=1)
    ax.fill_betweenx(masses, I_emb, x_max, color=ORBIT, alpha=0.16, zorder=1)

    # Break-even contours
    ax.plot(I_comb, masses, color=GROUND, linewidth=2.6, zorder=4,
            solid_capstyle="round")
    ax.plot(I_emb, masses, color=ORBIT, linewidth=2.6, zorder=4,
            solid_capstyle="round")

    # Reference grids
    for name, g in REF_GRIDS:
        if g <= x_max:
            ax.axvline(g, color=REFCOL, linewidth=1.2, linestyle=(0, (4, 3)),
                       zorder=3)
            ax.text(g, 152.5, name, rotation=0, ha="center", va="bottom",
                    fontsize=9.5, color=SUBINK)

    # Region labels
    ax.text(x_max * 0.985, 130, "Orbit wins\n(either accounting)", ha="right",
            va="top", fontsize=11.5, color="#1F7A6E", fontweight="bold", zorder=5)
    ax.text(0.030, 100, "Ground wins", ha="center", va="center", rotation=68,
            rotation_mode="anchor", fontsize=10.5, color="#C0512F",
            fontweight="bold", zorder=5)
    band_x = float((np.interp(128, masses, I_comb) + np.interp(128, masses, I_emb)) / 2)
    ax.text(band_x, 122, "depends on\nthe accounting", ha="center", va="center",
            fontsize=9.5, color="#9A7B1F", fontweight="bold", zorder=6)

    ax.set_xlabel("Displaced grid carbon intensity  (kgCO\u2082 / kWh)")
    ax.set_ylabel("Launched system mass  (kg / kW IT)")
    ax.set_title("When does orbit beat the ground? The accounting choice is the pivot",
                 loc="left")
    ax.set_xlim(0, x_max)
    ax.set_ylim(10, 150)

    legend = [
        Line2D([0], [0], color=GROUND, lw=2.6, label="Break-even, combustion-only (optimistic)"),
        Line2D([0], [0], color=ORBIT, lw=2.6, label="Break-even, embodied launch (pessimistic)"),
        Patch(facecolor=DEPEND, alpha=0.30, label="Accounting-dependent zone"),
    ]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=3, columnspacing=1.4, handlelength=1.8)

    fig.text(0.005, -0.085, STATUS_NOTE, fontsize=8.5, color=SUBINK, ha="left")

    out = FIGDIR / "break_even_map.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    set_style()
    params = m.load_params("params.yaml")
    t = tornado(params)
    bem = break_even_map(params)
    print(f"wrote {t}")
    print(f"wrote {bem}")


if __name__ == "__main__":
    main()
