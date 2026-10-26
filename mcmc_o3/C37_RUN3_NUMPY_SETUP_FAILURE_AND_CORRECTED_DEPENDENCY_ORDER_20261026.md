# RIMS c37 — GitHub Run #3 environment failure, immutable forensic finding and dependency fix

**Audit date:** 2026-10-26 (JST); **actual workflow Run #3:** https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40275684367 (conclusion: FAILURE); **executed commit:** `a5d531cfa2229660133eb654552d58b2a06fc8d9`.

## Exactly what ran and failed

- The `static-check` job completed successfully (99 previously declared static tests PASS).
- The `exact-first-failed-compute` job **failed in the first prerequisite step**, `Verify original 81-case manifest without replacing any frozen inputs`.
- The frozen manifest had been created successfully. Importing `mcmc_o3/c37_exact_shooting_probe.py` loaded `c24_native_background.py` which imports **NumPy** before NumPy had been installed for this job.
- **Exact observed failure:** `ModuleNotFoundError: No module named 'numpy'`.
- The step `Pin and patch original CLASS V18.29 exactly`, the native compilation step and the actual first `rims_002` `Class.compute()` step were all **SKIPPED**. This GitHub failure is an **environment/step-order error**, not new evidence of a RIMS solver failure.
- Original evidence artifact (unchanged): `rims-c37-one-shooting-exception`, GitHub artifact ID `12630087010`; contains manifest and SHA256 but no newly captured CLASS exception. There is **no** new full shooting error to interpret.

## Forward-only repair

- Insert a new native-job step `Install pinned NumPy before importing native preflight source` **before** the original manifest check. It pins **`numpy==2.5.3`**, already used by the prior successful native c35 CLASS builds, and checks its installed version.
- Keep pinned native compilation dependencies and original CLASS source/patch SHA checks unchanged; do not tune scientific parameters or replace case `rims_002`.
- Add a new static test `test_real_workflow_installs_numpy_before_python_preflight_import` to enforce workflow dependency order and the one-case guard.
- Updated intended static count: **100** (previous 99 + 1); this new total is **NOT** a confirmed GitHub PASS yet. Previous successful 99 cannot certify the added regression.
- Registered workflow on `main` has been synchronized byte-identically with the c37 source branch, remains **manual `workflow_dispatch` only**, default `static-only`, optional `first-compute-only`, *exactly one* previously failed frozen `rims_002` first normalization compute, bounded by 240 seconds. No automatic dispatch, no MCMC, no other physical cases.

**Claim boundary:** c35 still has unique physically attempted source cases 3/81, complete background solves 2, numerical solver failure 1, unattempted 78. c37 has not yet executed a new physical CLASS compute. It is scientifically incorrect to infer the source of `rims_002` shooting failure from the latest missing NumPy module; that is a separate setup defect. The full Cython error remains unknown until a properly initialized c37 native job executes and archives it.
