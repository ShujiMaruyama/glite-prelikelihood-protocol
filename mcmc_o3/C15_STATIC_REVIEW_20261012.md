# RIMS Phase II O3 c15 — static matched-control design (2026-10-12)

**Status: offline design only. NO CLASS/MCMC/Actions run dispatched.** This branch inherits c14's read-only review and adds the fixed c15 decision [JSON](./C15_MATCHED_CONTROL_STATIC_DECISION_20261012.json). The independently tested local package also contains the full generator, six Python unit tests, 16 YAML configurations, frozen covariance, fixed diagnostic eigenvector, and fail-closed observed-telemetry auditor; it is delivered separately as the `RIMS_c15_static_paired_preflight_20261012.zip` chat artifact, not as GitHub source files.

## What is fixed

The original c13b source archive SHA256 `acede0104b59aa72e177b6e056b954760bf5c1225d5692371e432359825430e3` and its 44 embedded checksums were verified. All c15 input proposals are defined with one frozen c13b ridge covariance (SHA256 `543c014fa0ba20d0219afeca339b34e473661940d8ff0fde8b9fe2b1c270da9b`), proposal scale 4.0, unchanged physical target/prior, and `learn_proposal=false`.

Two **different interpretive panels**, four fixed starts each: (1) independent reference-quantile LHS starts, drawn independently of c13b samples (NOT full-prior basin coverage), and (2) last recorded c13b accepted states (a conditional local transport diagnostic only, NOT inference or independent global starts). Each point has the same fixed start coordinates in two fresh configurations, and different RNG seeds. There are 16 prepared YAML configurations total.

The arms are 3-step and 27-step *predicted* Cobaya dragging with manual fast factors 27 and 243, nine slow sampled parameters and one fast `A_planck`. Cobaya's inherited `A_planck` prior is explicitly preserved from the c13b resolved config: `norm(loc=1,scale=0.0025)`. Its reference initial value is varied, not its prior. Generated target views hash to `275d9cfaa014e975f6dd44961ab962a5b4cc0d2adf834e5ad437504b779847c0`.

## Results actually executed

Six local unit tests passed: fixed source and manifest, matching of paired initial states, deterministic byte-for-byte regeneration, prior identity/periodicity mutation detection, and rejecting missing or mismatched synthetic runtime telemetry. **No new chain sample or physical likelihood evaluation exists at c15.**

## Blocking conditions, not yet met

Before any MCMC run, each of the eight distinct starts requires a finite RIMS CLASS and likelihood preflight and a *runtime* resolved-target identity comparison. A verified per-chain counter of **actual uncached CLASS calculations** is required. Without these, equal 18-minute wall times are not matched-cost samples and the pairwise 3 vs 27 efficiency comparison is NOT admissible. The fail-closed verifier requires slow-call budgets to match within 5%, actual runtime step counts, initial-state checks, and full telemetry. **No workflow was added; any future numerical run requires separate explicit authorization.**

All c10t/c11s/c12/c13/c13b/c14/c15 diagnostics are nonproduction. Gates remain **GetDist R−1 < 0.01** and **minimum headline ESS ≥1000**. No production posterior, Bayes factor, RIMS model preference, or ΛCDM competitiveness is claimed.
