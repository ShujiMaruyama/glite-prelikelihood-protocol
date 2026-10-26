# RIMS c35 — preregistered occupation-only source-contrast (2026-10-26)

**Scientific scope**: one actual previously executed physical background plus **two planned** new fixed input cases. NOT a completed 81-case scan, CLASS transfer likelihood, MCMC, model preference, or proof of uniqueness. RIMS remains separate from IFC/PORG/PBH-Hawking.

## Immutable evidence

- Real native CLASS Run #3 [40247625798](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40247625798), case `rims_000`, 4 successful native CLASS computes, archived ZIP SHA256 `5263f9489ada68adcc76c6d5e756ea95b3dfff40dec2448d2f87cea0efbe85dd`.
- Frozen 81-case manifest SHA256 `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.
- The original c24 physical verdict is `PHYSICAL_REJECT` due **only** to native grid endpoint rule; independent c32 verdict is `NATIVE_GRID_BRACKETED_SAMPLED_PASS`. Neither certifies continuum/perturbative stability.
- No new native CLASS computes were performed by c35 when this checkpoint was written.

## New source-identity check

From the original 40,000-row final CLASS z/phi source time series and the separately exported 1,721 retained native z<=3 samples, **all 1,721 redshifts join exactly by value and original row index** after reversing the descending full time-series order. Full-source `s(phi)` and stored sampled s are numerically identical for every row, to stored binary64 accuracy. This checks CLASS internal output identity, **not independent observational reproduction**.

For the physically executed `rims_000` weak-coupling corner:
- `delta_phi_native = 0.012889285584219756`.
- `delta_beta_native = 2.3166272618627137e-7`.
- Maximum curvature departure of beta(phi) from its endpoint secant = `5.974425815180595e-12`, **6.637002235090118e-10 relative to mean beta**.

These quantify the difficulty of detecting RIMS-specific nonlinearity in this *intrinsic source-function* signal; they are **not survey forecasts or galaxy observables**.

## Physics-grounded, preregistered controlled contrast

Source-exact m(phi)/m_ref=sqrt(s/s_ref) implies `beta=alpha_U(1-s)` and `m''/m=alpha_U^2(1-s)(1-3s)`. The sign changes at s=1/3, but this is **NOT** the total scalar mass m_eff² nor an independent dynamical prediction. The frozen input design fixes three consecutive exact cases with same potential, alpha_U, omega_phi0 and background parameters; phi_transition necessarily changes when s_i is changed.

| Case | Initial s_i | Theory m''/m sign | Initial beta from source | Conditional 2beta² proxy | Physical case status |
|---|---|---|---|---|---|
| `rims_000` | 0.10 | positive | 0.009 | 0.000162 | already completed in c32 only |
| `rims_001` | 1/3 | zero | 0.0066666667 | 0.00008888889 | **not executed** |
| `rims_002` | 0.65 | negative | 0.0035 | 0.0000245 | **not executed** |

The contrast is designed to make **numerical physical viability** of each case and source-bound evolution falsifiable; a zero mass-curvature term at the *initial* point does not mean the total effective mass vanishes or that the term remains zero at later times.

## Physically runnable GitHub source and failure-retaining audit

- `mcmc_o3/c35_frozen_pair_run.py` — user-manual-only, two specified cases `rims_001` and `rims_002`, separate subprocesses with 600 seconds per case, preserving solver failures, timeout/error logs, original receipts and no selection. The previously successful `rims_000` is **not rerun**. No `--all-81` mode.
- `mcmc_o3/c35_pair_audit.py` — independently examines the *exact* two source cases, 79 absent physical attempts in the new batch, c24 conservation of failure/provenance, c26 early occupation, c27 full native history SHA, and c32 isolated source-native z3 bracket for each completed case; no silent relabeling of c24 `PHYSICAL_REJECT`. Any physical solver failure remains physically failed, irrespective of whether the GitHub evidence archiving step succeeded.
- `mcmc_o3/test_c35_frozen_pair.py` — **10 new source/selection/timeout/no-rerun offline test cases**, intended alongside prior c32 suite 82 = **92 static tests, not yet executed**.
- `.github/workflows/rims-phaseii-c35-frozen-occupancy-pair.yml` — registered on main and c35 branch, `workflow_dispatch` ONLY, `run_mode=static-only` default, `pair-2` only after explicit user action. No cron/push, MCMC, all81 run, or automatic follow-on.

## Local cumulative independent audit

Complementary local package `RIMS_C35_SOURCE_MATCH_AND_FROZEN_PAIR_20261026.zip` retains unchanged c34 and c32 evidence archives, separate `references.bib`, full science note and an original-read-only source-matcher with **18/18 local tests PASS**. The GitHub executable source is not a byte-identical copy of the local forensic script: they perform **different** purposes and are separately described. The 92-test GitHub suite and the new two real native cases are NOT yet verified by GitHub Actions.

Prior work already covers scalar-dependent dark matter masses, generic fifth forces, RSD/WL modified-gravity degeneracies and Euler/gravitational-redshift testing (Castello et al. PRD 110, 103523, 2024; Nature Communications 2025 DOI 10.1038/s41467-025-65100-8). Unique RIMS forward predictions require gauge-consistent real perturbations across native RIE/RMI and five standard modes plus nuisance-matched multi-channel tests. No production claims before GetDist R−1<0.01 and minimum headline ESS≥1000, independent parity, covariances, nonlinear cut and second solver.
