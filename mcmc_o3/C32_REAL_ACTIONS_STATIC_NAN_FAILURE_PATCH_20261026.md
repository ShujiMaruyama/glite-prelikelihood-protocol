# RIMS c32 follow-up: actual GitHub static-failure forensics and corrected finite-source gate

Audit date: 2026-10-26, Japan Standard Time. **Do not modify or claim successful the original failed GitHub run** [40246746772](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40246746772), dispatched from c32 commit `9e547dcf8d97c2d9f3489bd3afe655d47272b0e0`.

## Exact observed failure

- Job `static-check`: FAILURE; `single-native-background`: SKIPPED (no physical CLASS run).
- Verified frozen source matrix hash: `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.
- Pytest result: **80 passed, 1 failed**. Failed test: `mcmc_o3/c24/test_c30_stability_column.py::test_nonfinite_stability_margin_is_not_silently_dropped`.
- Exact Python exception during receipt serialization, not during a CLASS numerical solve: `ValueError: Out of range float values are not JSON compliant: nan`.
- Underlying flaw: c32 constructed and stored the native-bracket dict **before** checking whether source `rims_stab` or other native fields contained NaN/Inf. When the synthetic nonfinite mass ratio was on one of the bracket rows, the original exception was caught, but an unsanitized `c32_native_z3_bracket` value remained in the failure receipt; the final `json.dumps(...,allow_nan=False)` then raised and no fail-closed receipt was created.
- The failure was **a valid security/scientific-integrity regression**, not a spurious test to drop. It does not imply a RIMS physics instability, observed fifth force, or posterior.

## Safe corrected implementation (source changed after original failed run)

`mcmc_o3/c24/c24_native_background.py` now checks **all unfiltered native z/phi/mass/H fields** for nonfinite values (plus nonpositive H) *before writing the native z=3 bracket or its SHA/JSON event*. The existing c24 `input_native_nonfinite_count` and c30 `c30_native_full_nonfinite_rows` counters are retained as **finite integers**. On any invalid physical column the solver is recorded as `run_status=solver_error`, with `failure_class`, `failure_message`, computation event log SHA and machine-readable receipt, and never as `PHYSICAL_VALID` or `NATIVE_GRID_BRACKETED_SAMPLED_PASS`.

One additional synthetic test `test_c32_nan_just_above_z3_returns_machine_readable_failed_receipt` deliberately inserts NaN in the *first native row above z3*, checks that the full-native invalid-row counter is one while the 0≤z≤3 invalid counter is zero, checks that **no source bracket is emitted**, and verifies that both failed receipt and independent `SOLVER_FAILED` audit are preserved. The original failing c30 nonfinite regression remains unchanged.

**Static suite expected after this patch = 82 tests** (c30 70 + initial c32 11 + new c32 1). This count is **NOT** a PASS claim. It is pending a new GitHub Actions dispatch. Do not rerun or reinterpret historical #1, do not start a physical `single-case` run until the new static run is inspected.

## Current safe operation

Existing manually registered c32 workflow `.github/workflows/rims-phaseii-c32-native-bracket-smoke.yml` on the default branch checks out the **selected branch's current head**. The workflow remains `workflow_dispatch` only, safe default `static-only`, separate optional `single-case` limited to frozen `rims_000`; **no automatic runs, no MCMC and no 81-trajectory batch**.

Select `rims-c32-native-bracket-endpoint-gate-20261023`, `run_mode=static-only` and click **Run workflow** as a *new* invocation. The old failed run is preserved and should not be rerun via its Re-run button.

## Unchanged science boundaries

The real archived c30 background solution passed native execution and had sampled `m_eff²/H²>0`, but the original c30 strict endpoint status is still **PHYSICAL_REJECT**. Neither old c30 nor the new c32 future bracketing method proves continuous interval stability, tensor/gradient stability, independent second solver, observational model preference or production RIMS posterior. The c18 matched CLASS eight-start parity and 81 physical trajectories remain pending; GetDist R−1<0.01 and minimum headline ESS≥1000 production thresholds are unchanged.
