# OrbitOrEarth

Reproducible decision model behind the paper *"When Does AI Compute Belong in
Orbit?"* It computes the break-even grid carbon intensity above which placing AI
compute in orbit emits less carbon than running it on the ground, per kW of IT
load, and propagates input uncertainty to a confidence interval.

## The model

Per kW, integrated over the GPU lifetime:

    I*  =  ( M * f_launch + B - D )  /  ( PUE * H * L * U )

Orbit emits less carbon than the ground baseline exactly when the displaced grid
intensity exceeds `I*`. All symbols and units are documented in `params.yaml`.

## Integrity

The default values in `params.yaml` are **placeholders**, reverse-engineered to
reproduce the preliminary envelope in the scoping brief (self-consistency check
only). They are **not** sourced. Every parameter marked `status: placeholder`
must be replaced with a cited value and a justified range before any number is
reported in the paper. No invented value is ever presented as real.

## Usage

    pip install -r requirements.txt
    python model.py --selfcheck   # reproduces the brief table (0.06 / 0.12 / 0.59 / 0.88)
    python model.py               # break-even + Monte-Carlo + water, current params
    pytest -q                     # test suite

A `Makefile` wraps these as `make selfcheck`, `make run`, `make test`.

## Files

- `params.yaml` - every parameter with value, [low, high] range, unit, source, status.
- `model.py` - break-even model, water, Monte-Carlo propagation, self-check.
- `test_model.py` - self-consistency and sanity tests.

## Status

Block 1 of the artifact: model core plus provenance scaffold. Next: source the
placeholders, then the parameter sweep and the break-even map (two provenance
contours) plus the tornado sensitivity plot.

## License

TBD (MIT suggested).
