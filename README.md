# OrbitOrEarth

**An open calculator for the orbital-vs-terrestrial carbon break-even of AI compute.**

OrbitOrEarth accompanies the paper *"When Does AI Compute Belong in Orbit? A Workload-Conditioned, Multi-Criteria Decision Framework for Orbital Data Centers."* It turns the paper's per-kilowatt lifecycle break-even model into an interactive decision tool and reproduces every figure and number reported in the manuscript.

The central finding is that the order-of-magnitude disagreement in the literature over orbital-data-center carbon reduces to a choice of accounting boundary and climate metric. The calculator makes that choice an explicit, movable axis: load the optimist (NTU) or the pessimist (Saarland) preset and watch the verdict flip.

## What's inside

| File | Purpose |
|------|---------|
| `orbitorearth.html` | Self-contained interactive calculator. Open in any browser, no install. |
| `model.py` | The break-even model. Central equation: `I* = (M*f + B - D) / (PUE*H*L*U)`. |
| `params.yaml` | All model parameters with value, low/high range, unit, source, and status. |
| `sweep.py` | Generates the sensitivity sweep, the tornado diagram, and the break-even map (300 DPI). |
| `test_model.py` | Reproducibility checks: the model reproduces the optimist, pessimist, and reference verdicts. |
| `requirements.txt` | Python dependencies for regenerating the figures. |

## Quick start

**The calculator.** Open `orbitorearth.html` in a web browser. Move the sliders (system mass, hardware lifetime, forcing multiplier, PUE, utilization, grid intensity), toggle the accounting boundary and the climate metric, or load a preset. The orbit-or-ground verdict, the break-even intensity `I*`, the Monte-Carlo interval, and a confidence label all update live.

**The figures.**

    pip install -r requirements.txt
    python sweep.py

This writes the paper's figures to `figures/`.

## Parameters and provenance

Every parameter in `params.yaml` carries a `source` and a `status` field (`sourced`, `estimated`, or `preliminary`). The forcing multiplier, the orbital-manufacturing term, the avoided-construction term, and the per-kilowatt water term are documented as preliminary. Substitute your own estimates and the verdict updates accordingly.

## How to cite

If you use OrbitOrEarth, please cite the archived release:

> [Author], *OrbitOrEarth: A Workload-Conditioned, Multi-Criteria Decision Calculator for Orbital Data Centers*, 2026. Zenodo. DOI: 10.5281/zenodo.XXXXXXX

Replace the DOI above with the one Zenodo assigns, and add the DOI badge here once the release is created.

## License

Released under the MIT License. See `LICENSE`.
