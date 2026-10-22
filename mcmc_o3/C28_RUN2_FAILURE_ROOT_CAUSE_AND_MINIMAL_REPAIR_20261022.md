# RIMS c28 — Run #2 real failure diagnosis and minimal input repair

**Date:** 2026-10-22. Status: **c28 corrected source committed and manually dispatchable; not yet run**. This note does not revise the original RIMS scientific claims or overwrite any c27 evidence.

## Immutable original failed physical attempt

- GitHub workflow: c27 `single-case`, run [39741330265](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39741330265)
- One and only frozen case `rims_000`: input SHA256 `e95f274bbafd51e117c9286480da1be42278c1e4def4aae447c1968dc0471e61`; 81-grid freeze SHA256 `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.
- Original GitHub artifact `rims-c27-single-native-class-background` ID **12409746244**; original GitHub artifact ZIP SHA256 **4d1542c02e67763c8f18171086563678456b6acf05516f99da2ff609060c1349** (identical locally downloaded ZIP).
- The source-pinned CLASS checkout, both patch SHA256 checks, native compiled installation, and c27's 56 static tests **succeeded**.
- The first `normalization_background` `Class.compute()` returned `CosmoSevereError` after ~1 ms. **Native compute attempted: 1; successful physical background solutions: 0; all 80 remaining cases: not attempted.**
- Exact CLASS error ends: `input_read_parameters_nonlinear ... You requested non-linear computation but no perturbations. You must set the 'output' field.`
- This happened in the **input parser**, before the background equations were solved. It is **not** a tachyonic branch, normalization failure or evidence against RIMS. Source failure status remains `SOLVER_FAILED`; no physical viability verdict.
- c27 audit/early epoch/full raw history steps were `skipped` by workflow's fail-closed success dependency, while the raw receipt/event log were retained and independently downloaded.

## Confirmed root cause, not a guessed replacement

The c27 background-only runner supplied simultaneously `output=""` and `non_linear="none"`. In the pinned upstream CLASS source `source/input.c`, function `input_read_parameters_nonlinear`, **presence** of the `non_linear` input (`flag1 == _TRUE_`) checks whether `ppt->has_perturbations == _FALSE_` **before** inspecting its value. Therefore even value `"none"` triggers the failure when output is empty.

**c28 minimal repair:** remove the `non_linear` input KEY entirely from background-only calls; do **not** force perturbation output (would silently change the declared background-only cost/physics). Frozen potential family, shell couplings, `s_i`, cosmological parameters, CLASS upstream commit and patches are unchanged. Four new regression tests check parameter omission on all 81 cases, complete synthetic runner/auditor wiring, unchanged 81-grid checksum, and provenance of the actual Class implementation module.

## Independent build-provenance correction

In c27, `binary_path` pointed to `class_public/__init__.py`, a Python wrapper, so its SHA256 was **not** a compiled binary hash. This original artifact remains unchanged; c28 identifies this limitation and repairs the real-mode provenance by resolving `classy.Class.__module__` (CLASS `_classy` extension), storing its actual compiled extension path+SHA256 and requiring the module path to be inside the pinned patched checkout and to have a recognized Python extension suffix. Synthetic test modules are allowed only in mock test calls, never through `verify_pinned_environment` in the real entrypoint. The c28 source is not yet validated by real physical execution.

## Physical and inference firewalls

The new workflow `.github/workflows/rims-phaseii-c28-corrected-background-smoke.yml` is `workflow_dispatch` ONLY, with `static-only` **default**, and a separate explicit `single-case` mode running only `rims_000`; no schedule, no MCMC, no 81-case batch and no automatic next stage. It retains an independent **failure-aware audit ledger** after any new solver failure and uploads evidence even on failure.

Run static-only first; only then separately authorize single-case. **Neither c28 static checks nor corrected real CLASS has yet been executed**. Do not rerun the old c27 failed run or change the original provenance artifact. The c18 matched 8-start parity, actual 81-trajectory scan, potential family research, independently coded solver and production inference remain explicitly pending.

No ΛCDM comparison, Bayes factor, production posterior, fifth-force detection or RIMS global priority is claimed. Production MCMC still requires GetDist R−1 < 0.01 and minimum headline ESS >=1000.