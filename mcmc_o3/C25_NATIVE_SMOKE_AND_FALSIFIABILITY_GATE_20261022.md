# RIMS Phase II c25 — Fail-closed physical smoke and cross-channel prediction gate

Date: 2026-10-22. **Cumulative continuation of c24, not a replacement of the frozen RIMS master, c18 parity, or c23 81-branch design.** The c24 branch is untouched. This c25 branch carries genuine updated executable Python and a separate manual-only Actions workflow.

## Auditing defect addressed

The c24 native runner did not distinguish failures during Python/Cython CLASS instance creation, parameter setting, native `compute()`, and `get_background()`. Especially, a Class.set failure before the first native compute could produce `native_compute_attempts=0` and incorrectly fail the provenance audit instead of being retained as a documented failed physical attempt. A background extraction error after successful compute could generate both `native_compute_end` and `native_compute_exception` for the same invocation.

c25 makes the event types disjoint:
- `native_setup_exception`: CLASS constructor or CLASS.set, **no native compute attempt if failing before compute**.
- `native_compute_start`: increments the attempt count exactly once.
- `native_compute_end(success=true)` or `native_compute_exception`: exactly one per started attempt.
- `native_extract_exception`: computed successfully, but could not extract the background. This is never misreported as a failed CLASS compute.

The independent c25 audit accepts a structurally documented zero-native-compute **solver failure** only when a setup-failure event proves why computation never began. It detects missing, duplicated, mismatched, retyped or falsified native events, and rejects a forged `compute_end(success=false)`. No synthetic/missing-case result may be promoted to real cosmology. Source-reported digests alone are not independent cryptographic attestation.

10 **new synthetic** tests have been committed for these c25 failure/tamper cases and conditional sensitivity reporting; the existing 11 c24 synthetic tests remain. These 21 test functions **have not yet been run on GitHub Actions**; do not label them PASS until their actual run report is checked. A separate local archived c23+c24 bundle's 27 tests had previously passed, but it is not byte-identical to the GitHub c25 source.

## Preserved science and new registered decision statistic

Frozen 81 input branches: potentials (exponential, centered quadratic, centered quartic) × alpha_U=(0.01,0.05,0.10) × Omega_phi0=(0.001,0.03,0.09) × initial occupancy s_i=(0.1,1/3,0.65), **fixed only on 2026-10-20**; expected `freeze_hash=0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`. No physical trajectories have run. Every physical and solver failure is retained by source case ID.

On any future verified PHYSICAL_VALID native background, c25 computes from the actual z=0..3 mass-shell span `s_min,s_max`:
- `u_±=sqrt(s_±)`, `h=(u_+-u_-)/2`, `u_c=(u_++u_-)/2`;
- intrinsic fifth-force root `W=A(1-u²)`, `A=alpha_U`;
- shell curvature sagitta `S_W=A h²`;
- ideal equal-error independent three-point 50%-power expected 5-sigma **relative intrinsic-force** noise ceiling `2 S_W/[5 sqrt(3/2) W_c]`.

This is a **conditional experimental-design diagnostic**, not a calibrated DESI/Euclid/Rubin forecast, posterior, observation, nor uniquely RIMS-specific statistical theorem. It is only released for PHYSICAL_VALID audit status. Failure of a trajectory or severe narrow-span precision cost is recorded without selection. Neither W nor u is automatically an observable galaxy/weak-lensing/RSD response; survey covariance, cross-calibration, competing mass maps and kinetic Euler closure are mandatory.

## How to run without upgrading claims

GitHub workflow: `.github/workflows/rims-phaseii-c25-native-background-smoke.yml`, registered identically on the default branch, **manual workflow_dispatch only**.

1. Choose branch `rims-c25-failure-receipt-hardening-20261022`.
2. Keep default `run_mode=static-only`. This regenerates and verifies the SHA-locked 81 design and executes 11 c24 + 10 c25 synthetic tests. **No CLASS evaluation.**
3. Inspect the actual run log/artifact and any failures; only after that choose a *separate* manual `single-case` run. It pins RIMS V18.29 and evaluates **only `rims_000`**, retaining the 80 `NO_RECEIPT` entries.
4. No 81-sweep option, no automatic follow-on, no MCMC and no user-independent scheduled running.

Hard gates: c18 independent baseline/instrumented **real** CLASS parity across 8 fixed points; c23 actual 81 physical attempts after a successful one-point smoke and separate authorization; independent second Einstein–Boltzmann code, nonlinear cut, full covariance and survey response. Production matched Planck 2018 + DESI DR2 + Pantheon+ claims require **GetDist R−1 < 0.01, minimum headline ESS ≥1000**. No detection, Bayes factor, model preference or LCDM competitiveness.

**Status when this note was authored: zero c25 Actions runs; unexecuted native CLASS and production inference.** Do not infer future run status from this static checkpoint.
