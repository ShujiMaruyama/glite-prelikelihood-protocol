# Glite pre-likelihood protocol

[![DOI](https://zenodo.org/badge/1250763079.svg)](https://doi.org/10.5281/zenodo.20404263)

## Archived release

- Zenodo archived release: https://doi.org/10.5281/zenodo.20404264
- Concept DOI for all versions: https://doi.org/10.5281/zenodo.20404263
- Related V152 reproducibility archive: https://doi.org/10.5281/zenodo.20390399

Glite is a reproducible, low-resource pre-likelihood triage scaffold for scalar-tensor modified-gravity branches. It generates deterministic fixture data, figures, control vectors, threshold sweeps, and a SHA-256 manifest for an illustrative logarithmic-density scalar-tensor branch.

This repository is prepared for a SoftwareX original software publication as `v1.0.0-softx`. It is derived from the earlier all-rights-reserved V152 Zenodo reproducibility archive:

- V152 archive DOI: 10.5281/zenodo.20390399
- V152 concept DOI: 10.5281/zenodo.20390398

## Claim boundary

This software is not a Boltzmann solver, likelihood engine, posterior sampler, model-ranking code, Solar-System solver, or observational validation. It is a deterministic pre-likelihood audit scaffold. Passing the declared gates grants only permission for subsequent backend implementation.

The package does **not** claim:

- observational evidence;
- posterior constraints;
- Bayesian model selection;
- Solar-System viability;
- a true Hu-Sawicki f(R) production comparison;
- production-inference validity.

## Contents

- `scripts/generate_all_fixtures.py` - regenerate deterministic CSV fixtures and figures.
- `scripts/check_artifact_manifest.py` - verify SHA-256 hashes listed in `data/artifact_hash_manifest.csv`.
- `data/` - benchmark responses, closure-family stress fixtures, protocol controls, threshold sweeps, synthetic external precheck, and manifest.
- `figures/` - generated fixture figures.
- `run_cards/` - declared run-card and gate thresholds.
- `docs/` - claim boundary, SoftwareX notes, prior DOI record, and reproducibility instructions.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_all_fixtures.py
python scripts/check_artifact_manifest.py --manifest data/artifact_hash_manifest.csv --root .
```

Expected terminal output:

```text
Generated Glite v1.0.0-softx fixtures in <repository>
Manifest verification PASSED
```

## Outputs

The main generated artifacts are:

- `data/benchmark_responses.csv`
- `data/closure_family_stress.csv`
- `data/external_constraint_precheck.csv`
- `data/protocol_control_calibration.csv`
- `data/protocol_control_input_vectors.csv`
- `data/threshold_sweep.csv`
- `data/xi_gate_sequence.csv`
- `figures/fig_locked_responses.{pdf,png}`
- `figures/fig_transfer_matrix_scan.{pdf,png}`
- `figures/fig_xi_gate_sequence.{pdf,png}`
- `figures/fig_failure_decision_flow.{pdf,png}`

## Citation

Please cite the V152 reproducibility archive and, once available, the SoftwareX publication:

```text
Maruyama, S. (2026). Pre-Likelihood Viability Protocol for a Logarithmic-Density Scalar-Tensor Branch - V152 Reproducibility Package (Version V152). Zenodo. https://doi.org/10.5281/zenodo.20390399
```

## License

- Python source code: MIT License.
- Data fixtures, run cards, figures, and documentation: CC BY 4.0 unless otherwise stated.
