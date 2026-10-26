# RIMS c39 — Native effective-mass source decomposition at the UNCHANGED stability veto

**Dated:** 2026-10-26 JST. **Author:** Shuji Maruyama. © 2026 Shuji Maruyama. All rights reserved.

## Exact baseline and non-negotiable claim boundary

- Actual c37 GitHub Actions [Run #5, 40277614362](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40277614362): 100/100 Python static checks passed; original frozen `rims_002` first native CLASS normalization `Class.compute()` failed **again** (expected diagnostic outcome). Source exception 1,426 bytes, original c35 first-1,000-character error digest matched.
- Early-time native rejection at `a≈3.945905e−10`, `m_eff²/H²≈−1.004939e−10`; the original gate was `m_eff²/H² < −1.0e−10`, approximately `4.939e−13` beyond its threshold, ~0.4939% of the threshold. **Printed values have limited digits**; no unrounded term-level data existed in that run.
- c38 read-only interpretation did **not** establish whether `rims_002` failure is caused by potential curvature, coupled-DM curvature, cancellation, integrator precision or inconsistent initial conditions. No mathematical physical no-go is established.
- Frozen input-81 SHA256: `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`; frozen case `rims_002` SHA256: `9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284`. Only **3 unique frozen cases have physical attempts**; 2 completed final native backgrounds; 1 solver-failed; 78 untouched. One repeated failed compute does **not** count as a new parameter point.

## What the original native code REALLY evaluates

The actual source in `rims_o3_patch/base_parts/part01` defines

```c
rims_meff2 = ddV_scf + 3.0 * rho_idm * rims_mass_curvature_value;
rims_stability_margin = rims_meff2 / (H * H);
class_test((rims_enforce_stability == _TRUE_) &&
           (rims_stability_margin < -rims_stability_tolerance), ...);
```

c39 **retains precisely this original formula, tolerance `1e−10`, and the original `class_test`**. No change to `s_i`, `alpha_U`, potential, `phi_t`, background `ic`, shooting guesses, normalization, or RHS dynamics is permitted.

The standalone `mcmc_o3/c39_instrument_stability_terms.py` inserts ONE `fprintf(stderr,...)` block **immediately before** the unmodified `class_test`, *only when the exact original veto condition becomes true*. It emits a uniquely tagged `RIMS_C39_TERMS_V1` record with 17 significant digits for:
`a`, `phi`, `s`, `H`, `Vpp=ddV_scf`, `rho_idm`, `mass_curvature=m,φφ/m`, `matter_term=3 rho_idm mass_curvature`, `raw_meff2`, `H²`, `ratio`, and `tolerance`. It leaves the original `class_test` source byte-identical and records the original/modified `background.c` SHA256. Byte-exact removal of the sole instrumentation block must reconstruct the original patched C source or the overlay refuses to run. The original upstream CLASS commit and BOTH frozen RIMS patch SHA256 checks are unchanged.

The independent `mcmc_o3/c39_audit_raw_stability_terms.py` checks:
- exact original case/freeze identity, **one** first native `Class.compute` attempt, intentionally reproduced shooting error and exact original c35 error-prefix hash;
- audit of the original physical C-source SHA256 before and after the overlay; original veto preserved, original tolerance unmodified;
- each and every logged native veto record independently satisfies **`matter_term=3 rho_idm mass_curvature`**, **`Vpp+matter_term=raw_meff2`**, **`H²=H×H`**, and **`ratio=raw_meff2/H²<−1e−10`**; verifies finite values, positive H, occupancy in (0,1);
- preserves ALL triggering records, does not pick a preferred one; any omitted/invalid record or nonreproduced c35 shooting result **fails closed**.

This **is NOT** a solved cosmological background, independent CLASS implementation, convergence check, tensor/gradient-stability proof, fifth-force detection, survey forecast or Bayesian evidence.

## Scientifically discriminating prospective outcomes

Define `A=Vpp/H²`, `B=3 rho_idm(m,φφ/m)/H²`, `M=A+B` at the first original native veto. Once measured:
- `A≥0, B<0`: initial direct evidence at the rejection point of *coupling-dominated negative effective mass*;
- `A<0, B≥0`: direct evidence of a *potential-curvature dominated negative contribution*;
- `A<0, B<0`: both physical source terms negative there;
- High cancellation condition number `K=(|A|+|B|)/|A+B|` may motivate dedicated numerical-precision and integration-convergence tests. **K alone is not evidence of an integration error.**

These conditions are proposed **classification gates**, not yet an observed partition or a unique RIMS discovery. If unexpected signs occur, retain them; do not adjust frozen parameters to obtain a desired physics story.

## Pre-registered operation; NO automatic physical run

- New manual-only workflow `.github/workflows/rims-phaseii-c39-source-terms-veto.yml` is registered on `main` and on dedicated research branch `rims-c39-native-stability-term-decomposition-20261026`.
- Default `run_mode=static-only`. Intended static tests: **110 (previous verified c37 100 + ten new c39 synthetic/regression tests)**. New total is **NOT yet verified by GitHub Actions**.
- Optional, separately authorized `run_mode=source-terms-one` runs the original case `rims_002` one first normalization compute using c37's full-exception recorder, with diagnostic-only source print and independent term audit. Hard shell timeout **240 seconds**; original patch check and new source-code SHA lock; physical rejection **must remain active**.
- No MCMC, no 81-case physical batch, no automatic retry, no full cosmological inference. A green GitHub result means *forensic capture and source arithmetic checked* and is **never** a background-viability certificate.
- Neither static nor native mode has been dispatched by this c39 checkpoint. No new source-term numerical values have been observed.

## Next hard scientific gate

1. Confirm 110 regression tests actually pass in GitHub Actions; repair any errors without changing the physics/source guards.
2. Only after static pass, manually authorize *one* real c39 native probe. Inspect both physical source signs, cancellation index and original gate at the EXACT rejection point, rather than trying to rescue shooting.
3. If the two-source decomposition is numerically consistent, predeclare convergence experiments at unchanged physical input and unchanged safety threshold (different solver error-control settings **only if demonstrably available, justified, and bounded**), retaining every successful/failed trial and SHA256.
4. Continue toward full perturbation tensor/hyperbolicity and matched observable signatures; do not infer `m_eff²` is necessarily the complete gauge-correct propagating eigenfrequency for every mode.
5. Production observational inference remains outside this diagnostic. Hard gate remains GetDist `R−1<0.01`, minimum headline ESS `≥1000`; no ΛCDM preference/Bayes factor/unique-detection claim without actual production artifacts.

This c39 development concerns RIMS ONLY. Do not mix with PORG, IFC, PBH/Hawking or unrelated research branches.
