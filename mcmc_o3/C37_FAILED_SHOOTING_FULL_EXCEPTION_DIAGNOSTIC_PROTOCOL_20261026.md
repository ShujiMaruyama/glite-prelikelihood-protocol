# RIMS c37 — single original CLASS shooting failure, full exception capture

**Date:** 2026-10-26. Author: Shuji Maruyama, Independent Researcher, Muroran, Hokkaido, Japan. © 2026 Shuji Maruyama. All rights reserved.

## Why this new gate exists

GitHub c35 Run #2 [40269433141](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40269433141) returned overall SUCCESS **because both attempts and their independent forensic audit completed**. The physical outcomes were unequal: `rims_001` successfully solved its native background; `rims_002` failed in the **FIRST** normalization `Class.compute()` (one attempt, zero successful native computes). Source error is `CosmoComputationError`, `background_init`, `Shooting failed`, `input_find_root`, `background_solve`, `evolver_ndf15`. The original native receipt stored **exactly 1,000 characters** of the exception, SHA256 `eb8b7a6e5e52cec209141a7c359c5e6947b5479bb076df592558853b41b4beaf`. The exception ended mid-C-call, so the underlying numerical derivative failure is unknown.

Frozen case `rims_002` SHA256 `9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284`; frozen 81-input design SHA256 `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`. Immutable c35 ZIP sha256 `b5c5a80bf17a91069bf772f2f676949d3b77773d07dd79f25a631e405df1853c`, ID 12627798137. c36 independent audit ZIP sha256 `a25b55dda6a3bb0936e4e1d2173706b276bdae6f2786017e223fb48211ea4038`.

## Exactly matched experimental intervention, without physics retuning

The new, **separate** `mcmc_o3/c37_exact_shooting_probe.py` calls the old, unchanged `c24_native_background.base_args` on *only* the original frozen `rims_002` and sets `rims_phi_ref=4.11730971054`, `rims_require_normalization="no"`; these are exactly the frozen source's original **first** normalization call. The tool pins the same upstream CLASS commit `e85808324f51fc694d12e3ed7439552a3c3f9540`, same frozen patch SHA pair, compiled Cython native module and unchanged model parameters. It makes **at most one** `Class.compute()` call. No shooting guess adjustment, solver-tolerance sweep, replacement potential, fallback initial condition, other case, original c35 re-run, full normalisation, MCMC, or likelihood occurs.

It records the **entire `str(exc)` as exposed by the Cython CLASS Python interface**, without an application-side 1,000-character cap, in `full_CLASS_exception.txt`. Also retains the Python traceback, raw full-process stdout/stderr, compiled native CLASS SHA256, exact first-call parameter JSON and its SHA256, duration, status and exception SHA256. An additional indicator checks the first 1,000 characters against the previous truncated source error SHA256. A matching high-level `Shooting failed` class **does not imply** the entire C root cause is identical; verify the stored prefix flag. CLASS itself could internally abbreviate an error before exposing it in `str(exc)`: this diagnostic cannot magically reconstruct a C stack or lost native-state information.

Reproduction statuses:
- `ORIGINAL_SHOOTING_FAILURE_REPRODUCED`: first native compute raises `CosmoComputationError` containing `Shooting failed`. **This is a deliberately reproduced failure, not successful physics**. The independent error-prefix hash check distinguishes exact c35 precursor from merely similar failure.
- `OTHER_ERROR`: a different exception is preserved; the GitHub diagnostic step fails, evidence archives nonetheless.
- `FIRST_COMPUTE_RETURNED_NOT_A_NORMALIZED_BACKGROUND`: first compute succeeded unexpectedly. Still **not** a complete mass-normalized solution; the diagnostic job flags the discrepancy without promoting the branch.

## GitHub execution firewall

Workflow `.github/workflows/rims-phaseii-c37-exact-shooting-diagnostic.yml` is registered on the default `main` branch and the dedicated c37 research branch. `workflow_dispatch` ONLY, no cron, no push trigger; static-only default. Run modes:
- `static-only`: prior 92 mock/static tests plus 7 new immutable-input, >1,000-character full-exception, no overwrite, atypical failure and status tests = **99 tests intended**, GitHub result *not yet obtained*.
- `first-compute-only`: separately authorized, only after static inspection; one original `rims_002` first native compute, shell bounded by **240 seconds** (`timeout --kill-after=30s`), and 55 minute overall compilation/job cap. Every result is archived even if timeout, exception capture or setup fails. This job can be GREEN when a **failure reproduces correctly**; GREEN is not a scientifically viable physical solution.

The original c35 Run #2, c36 analysis and c32 `rims_000` background are immutable, never overwritten or reinterpreted. Frozen 81 total: **3 physically attempted** (2 native completed, 1 solver-failed), **78 never attempted**. The c37 single first-normalization forensic retry will be separately tallied as a **repeat of the existing failed frozen case**, *not* a fourth independent physical parameter point or a full trajectory.

## Scientific continuation and falsifiability

Next diagnose the actual **innermost failure condition** from the captured Cython exception; only then consider a separately preregistered numerical-accuracy / initial-shooting parameter sensitivity design, distinguished from changing physical model assumptions. Any solver resilience analysis must retain the original failed result, all newly attempted settings, exact patch versions, and independent background/perturbation gates. Do not interpret the initial source mass curvature sign as the sign of full effective scalar mass squared, nor assume a negative `m''/m` mathematically prohibits a physical background.

No c37 CLASS computation, 81-background scan, c18 all-eight parity, second Einstein–Boltzmann solver, production Planck/DESI/Pantheon+ MCMC, model preference, Bayes factor, or detection has been executed here. Production thresholds remain GetDist R−1 < 0.01 and minimum headline ESS ≥ 1000.

## Local immutable preparation artifact

`RIMS_C37_SHOOTING_EXCEPTION_PREP_20261026.zip` SHA256 `7b60e7cea928731788d63a378aaca0174b603fe4701c6f2c165147edb389a464` preserves the byte-identical c35 and c36 ZIP archives, original 1,000-character error prefix, preparation ledger and SHA256 manifest. **It does not contain a new full CLASS error**; only the separately authorized c37 diagnostic can acquire that.
