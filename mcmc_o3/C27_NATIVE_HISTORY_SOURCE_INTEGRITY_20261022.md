# RIMS c27 — full native z/phi provenance cross-check (2026-10-22)

**Status: source committed, local mock replay PASS, GitHub Actions NOT DISPATCHED, no physical CLASS run.**

c26 previously recomputed initial occupancy from the *reported earliest phi*, but did **not** reparse and independently verify that phi came from the full original native CLASS history. A short fake history and an internally self-consistent c26 snapshot could otherwise pass a superficial receipt audit. c27 fixes that **evidence-integrity** gap without modifying the frozen 81-case design or replacing c26's science gate.

## Added independent source-binding gate

The pinned physical runner on the c27 branch now writes every unfiltered native final `Class.get_background()` redshift and scalar-field value to a canonical `c27_full_history_z_phi.json` file and records its SHA256 digest in the physical run receipt. It does this before trimming to 0<=z<=3. The standalone `c27_history_integrity.py` recomputes the c26 earliest-z, earliest-phi, source occupancy, row index, thresholds and conclusion from this entire separate history artifact. Missing rows, altered chronology, source case ID, SHA mismatch, renamed mode, nonfinite entry, updated start-threshold or initial status have **hard FAIL** outcomes.

The original source bytes, frozen input case SHA, full native row count, per-run digest and source-specific earliest-state report must be consistent. This does **NOT** independently attest the truth of a compromised physical CLASS binary or substitute for a second Einstein--Boltzmann implementation. A joint rewrite of all self-reported receipts and their hashes remains beyond this integrity gate; signed external source provenance and physical parity are separate requirements.

## Verification so far

- Existing archived c23 and c24 tests plus c26: **46 passed** in an independent local replay.
- New independent c27 full-history unit tests: **14 passed**.
- Synthetic end-to-end Class-like mock with a complete 6-row background: runner -> original history file -> independent audit **PASS**, and source tampering is rejected. Two synthetic integration test cases were added to the GitHub c27 branch.
- Independent local replay suite (original archived branches + local new c27 implementation): **62 passed**. This is **not** a claim that the precise live GitHub branch has passed Actions. The local archive's c24 runner is an independently amended archived predecessor rather than byte-identical to the GitHub c27 executable, which requires branch-specific GitHub Actions verification.
- Actual c27 GitHub Actions run count when last checked: **0**. Actual native RIMS CLASS backgrounds newly executed: **0**. Completed 81-trajectory physical scan: **0**. Production posterior: **none**.

## Safe dispatch, production firewall

The new action `.github/workflows/rims-phaseii-c27-history-provenance-smoke.yml` is on **main** and on the dedicated branch, byte-identically. It is manually triggered with **default static-only**. A separate manually selected `single-case` mode is limited to pinned `rims_000` and must verify the original history before any scientific promotion. No 81-case dispatch option and no automatic next step, MCMC or long run. Once the static GitHub job is inspected, only then authorize the single physical point; after that revisit the pending c18 eight-start matched numerical parity.

Scientific novelty remains the previously developed bounded-shell multichannel closure and its potential-dependent reachability/falsification. This audit is a verification improvement, **not a new dark-sector observation, novelty priority, or model fit**. No claim of superiority to LambdaCDM, no Bayes factor, and no production posterior.

Immutable production gates: **GetDist R-1<0.01**, minimum headline ESS **>=1000**, independent nonlinear C_NL and covariance checks, all 81 attempted physical trajectories with failures retained, second independent solver.

## Source pointers

- `mcmc_o3/c24/c27_history_integrity.py`
- `mcmc_o3/c24/test_c27_history_integrity.py`
- `mcmc_o3/c24/test_c27_runner_integration.py`
- `mcmc_o3/c24/c24_native_background.py` (the c27 export is integrated)
- `.github/workflows/rims-phaseii-c27-history-provenance-smoke.yml` (manual-only)
