# When Does AI Compute Belong in Orbit? A Workload-Conditioned, Multi-Criteria Decision Framework for Orbital Data Centers

**Target venues:** IEEE Access; IEEE Transactions on Sustainable Computing (secondary: ACM e-Energy / HotCarbon).
**Paper type:** characterization and decision framework (analysis). NOT a hardware architecture, NOT a scheduler.
**Status:** v0 skeleton. Numbers and results are filled progressively as parameters are sourced.
**Placeholders:** `[À REMPLIR]` = value to source; `[FIG n]` = figure; `[TABLE n]` = table; `[DERIVED]` = transparent build-up, not a citation.
**Integrity rule:** no fabricated value or reference. A value enters only when sourced (primary/peer-reviewed) or explicitly derived-and-traced.

---

## Abstract

> Artificial intelligence now consumes electricity and water faster than terrestrial data centers can sustainably supply. Several operators propose a radical alternative: place AI compute in orbit, where sunlight is continuous and waste heat radiates into space. Early assessments disagree by an order of magnitude, one camp reporting near carbon-neutral orbital data centers, another up to ten times worse once launch is fully accounted. We show this gap is not a contradiction but two camps sampling different regions of one parameter space, and, decisively, choosing different climate metrics: direct launch CO2 versus CO2-equivalent including high-altitude radiative forcing, which the literature shows dominates rocket climate impact. We develop a workload-conditioned decision framework that says when orbital placement lowers the environmental cost of AI compute and when it does not. We propose no new hardware and no scheduler; we characterize the conditions. A per-kW lifecycle break-even model with Monte-Carlo uncertainty isolates the technical levers (displaced grid intensity, launch accounting, GPU lifetime, radiator mass per kW) and one workload lever: data provenance, born in orbit versus Earth-origin, crossed with latency class. The break-even grid intensity ranges from [À REMPLIR] to [À REMPLIR] kgCO2/kWh across realistic configurations and flips inside the plausible envelope; under CO2e-with-forcing the threshold shifts further, reconciling the two camps. We evaluate carbon together with water, latency, and orbital debris as a dominance profile rather than a single score, and release OrbitOrEarth, an open calculator that lets either camp replay its assumptions. Processing Earth observation where it is captured is the clearest case for orbit; interactive inference for ground users is the clearest case against.
>
> *(Headline numbers preliminary; updated when the sweep is re-run on sourced inputs. Brief's preliminary envelope was 0.06–0.88 kgCO2/kWh.)*

## Index Terms

Sustainable computing, orbital data center, AI compute placement, life-cycle carbon, multi-criteria decision, workload taxonomy, satellite edge computing, reproducible artifact, radiative forcing.

---

## I. Introduction

*Intent: motivate, state the gap, lead with the metric-reconciliation contribution, front-load the Earth-observation teaser, list contributions, roadmap.*

- **A. The sustainability crisis of AI compute.** Energy and water strain of terrestrial AI data centers. `[À REMPLIR: grid intensities, water figures — SOURCED]`
- **B. The orbital proposal.** Google Suncatcher, Starcloud, China's Star-Compute / Three-Body. `[À REMPLIR — SOURCED]`
- **C. The order-of-magnitude disagreement.** Optimist camp (near carbon-neutral) vs pessimist camp (up to 10x worse). Name the camps (NTU vs Saarland). `[À REMPLIR — SOURCED]`
- **D. Teaser of the worked decision.** Earth observation processed in orbit as the clearest "orbit wins" case (full treatment in Sec. V-F).
- **E. The gap.** No computing-side framework adjudicates who is right and for which workload; and the disagreement has not been examined as a *climate-metric choice*.
- **F. Contributions.**
  - **C1 (spine).** We show the optimist/pessimist disagreement reduces to a small parameter set and, decisively, to the climate-metric choice (direct CO2 vs CO2e with high-altitude forcing).
  - **C2.** A per-kW lifecycle break-even model with traceable sourced parameters and Monte-Carlo uncertainty propagation.
  - **C3.** A two-axis workload taxonomy (data provenance × latency) and a decision rule mapping (workload, grid, vehicle, metric) → orbit/ground + confidence.
  - **C4.** A multi-criteria evaluation (carbon, water, latency, e-waste/debris) as a dominance profile, not a single weighted score.
  - **C5.** OrbitOrEarth, an open calculator reproducing the sweep, the tornado, and the decision map.
- **G. Roadmap.**

## II. Background and Related Work

*Intent: position precisely; differentiate from prior orbital analyses AND from LCA/architecture work.*

- **A. Real projects.** Suncatcher (dawn-dusk SSO ~650 km), SpaceX and Starcloud (SSO) all converge on sun-synchronous LEO for continuous solar. Three-Body / Star-Compute (China) is Earth-observation compute, likely a classic 10:30 SSO with eclipses: it is the born-in-orbit EO case study (Sec. V-F), not a dawn-dusk convergence point. `[À REMPLIR — SOURCED]`
- **B. Existing analyses.** Nature Electronics piece; ESpaS "Dirty Bits" tool; tether architecture; ASCEND study. `[À REMPLIR — SOURCED]`
- **C. The thermal wall.** Radiation-only cooling, T^4 law; imported as an input, not claimed. `[À REMPLIR — SOURCED]`
- **D. The carbon AND the metric controversy.** Direct CO2 is not the dominant rocket climate forcer; black carbon and alumina dominate radiative forcing (Ross & Sheaffer 2014). `[À REMPLIR — SOURCED]`
- **E. Differentiation table.** `[TABLE 1 — columns: prior work | does an LCA? | proposes architecture? | gives a decision rule? | multi-criteria? | open artifact? | rows: each prior; last row: ours]`
- **F. Explicit positioning.** Neither an LCA nor an architecture, but a decision framework.

## III. System Model and Assumptions

*Intent: the model, the metric definition, the parameters with provenance.*

- **A. Per-kW lifecycle model.** System boundaries: launch, bus, radiator, solar, avoided terrestrial DC construction, water (electricity + cooling). GPU manufacturing assumed equal both sides, cancels.
- **A-bis. Reference orbit (structural keystone).** Dawn-dusk sun-synchronous LEO; nominal ~650 km (Suncatcher, the most concrete program), altitude swept 500-1600 km as a sensitivity axis (not a fixed central). Continuous solar (no eclipse) gives operational carbon approximately 0, valid for dawn-dusk specifically, NOT generic SSO. Altitude couples to four downstream quantities: launch CO2 (delta-V), black-carbon forcing, radiation/GPU lifetime, and latency. Sourced: Suncatcher ~650 km dawn-dusk SSO; SpaceX and Starcloud SSO; ~500 km analysis (arXiv 2603.28829); tether ~1600 km DDSS (arXiv 2512.09044).
- **B. The break-even equation.** `I* = ( M·f_launch + B − D ) / ( PUE·H·L·U )`. `[DERIVED — full derivation; reproduced in OrbitOrEarth]`
- **C. The metric definition (the spine).** Base metric = direct CO2, applied symmetrically to orbit and ground. Non-CO2 high-altitude forcing (black carbon, alumina, H2O) treated as an explicit axis, the pivot of the camp split. `[À REMPLIR — SOURCED: Ross & Sheaffer; DLR/Acta Astronautica]`
- **D. Parameters and provenance.** `[TABLE 2 — each parameter: symbol, value, [low, high], unit, what-measured, source/derivation, status. Mirrors params.yaml.]`
- **E. Multi-criteria metrics.** Definitions: carbon, water (gal/kW), latency (LEO propagation + ground-pass), e-waste/orbital debris (ordinal).

## IV. Method

*Intent: reproducible methodology.*

- **A. Analytical derivation** of the break-even threshold and the verdict condition `I_grid > I*`.
- **B. Sensitivity sweep + tornado** (lever ranking). `[FIG 1: tornado]`
- **C. Monte-Carlo uncertainty propagation** (the "confidence intervals"): triangular draws over sourced ranges → distribution of I* (median, 90% interval).
- **D. Workload taxonomy.** Provenance (born-in-orbit vs Earth-origin) × latency (batch vs interactive); how provenance shifts the break-even via uplink/downlink and latency terms. `[DERIVED — adjustment terms]`
- **E. The decision rule.** `[FIG 2: flowchart] (workload, grid, vehicle, metric) → orbit / ground + confidence.`

## V. Results

*Intent: decision regions and when the verdict flips; both metrics shown.*

- **A. Break-even tables** (sourced). `[TABLE 3]`
- **B. The flagship decision map** (provenance × technical) under direct CO2. `[FIG 3: break-even map, two provenance contours, reference grids]`
- **C. The metric-choice flip.** The same map under CO2e-with-forcing; the verdict moves. `[FIG 4: CO2 vs CO2e side by side]` — C1 made visible.
- **D. Reconciliation of the two camps.** Each camp = a region and a metric of the same space. `[À REMPLIR]`
- **E. Water-versus-carbon trade-off.** `[FIG 5]`
- **F. Worked decision.** Earth observation (orbit wins) vs interactive inference for ground users (ground wins). `[À REMPLIR — the front-loaded example, full here]`

## VI. Discussion

- **A. When orbit genuinely wins.** Born-in-orbit, batch, dirty displaced grid, lenient forcing accounting.
- **B. When it loses.** Earth-origin, interactive, clean grid, full forcing.
- **C. The metric choice as the crux.** Implications for how the community should report orbital-compute carbon.
- **D. Implications for AI compute siting.**

## VII. Limitations and Threats to Validity

*Intent: counter the "position + arithmetic" risk head-on.*

- **A. Inherited input uncertainty**, especially the launch factor and the forcing multiplier.
- **B. Metric honesty.** We show the verdict under BOTH metrics rather than pick one, pre-empting the "convenient metric" critique.
- **C. Vehicle projection risk.** Starship not yet flown; central case anchored on flown Falcon-class, Starship as forward-looking sensitivity.
- **D. Scope.** No scheduler, no custom thermal/orbital model, no full LCA.
- **E. Countermeasures.** Model rigor, multi-criteria evaluation, open artifact.

## VIII. Conclusion

`[À REMPLIR — summary; the decision rule's takeaway; the metric choice as the resolution of the debate.]`

## Reproducibility and Artifact

**OrbitOrEarth** — open calculator reproducing the sweep, the tornado, and the decision map; carries NTU-optimist and Saarland-pessimist presets; `params.yaml` with sourced provenance per parameter. `[link on publication]`

## References

`[Managed separately; every entry sourced and verified; no fabricated references. Linked APA/IEEE.]`
