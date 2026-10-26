# RIMS c38 — first physically grounded diagnosis of the frozen negative-curvature shooting failure

**Date:** 2026-10-26 JST. **Author:** Shuji Maruyama, Independent Researcher, Muroran, Hokkaido, Japan. © 2026 Shuji Maruyama. All rights reserved.

## Actual, independently inspected native evidence

GitHub Actions [c37 Run #5 / 40277614362](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40277614362) concluded **SUCCESS**. The static job had **100/100 PASS**; CLASS V18.29 pinned build and the *single deliberately repeated* first normalization `Class.compute()` of fixed `rims_002` both executed. The compute **failed** as intended and emitted a complete `CosmoComputationError`; the diagnostic succeeded because the prior failure was reproduced and its 1,426-byte exception plus 1,735-byte traceback were archived. The source run is not a valid physical background solution.

Original GitHub physical artifact ID **12630937571**, unchanged ZIP SHA256 **`795171946cdbe1ddb3e0f220ecbf73e9e1d81427262d6dab24dbc03b6ea44e1a`**, all **eight** interior SHA256 checks passed. The first 1,000 characters of the newly captured full error independently SHA256 to `eb8b7a6e5e52cec209141a7c359c5e6947b5479bb076df592558853b41b4beaf`, **identical** to the truncated error stored in the executed c35 Run #2. The frozen 81-case grid SHA256 is `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`; `rims_002` original case SHA256 `9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284`. One rerun is **not a fourth unique physical parameter point**.

## Physical-code direct stopping condition, NO artificial gate relaxation

Complete nested traceback pinpoints:
`input_find_root` → `background_init` → `background_solve` → `evolver_ndf15` → `background_derivs` → **`background_functions(L:624)`**, triggering the **RIMS source-specific** guard

```c
class_test((pba->rims_enforce_stability == _TRUE_) &&
           (pvecback[pba->index_bg_rims_stability_margin] < -pba->rims_stability_tolerance),
           pba->error_message, ...);
```

Grounding source: `rims_o3_patch/base_parts/part01` implements
`rims_meff2 = ddV_scf + 3 * rho_idm * rims_mass_curvature(phi)`,
`rims_stability_margin = rims_meff2 / H²`, with actual enforcement of `margin < -tolerance`. No altered physics or patched threshold was used to obtain c37.

**Reported by native C on exit** (rounding of printed numbers acknowledged):

| Measured source variable | Value |
|---|---:|
| Scale factor `a` | `3.945905e-10` |
| Corresponding *approximate* `z=1/a-1` | `2.534272872e9` |
| `m_eff²/H²` | `−1.004939e−10` |
| Enforced lower bound | `−1.000000e−10` |
| Threshold overshoot | **`4.939e−13`** |
| Relative overshoot to tolerance | **0.4939%** |

The local instantaneous formal scale `sqrt(|m_eff²|)/H≈1.00247e−5` is tiny. **This is not a bound on integrated instability, and not proof that the negative value is numerical noise.** The effective mass sign can arise from interplay between the scalar potential curvature and matter-coupling curvature; the present trace lacks the independent physical contributions at the rejection point, and no direct convergence or precision test has been executed.

### Claim boundary

The previous diagnosis “only a shooting guess failure” was **incomplete**: shooting reports the error because the evolving background triggers a **hard, explicit RIMS effective-mass stability veto** at very small scale factor. Whether that slight veto violation is robust under integration precision, represents a genuine tiny tachyonic branch, or indicates a mathematical/implementation inconsistency remains **unresolved**. Raising `rims_stability_tolerance` or setting `rims_enforce_stability=no` and reporting a solved cosmology would invalidate the original safety protocol; **prohibited as a success claim**.

The immutable original c35 status is `SOLVER_FAILED`. Underlying unique frozen 81 inputs: **3 attempted, 2 final background solved, 1 failed, 78 unattempted**. c37/c38 do not increase the unique-case count; no posterior, full 81-run, evidence/Bayes factor, complete observational forward transfer or distinct tensor/gradient safety result exists.

## Next predeclared HARD GATE (not executed yet)

1. Retain identical cosmological parameters and the same `rims_stability_tolerance = 1e−10`, `rims_enforce_stability=yes`. Instrument the FAIL branch with **separately logged raw source values** of `ddV_scf`, `rho_idm`, `rims_mass_curvature`, `H`, `phi`, `s` at its first failing step. Give this changed diagnostic C source an explicit new hash and keep original sources/receipts intact.
2. Resolve each contribution `V_{,φφ}/H²` and `3 ρ_idm (m_{,φφ}/m)/H²`. Inspect whether sign reversal follows physical terms or catastrophic numerical cancellation; use raw precision, not printed `%e` values, for a convergence decision.
3. Run a *separately manually authorized*, predeclared numerical convergence bracket (two or more tolerances) while retaining **all** solver outcomes and exact thresholds. Do not silently accept an unstable trajectory, filter failures, choose a new initial condition or generalize from one state.
4. Only after hard-gate numerical verdict: determine early-time EFT/BBN consistency, tensor/gradient/hyperbolicity and actual matched model observables. No observational superiority or uniqueness without a valid forward model and competitor reproduction.

## Reproducibility package

Independent local read-only ZIP: `RIMS_C38_EXACT_STABILITY_THRESHOLD_FORENSIC_20261026.zip`, SHA256 **`51e9e710da994d806d89b6827ecdfed968aa61260e910c37e55b5556fb3bc6f5`**. It embeds the *byte-identical original c37 GitHub artifact*, an executable, source-hash-and-frozen-case-gated independent Python audit, JSON result, full Japanese research analysis and **5/5 offline unittest PASS**. The package does **not** create a new CLASS physical run; audit is read-only.

**Scientific novelty gate:** a marginal instability point is a forensic result, not a unique prediction. Continue enforcing prior-art comparison against scalar-dependent DM and fifth-force/Euler models; retain native RIE/RMI and other perturbation-mode capabilities without conflating them with this background diagnostic.
