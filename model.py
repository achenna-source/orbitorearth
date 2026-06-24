"""
OrbitOrEarth - core model
==========================
Break-even carbon intensity for orbital vs terrestrial AI compute, per kW of
IT load.

Central equation (per kW, integrated over the GPU lifetime):

    I*  =  ( M * f_launch  +  B  -  D )  /  ( PUE * H * L * U )

with
    M         launched system mass per kW           [kg/kW]    (radiator-dominated)
    f_launch  launch emission factor                [kgCO2/kg] (combustion-only OR embodied)
    B         orbital embodied carbon per kW        [kgCO2/kW] (bus, solar, radiator mfg)
    D         avoided terrestrial DC construction   [kgCO2/kW] (second-order)
    PUE       terrestrial power usage effectiveness [-]
    H         hours per year                        [h/year]
    L         GPU useful lifetime                   [year]
    U         average utilization                   [-]

Orbit emits less carbon than the ground baseline exactly when the displaced grid
intensity I_grid exceeds I*. Operational carbon in orbit is ~0 (continuous
solar). Per-kW GPU manufacturing carbon is assumed equal on both sides and
cancels in the differential.

INTEGRITY NOTE
--------------
Sourcing in progress. As of now, launch_factor_* (traced), system_mass_per_kw
(radiator component) and gpu_lifetime_years carry SOURCED values; pue, utilization,
orbital_embodied_per_kw and dc_construction_avoided_per_kw remain PLACEHOLDERS.
The `--selfcheck` regression is decoupled (it uses fixed reference inputs, not
params.yaml) so it verifies the FORMULA, not the sourced values. Every parameter
with status "placeholder" must be replaced by a cited value (and low/high range)
before its number is reported in the paper. No invented value is ever presented
as real.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
@dataclass
class Param:
    value: float
    low: float
    high: float
    unit: str
    source: str
    status: str  # "sourced" or "placeholder"


def load_params(path: str | Path = "params.yaml") -> dict[str, Param]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    out: dict[str, Param] = {}
    for name, d in raw["parameters"].items():
        out[name] = Param(
            value=float(d["value"]),
            low=float(d["low"]),
            high=float(d["high"]),
            unit=str(d["unit"]),
            source=str(d.get("source", "[A SOURCER]")),
            status=str(d.get("status", "placeholder")),
        )
    return out


def load_settings(path: str | Path = "params.yaml") -> dict:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return raw.get("settings", {})


def resolve(params: dict[str, Param], accounting: str) -> dict[str, float]:
    """Flatten to point values; select the launch factor for the chosen accounting.

    accounting in {combustion_only, embodied_included, embodied_forced}.
    'embodied_forced' multiplies the embodied launch factor by the CO2e forcing
    multiplier (high-altitude black-carbon + alumina radiative forcing).
    """
    p = {k: v.value for k, v in params.items()}
    if accounting == "embodied_forced":
        p["launch_emission_factor"] = (
            p["launch_factor_embodied_included"] * p["forcing_multiplier"]
        )
    else:
        p["launch_emission_factor"] = p[f"launch_factor_{accounting}"]
    return p


# --------------------------------------------------------------------------
# Core model (per kW of IT load)
# --------------------------------------------------------------------------
def ground_energy_kwh(p: dict[str, float]) -> float:
    """Electricity drawn at the terrestrial DC per kW, over the GPU lifetime."""
    return p["pue"] * p["hours_per_year"] * p["gpu_lifetime_years"] * p["utilization"]


def orbit_carbon_per_kw(p: dict[str, float]) -> float:
    """Differential embodied carbon of the orbital option per kW (vs ground)."""
    return (
        p["system_mass_per_kw"] * p["launch_emission_factor"]
        + p["orbital_embodied_per_kw"]
        - p["dc_construction_avoided_per_kw"]
    )


def break_even_intensity(p: dict[str, float]) -> float:
    """Grid intensity (kgCO2/kWh) above which orbit emits less carbon than ground."""
    return orbit_carbon_per_kw(p) / ground_energy_kwh(p)


def ground_carbon_per_kw(p: dict[str, float], grid_intensity: float) -> float:
    """Operational carbon of the ground option per kW over lifetime, at a given grid."""
    return ground_energy_kwh(p) * grid_intensity


def orbit_wins(p: dict[str, float], grid_intensity: float) -> bool:
    """True if orbit emits less carbon than ground at this grid intensity."""
    return orbit_carbon_per_kw(p) < ground_carbon_per_kw(p, grid_intensity)


# --------------------------------------------------------------------------
# Water (second decided axis; orbit operational water ~ 0)
# --------------------------------------------------------------------------
def water_saved_gallons_per_kw(p: dict[str, float]) -> float:
    """Water avoided by leaving the ground, per kW over the GPU lifetime."""
    e = ground_energy_kwh(p)
    return e * (p["water_intensity_grid_gal_per_kwh"] + p["cooling_water_gal_per_kwh"])


# --------------------------------------------------------------------------
# Monte-Carlo uncertainty propagation (the brief's "confidence intervals")
# --------------------------------------------------------------------------
def _triangular(rng: np.random.Generator, p: Param, n: int) -> np.ndarray:
    if p.high <= p.low:
        return np.full(n, p.value)
    mode = min(max(p.value, p.low), p.high)
    return rng.triangular(p.low, mode, p.high, n)


def monte_carlo_break_even(
    params: dict[str, Param],
    accounting: str,
    n: int = 100_000,
    seed: int = 0,
) -> np.ndarray:
    """Propagate input ranges to a distribution of the break-even intensity I*."""
    rng = np.random.default_rng(seed)
    d = {k: _triangular(rng, p, n) for k, p in params.items()}
    if accounting == "embodied_forced":
        lf = d["launch_factor_embodied_included"] * d["forcing_multiplier"]
    else:
        lf = d[f"launch_factor_{accounting}"]
    e = d["pue"] * d["hours_per_year"] * d["gpu_lifetime_years"] * d["utilization"]
    orbit = (
        d["system_mass_per_kw"] * lf
        + d["orbital_embodied_per_kw"]
        - d["dc_construction_avoided_per_kw"]
    )
    return orbit / e


def summarize(samples: np.ndarray, lo: float = 5, hi: float = 95) -> dict[str, float]:
    return {
        "median": float(np.median(samples)),
        f"p{int(lo)}": float(np.percentile(samples, lo)),
        f"p{int(hi)}": float(np.percentile(samples, hi)),
        "mean": float(np.mean(samples)),
    }


# --------------------------------------------------------------------------
# Self-consistency vs the scoping brief's preliminary envelope
# --------------------------------------------------------------------------
# Equation regression. This verifies the break-even FORMULA against the brief's
# preliminary envelope (0.06 / 0.12 / 0.59 / 0.88). It uses FIXED reference inputs
# below, NOT the values in params.yaml, so that sourcing real parameters (which
# produce different, real results) does not break the formula test.
REGRESSION_FACTORS = {"combustion_only": 37.9, "embodied_included": 185.0}
REGRESSION_FIXED = dict(pue=1.2, hours_per_year=8766.0, utilization=1.0,
                        orbital_embodied_per_kw=0.0, dc_construction_avoided_per_kw=0.0)
BRIEF_TABLE = [
    dict(mass=50, accounting="combustion_only", expected=0.06),
    dict(mass=100, accounting="combustion_only", expected=0.12),
    dict(mass=100, accounting="embodied_included", expected=0.59),
    dict(mass=150, accounting="embodied_included", expected=0.88),
]


def selfcheck(verbose: bool = True, tol: float = 0.01) -> bool:
    """Regression test of the break-even formula against the brief's envelope,
    using fixed reference inputs (independent of sourced params.yaml values)."""
    ok = True
    for row in BRIEF_TABLE:
        p = dict(REGRESSION_FIXED)
        p["system_mass_per_kw"] = float(row["mass"])
        p["launch_emission_factor"] = REGRESSION_FACTORS[row["accounting"]]
        p["gpu_lifetime_years"] = 3.0
        got = break_even_intensity(p)
        close = abs(got - row["expected"]) <= tol
        ok = ok and close
        if verbose:
            tag = "ok" if close else "MISMATCH"
            print(
                f"  mass={row['mass']:>3} kg/kW  {row['accounting']:<18} "
                f"expected={row['expected']:.2f}  got={got:.3f}  [{tag}]"
            )
    return ok


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="OrbitOrEarth core model")
    ap.add_argument("--params", default="params.yaml")
    ap.add_argument(
        "--selfcheck",
        action="store_true",
        help="verify the model reproduces the brief's preliminary table",
    )
    args = ap.parse_args()

    params = load_params(args.params)
    settings = load_settings(args.params)
    accounting = settings.get("launch_accounting", "embodied_included")

    if args.selfcheck:
        print("Break-even formula regression vs the brief envelope (GPU lifetime = 3 y):")
        ok = selfcheck()
        print("PASS" if ok else "FAIL")
        unsourced = [k for k, p in params.items() if p.status != "sourced"]
        print(f"\n{len(unsourced)} parameter(s) still need a source:")
        for k in unsourced:
            print(f"  - {k}")
        raise SystemExit(0 if ok else 1)

    p = resolve(params, accounting)
    istar = break_even_intensity(p)
    samples = monte_carlo_break_even(
        params,
        accounting,
        n=int(settings.get("monte_carlo_samples", 100_000)),
        seed=int(settings.get("seed", 0)),
    )
    s = summarize(samples)
    water = water_saved_gallons_per_kw(p)

    print(f"Launch accounting : {accounting}")
    print(f"Break-even I*     : {istar:.3f} kgCO2/kWh (point estimate)")
    print(
        f"Monte-Carlo I*    : median {s['median']:.3f}, "
        f"90% interval [{s['p5']:.3f}, {s['p95']:.3f}] kgCO2/kWh"
    )
    print(
        f"Water avoided     : {water:,.0f} gallons/kW over "
        f"{p['gpu_lifetime_years']:.0f} years"
    )
    print("\nReference grids (kgCO2/kWh): clean 0.05 | US avg 0.37 | gas 0.50")
    print("WARNING: defaults are placeholders, not sourced. See params.yaml.")


if __name__ == "__main__":
    main()
