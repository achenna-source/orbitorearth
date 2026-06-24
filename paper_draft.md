# When Does AI Compute Belong in Orbit? A Workload-Conditioned, Multi-Criteria Decision Framework for Orbital Data Centers

**Target venues:** IEEE Access; IEEE Transactions on Sustainable Computing (secondary: ACM e-Energy / HotCarbon).
**Paper type:** characterization and decision framework (analysis). NOT a hardware architecture, NOT a scheduler.
**Status:** v0 skeleton. Numbers and results are filled progressively as parameters are sourced.
**Placeholders:** `[À REMPLIR]` = value to source; `[FIG n]` = figure; `[TABLE n]` = table; `[DERIVED]` = transparent build-up, not a citation.
**Integrity rule:** no fabricated value or reference. A value enters only when sourced (primary/peer-reviewed) or explicitly derived-and-traced.

---

## Abstract

> Artificial intelligence now consumes electricity and water faster than terrestrial data centers can sustainably supply. Several operators propose a radical alternative: place AI compute in orbit, where sunlight is continuous and waste heat radiates into space. Early assessments disagree by an order of magnitude, one camp reporting near carbon-neutral orbital data centers, another up to ten times worse once launch is fully accounted. We show this gap is not a contradiction but two camps sampling different regions of one parameter space, and, decisively, choosing different climate metrics: direct launch CO2 versus CO2-equivalent including high-altitude radiative forcing, which the literature shows dominates rocket climate impact. We develop a workload-conditioned decision framework that says when orbital placement lowers the environmental cost of AI compute and when it does not. We propose no new hardware and no scheduler; we characterize the conditions. A per-kW lifecycle break-even model with Monte-Carlo uncertainty isolates the technical levers (displaced grid intensity, launch accounting, GPU lifetime, radiator mass per kW) and one workload lever: data provenance, born in orbit versus Earth-origin, crossed with latency class. At a representative configuration the break-even grid intensity spans roughly 0.06 to 1.5 kgCO2/kWh as the climate metric moves from direct launch CO2 to CO2-equivalent with high-altitude forcing — over an order of magnitude, driven almost entirely by that choice (Monte-Carlo 90% interval [0.08, 0.62] under embodied, direct-CO2). Under direct-CO2 accounting orbit beats most grids; under CO2e-with-forcing it beats almost none, which is precisely the two camps' disagreement. We evaluate carbon together with water, latency, and orbital debris as a dominance profile rather than a single score, and release OrbitOrEarth, an open calculator that lets either camp replay its assumptions. Processing Earth observation where it is captured is the clearest case for orbit; interactive inference for ground users is the clearest case against.
>
> *(All break-even levers are now sourced; the two second-order terms — orbital manufacturing and avoided ground construction — are set to zero pending sourcing and act in opposite directions. Brief's preliminary envelope was 0.06–0.88 kgCO2/kWh.)*

## Index Terms

Sustainable computing, orbital data center, AI compute placement, life-cycle carbon, multi-criteria decision, workload taxonomy, satellite edge computing, reproducible artifact, radiative forcing.

---

## I. Introduction

The electricity and water demands of artificial intelligence are growing faster than terrestrial data centers can sustainably meet. Data centers and data-transmission networks already drew on the order of 1 to 1.5 percent of global electricity and released roughly 0.9 percent of energy-related greenhouse gases in 2021, and their local burden is acute where grids are dirty or water is scarce: data centers account for about 7 percent and 21 percent of national electricity in Singapore and Ireland respectively, and data centers in the United States consumed on the order of 620 billion litres of water in 2019. The current surge in AI training and inference is accelerating this trajectory `[À SOURCER: current AI-specific energy projection]`, and the binding constraint is increasingly the carbon intensity of the grid a data center can reach. This raises a question that until recently sounded fanciful: should some AI compute leave the grid entirely?

Several operators now propose exactly that. In orbit, sunlight is nearly uninterrupted and deep space is a vast cold sink into which waste heat radiates without water. Within two years, Google's Project Suncatcher (with radiation-tested accelerators and a sun-synchronous design point), SpaceX, Starcloud, the EU-backed ASCEND feasibility study, and China's Star-Compute / Three-Body constellation have moved orbital data centers from speculation toward engineering. These concepts converge on sun-synchronous low-Earth orbit; in its dawn-dusk variant the spacecraft sees near-continuous sunlight, so that operational carbon approaches zero — the property on which every optimistic assessment rests.

Yet the assessments that should guide such investments disagree by an order of magnitude. An optimist pole, in a Nature Electronics analysis from NTU, Zhejiang and KAIST, holds that orbital data centers can be carbon-neutral within a few years of operation, under a life-cycle carbon-usage-effectiveness metric in which operational carbon is zero. A pessimist pole, the "Dirty Bits in Low-Earth Orbit" study from Saarland University, finds that even under optimistic assumptions in-orbit systems are up to an order of magnitude worse than terrestrial equivalents once the embodied carbon of launch and re-entry is fully counted. Both rest on the same physics; both are peer-reviewed; their conclusions are opposite. A decision-maker reading this literature cannot tell whether orbit is a climate solution or a climate liability.

We argue that this is not a genuine scientific contradiction. Reproducing both poles within a single per-kilowatt lifecycle model, we find their disagreement reduces to a small set of technical parameters — chiefly the displaced grid intensity, how launch emissions are accounted, GPU lifetime, and radiator mass per kilowatt — and, decisively, to a choice of climate metric. Counting only direct launch CO2 places the break-even near 0.06 kgCO2/kWh, where orbit beats most grids; counting the full CO2-equivalent including the high-altitude radiative forcing that atmospheric-science work shows dominates rocket climate impact raises it above 1.5 kgCO2/kWh, where orbit beats almost none. Across the realistic range of system mass these choices trace three break-even contours (Figure [break_even_map]); the optimist and pessimist poles are the outer two, and the carbon-intensive grids on which AI actually runs fall in the metric-dependent band between them. The two poles are sampling opposite ends of one continuum, not contradicting each other.

The framework also yields actionable guidance, and one case stands out: processing Earth-observation data where it is captured — data born in orbit, under no strict latency budget — is the clearest setting for orbital placement, whereas interactive inference for ground-based users is the clearest setting against it (full treatment in Section V-F). What has been missing is a computing-side framework that adjudicates such cases. Prior work performs life-cycle accounting, proposes orbital architectures, or issues warnings, and one analysis places workloads between orbital and terrestrial clouds by carbon alone; none offers a workload-conditioned, multi-criteria decision rule, and none has examined the disagreement itself as a choice of climate metric.

This paper makes five contributions. **C1**, its spine, shows that the optimist-pessimist disagreement over orbital-compute carbon reduces to a small parameter set and, decisively, to the climate-metric choice (direct CO2 versus CO2-equivalent with high-altitude forcing), reconciling two contradictory literatures within one model. **C2** is a per-kilowatt lifecycle break-even model with traceable, sourced parameters and Monte-Carlo uncertainty propagation that isolates the levers determining the verdict. **C3** is a two-axis workload taxonomy (data provenance × latency class) and a decision rule mapping a workload, grid, launch vehicle and metric to an orbit-or-ground recommendation with a confidence level. **C4** evaluates carbon together with water, latency and orbital debris as a dominance profile rather than a single weighted score. **C5** is OrbitOrEarth, an open calculator that reproduces the sweep, the tornado and the decision map, letting either camp replay its own assumptions.

The remainder of the paper is organized as follows. Section II positions the work against the optimist-pessimist spectrum and existing analyses. Section III defines the reference orbit and the per-kilowatt break-even model. Section IV reports the sourced parameters and reconciles the two camps under each metric. Section V develops the workload taxonomy, the decision rule, the multi-criteria profiles and worked cases. Section VI discusses limitations and threats to validity, and Section VII concludes.

## II. Background and Related Work

*Intent: position precisely; differentiate from prior orbital analyses AND from LCA/architecture work.*

- **A. Real projects.** Suncatcher (dawn-dusk SSO ~650 km), SpaceX and Starcloud (SSO) all converge on sun-synchronous LEO for continuous solar. Three-Body / Star-Compute (China) is Earth-observation compute, likely a classic 10:30 SSO with eclipses: it is the born-in-orbit EO case study (Sec. V-F), not a dawn-dusk convergence point. `[À REMPLIR — SOURCED]`
- **B. The carbon controversy: a spectrum, not a binary.** Published estimates span an order of magnitude; the optimist and pessimist poles are the extremes of one continuum that C1 parameterises. *Optimist pole* — Aili, Choi, Ong & Wen (NTU + Zhejiang + KAIST), *Nature Electronics* 2025 Perspective (DOI 10.1038/s41928-025-01476-1): frameworks for orbital edge and cloud data centres that can be carbon-neutral, with a life-cycle carbon usage effectiveness (CUE) method and a carbon-aware multicloud that places workloads on orbital vs terrestrial clouds by CUE. *Pessimist pole* — Ohs, Stock, Schmidt, Fraire & Hermanns (Saarland), *Dirty Bits in LEO* (arXiv 2508.06250, ACM SIGENERGY Energy Informatics Review 2025), ESpaS tool: even under optimistic assumptions, in-orbit systems are up to an order of magnitude worse than terrestrial (CO2e), driven by embodied launch and re-entry. *Between the poles*: ASCEND (Thales Alenia / EU Horizon 2024), an industrial feasibility study, optimist-conditional on a launcher ~10x less emissive; the tether architecture (arXiv 2512.09044), tethered-chain concept with envelope CO2 estimates. Adjacent lifecycle analyses we also draw on: a LEO-constellation launch LCA (arXiv 2504.15291) and an orbital-DC impact analysis at ~500 km (arXiv 2603.28829).
- **C. The thermal wall.** Radiation-only cooling, T^4 law; imported as an input, not claimed. `[À REMPLIR — SOURCED]`
- **D. The carbon AND the metric controversy.** Direct CO2 is not the dominant rocket climate forcer; black carbon and alumina dominate radiative forcing (Ross & Sheaffer 2014). The two poles differ precisely in accounting boundaries: the optimist counts operational carbon (approximately 0 in orbit) with launch amortised over lifetime, while the pessimist counts embodied launch and re-entry under a CO2e metric. C1 formalises this on our own model: the disagreement is a choice of metric and boundary, not of physics. `[À REMPLIR — SOURCED: Ross & Sheaffer; DLR/Acta Astronautica]`
- **E. Differentiation table (Table 1).** Filled and verified against the primary papers. The discriminating columns are multi-criteria and workload-conditioning: the only prior decision element (NTU's carbon-aware multicloud) places by carbon alone and is not workload-conditioned. The unique combination is a workload-conditioned, multi-criteria decision rule plus an open artifact.

| Prior work | Lifecycle CO2? | Architecture? | Decision rule? | Multi-criteria? | Open artifact? |
|---|---|---|---|---|---|
| NTU / Nature Electronics (optimist) | Yes (CUE) | Partial (frameworks) | Partial (carbon-only placement) | No | No |
| Saarland / Dirty Bits, ESpaS (pessimist) | Yes | No | No | No (carbon only) | Yes (ESpaS) |
| Tether architecture (arXiv 2512.09044) | No (envelope) | Yes | No | No | No |
| ASCEND (Thales / EU) | Yes | Yes | No | Partial (carbon, water) | No |
| **This work** | **No (decision framework)** | **No** | **Yes (workload-conditioned)** | **Yes (carbon+water+latency+debris)** | **Yes (OrbitOrEarth)** |
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
