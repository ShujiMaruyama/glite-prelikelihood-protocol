# RIMS c29 — live CLASS background-parameter failure diagnosis and repair

**Date:** 2026-10-23; **status:** corrected source and manual-only workflow registered; new branch not executed in GitHub Actions. Nothing here establishes a production cosmological inference result.

## Immutable observed GitHub evidence: c28 Run #2

- GitHub run: [39887833682](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39887833682) (2026-10-23 UTC, `single-case`).
- Workflow concluded `failure`; `static-check` succeeded with **60/60** tests.
- Original failed artifact: `rims-c28-single-native-class-background` **artifact ID 12473741252**; original recorded case `rims_000`, frozen-81 matrix `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.
- Pinned upstream, patches and compiled native extension all succeeded. **The previous c27 `non_linear='none'` parser failure was resolved.**
- **THREE successful real native background normalization computations.** Source `native_compute.log` records:
  1. `mass_ratio=1.0020129165561753` at `phi_ref=4.11730971054`;
  2. `mass_ratio=1.0000006868179911` at `phi_ref=4.34064822101824`;
  3. `mass_ratio=1.0000000002346996` at `phi_ref=4.340724518959356`.
- `normalization_iteration_success=true`, total `native_compute_attempts=4`, where attempt **#4 `final_background` failed** with `CosmoSevereError: Class did not read input parameter(s): ic`.
- c28 runner passed perturbation-only `ic='ad'` in `base_args`. It removed `ic` explicitly from each of the 3 normalization calls with `q.pop('ic',None)`, but NOT from the final background call. As `output=''`, no perturbations were requested and CLASS rightfully did not consume the `ic` key. This is an **input parser fail** on final solve, not evidence of physical instability or an executed final physical history.
- Retained failure-aware audit: `SOLVER_FAILED=1`, `NO_RECEIPT=80`; `PHYSICAL_VALID=0`. c26/27 post-run stability and independent source-history checks were correctly skipped. The auxiliary report-only audit *also* displayed failure because it treated a documented `SOLVER_FAILED` as a scientifically successful solve requirement. Its independent evidence JSON was written and archived.

## c29 minimal fix and audit improvement

- `base_args` now **omits `ic` entirely**, with the physical frozen 81 cases, CLASS upstream/patch SHA256 and all numerical parameter values unchanged.
- Both the 1–16 iteration mass-normalization backgrounds and the final background are now strictly background-only, `output=''`. A new runner guard rejects `ic`, `non_linear`, or `non linear` when output is blank. Source receipt and auditor version must be `c29_native_background_v5`.
- New synthetic parser regression `test_c29_ic_parser_regression.py` contains **4 additional test cases**: 81 input-parameter integrity, three-stage normalization plus final no-ic call, faithful reproduction of the old fake parser failure, and no promotion of original failed real run.
- c28 native compiled `_classy` extension SHA/path verification remains unchanged.
- New `.github/workflows/rims-phaseii-c29-background-only-ic-smoke.yml` is **manual dispatch only**, **static-only by default**. Separate `single-case` may be launched manually **only after the static preflight is inspected**, with one `rims_000` real CLASS attempt, no full 81-case mode, no MCMC, and no automatic follow-on.
- A failure-aware evidence step retains the `failure_aware_audit.json` even if one-case physics fails, and accepts auditor exit 2 as an *expected outcome of recording a nonphysical solver failure*, not as a PASS for physics. The primary solver remains red on any failure.

**c29 static Python test target = 64 total** (the c28 registered 60 plus 4 new); this is NOT YET A VERIFIED PASS. No Actions run has been dispatched on c29 as part of this repair.

## Forward-model and scientific boundaries

All successful normalization solves are real patched CLASS compute events, but are **not** full physical background solutions validated by c26/c27 initial state, 0≤z≤3 effective mass, observational covariance or independent solver. The true c29 corrected final background has **not been executed**, and RIMS competitiveness with ΛCDM is unverified. c18 all-eight independent native parity remains a separate hard gate. The 81 physical trajectories remain unexecuted. Production matched Planck 2018 + DESI DR2 + Pantheon+ inference can claim a posterior only if GetDist R−1 < 0.01 and minimum headline ESS ≥1000; no Bayes factor, model preference or detection.
