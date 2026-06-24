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

    def curve(factor):
        out = []
        for M in masses:
            p = dict(base)
            p["system_mass_per_kw"] = M
            p["launch_emission_factor"] = factor
            out.append(m.break_even_intensity(p))
        return np.array(out)

    f_comb = base["launch_factor_combustion_only"]
    f_emb = base["launch_factor_embodied_included"]
    f_force = f_emb * base["forcing_multiplier"]
    I_comb = curve(f_comb)     # optimist: direct CO2  (~ NTU pole)
    I_emb = curve(f_emb)       # embodied launch, direct CO2
    I_force = curve(f_force)   # CO2e + high-altitude forcing  (~ Saarland pole)

    C_OPT, C_MID, C_PES = "#1F7A6E", "#B07A1E", "#C0392B"
    x_lo = 0.02
    x_hi = max(2.4, float(I_force.max()) * 1.1)
    fig, ax = plt.subplots(figsize=(10.2, 6.3))

    # Region tints: ground wins under any metric | metric-dependent | orbit wins under any metric
    ax.fill_betweenx(masses, x_lo, np.clip(I_comb, x_lo, x_hi), color=GROUND, alpha=0.10, zorder=1)
    ax.fill_betweenx(masses, np.clip(I_comb, x_lo, x_hi), np.clip(I_force, x_lo, x_hi),
                     color=DEPEND, alpha=0.16, zorder=1)
    ax.fill_betweenx(masses, np.clip(I_force, x_lo, x_hi), x_hi, color=ORBIT, alpha=0.12, zorder=1)

    # Three break-even contours
    ax.plot(I_comb, masses, color=C_OPT, linewidth=2.8, zorder=5, solid_capstyle="round")
    ax.plot(I_emb, masses, color=C_MID, linewidth=2.0, zorder=5, linestyle=(0, (5, 2)),
            solid_capstyle="round")
    ax.plot(I_force, masses, color=C_PES, linewidth=2.8, zorder=5, solid_capstyle="round")

    # Reference grids
    for name, g in REF_GRIDS:
        if x_lo <= g <= x_hi:
            ax.axvline(g, color=REFCOL, linewidth=1.1, linestyle=(0, (4, 3)), zorder=3)
            ax.text(g, 148, name + "  ", rotation=90, ha="center", va="top",
                    fontsize=9, color=SUBINK, zorder=4)

    # Camp tags at the tops of the extreme curves
    ax.text(float(np.interp(146, masses, I_comb)), 147, "NTU", ha="center", va="bottom",
            fontsize=10.5, color=C_OPT, fontweight="bold", zorder=6)
    ax.text(float(np.interp(146, masses, I_force)), 147, "Saarland", ha="center", va="bottom",
            fontsize=10.5, color=C_PES, fontweight="bold", zorder=6)

    # Region labels
    ax.text(0.9, 26, "Orbit wins\nunder any metric", ha="center", va="center",
            fontsize=11, color=C_OPT, fontweight="bold", zorder=6)
    ax.text(0.030, 112, "Ground\nwins", ha="center", va="center",
            fontsize=10, color=C_PES, fontweight="bold", zorder=6)
    ax.text(0.26, 112, "verdict depends on the\nmetric / accounting choice", ha="center",
            va="center", fontsize=10.5, color="#8A6A12", fontweight="bold", zorder=6)

    ax.set_xscale("log")
    ax.set_xlabel("Displaced grid carbon intensity  (kgCO\u2082 / kWh, log scale)")
    ax.set_ylabel("Launched system mass  (kg / kW IT)")
    ax.set_title("The two camps are one model read under different climate metrics", loc="left")
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(10, 150)
    ax.grid(which="minor", axis="x", color=GRIDCOL, linewidth=0.6)

    legend = [
        Line2D([0], [0], color=C_OPT, lw=2.8, label="Optimist: direct launch CO\u2082  (\u2248 NTU)"),
        Line2D([0], [0], color=C_MID, lw=2.0, linestyle=(0, (5, 2)),
               label="Embodied launch, direct CO\u2082"),
        Line2D([0], [0], color=C_PES, lw=2.8,
               label="Pessimist: CO\u2082e + high-altitude forcing  (\u2248 Saarland)"),
    ]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.13),
              ncol=3, columnspacing=1.4, handlelength=1.9, fontsize=9.5)

    fig.text(0.005, -0.105, STATUS_NOTE + "  Forcing multiplier x1 (direct CO\u2082) to x50; central x10.",
             fontsize=8.5, color=SUBINK, ha="left")

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
