# RIMS c36 — actual c35 paired physical-run forensic checkpoint

**Date:** 2026-10-26 JST. **Research branch:** RIMS only. This checkpoint is a *read-only investigation* of an executed two-case native CLASS run, not a new CLASS execution, not an 81-case scan, and not a detection or production posterior.

## Audited source

- GitHub Actions [Run #2 / 40269433141](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40269433141), executed code SHA `285e39a444ee0c13f677785cad9ee64a87bc4f2d`. GitHub overall status **SUCCESS**. Both `static-check` (92/92 PASS) and `frozen-occupancy-pair` jobs completed successfully.
- Original physical artifact `rims-c35-two-frozen-native-backgrounds`, GitHub ID **12627798137**, downloaded source ZIP SHA256 **`b5c5a80bf17a91069bf772f2f676949d3b77773d07dd79f25a631e405df1853c`**. All 11 SHA256SUMS entries verified independently. No original files altered.
- Frozen 81 SHA256: `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`. The run contained **exactly** `rims_001` and `rims_002`, not `rims_000`. Including archived c32 `rims_000`, **3/81 physically attempted, 2 solver-completed, 1 solver-failed, 78 not attempted**. Beware: overall GitHub SUCCESS signifies both attempts and evidence auditing finished; **it emphatically does not mean both cases are physically stable or solved**.

## Unaltered source-by-source findings

| Case | Frozen s_i | Initial sign of source mass curvature m,phi phi/m | Real native solver | Conservative c24 / distinct c32 |
|---|---:|---|---|---|
| rims_000 | 0.10 | POSITIVE | prior c32 solved | historical PHYSICAL_REJECT for endpoint grid / separate sampled-bracket PASS |
| rims_001 | 1/3 | ZERO | **four real native Class.compute successes**, three normalization and final background | historical PHYSICAL_REJECT only endpoint grid; independent c26 initial PASS, c27 full-source PASS, c32 **NATIVE_GRID_BRACKETED_SAMPLED_PASS** |
| rims_002 | 0.65 | NEGATIVE | **first native normalization Class.compute failed**; ZERO successful normalization solutions | original **SOLVER_FAILED**; no background history, no c26/c27/c32 physical source gate |

Native `rims_001`: 40,000-row original history, 1,721 native 0<=z<=3 samples, `min(m_eff²/H²)=0.00379089027507108`, `max Xi=0.28334313450091914`, `s_min=0.33300906098783195`, `s_max=0.3330490613767918`. At z=3 the true adjacent native bracket is (2.9995860999538064,3.0028107653487153) with mass/H² values (0.00379089027507108,0.003781894005469812). Both positive and raw-source identity checked. As `s(z)<1/3` for **all sampled 1,721 points**, `m,phi phi/m = alpha_U²(1-s)(1-3s)` is **positive** across that *sampled late epoch* despite exactly zero at the declared initial s_i=1/3. The sampled mass-function curvature lies [5.6878634471889544e-08,6.488601486649732e-08]. This is a source-mass derivative, **not** automatically the total scalar effective mass and not observational uniqueness.

`rims_002` from **original unaltered logs**: `CosmoComputationError` in `background_init`, with `Shooting failed, try optimising input_get_guess()` and nested `input_find_root` → `background_solve` → `evolver_ndf15`. It occurred during the first `normalization_background` attempt, in 0.008 s; receipt `normalization_iteration_success=false`. It is an **actual numerical setup/shooting failure**, not proof that physical solutions are absent or that negative source curvature equals an unstable total effective mass. Current `failure_message` was truncated to 1000 characters (and native event error to 500), ending before the innermost C derivative error details. This is a reproducibility blind spot: preserve the complete Cython/CLASS exception and source shooting diagnostics in a future independently authorized single-case run, with no arbitrary retuning, case selection, or automatic rescue.

## Scientific gate hierarchy

A solver failure is a recorded scientifically relevant outcome, but no `rims_002` physical solution exists in this run for stability, lensing, perturbation or observables. Native sampled-grid PASS for `rims_001` does **not** prove continuous non-tachyonicity, tensor/gradient perturbative safety, nonlinear correctness, an independently implemented second Einstein–Boltzmann solver, or matched Planck/DESI/Pantheon+ competitiveness. The broader RIMS novelty must be demonstrated against prior coupled dark sector / Euler / gravitational-redshift frameworks, not asserted because this intrinsic mass function changes sign.

No new CLASS/MCMC runs were dispatched as part of c36. **Never rerun c35 historical Run #2** or cherry-pick a replacement for `rims_002` and call it successful. The next appropriate action is full-error and numerical-shooting provenance instrumentation for the *same* failed frozen case, followed by a separately approved, bounded reproduction. Preserve `rims_000`, `rims_001` and the failed `rims_002` separately, even if the future diagnostic succeeds. Production criteria: GetDist R−1 < 0.01, minimum headline ESS >=1000.

## Release

Independent package: `RIMS_C36_C35_PAIR_FORENSIC_20261026.zip`, SHA256 **`a25b55dda6a3bb0936e4e1d2173706b276bdae6f2786017e223fb48211ea4038`**. Contains byte-identical original c35 artifact, machine-readable numeric and status report, and Japanese audit explanation. The GitHub branch stores corresponding decision records; it does not start any workflow or overwrite prior results.
