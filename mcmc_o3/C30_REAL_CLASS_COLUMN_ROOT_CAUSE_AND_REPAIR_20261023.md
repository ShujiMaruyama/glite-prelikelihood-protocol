# RIMS c30: exact patched CLASS stability output, physical-gate integrity (2026-10-23)

**Stage:** source fix and manual-only static/native workflow staged. No c30 Actions run has been executed yet. **Original c29 failure remains immutable.**

## c29 Run #2 verified evidence

[Live GitHub Run 39913415302](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39913415302) concluded FAILURE, while the 64-test static job and patched native CLASS compilation succeeded. The sole physical background `rims_000` had three successful normalization `Class.compute()` runs, and **the final `Class.compute()` also completed successfully**. Extraction of `Class.get_background()` subsequently FAILED because the c29 Python reader searched for invented guessed column name `rims_m2eff_over_H2`; the original patched CLASS `background_output_titles()` does not use that name. The exception was `RuntimeError: Missing/ambiguous patched RIMS CLASS background field rims_m2eff_over_H2: []`.

The uploaded preserved artifact ZIP, independently inspected, is SHA256 `513f8dc85fd8538831e007b5fca37a089a84fbc072adf822088bd7729fdbf502`; GitHub artifact ID **12484166300**, 7 files. Its four `native_compute_start` events each have successful `native_compute_end` events; normalization `mratio` reached 1.0000000002346996; `normalization_iteration_success=true`, `native_compute_attempts=4`, `run_status=solver_error`, and failure-aware audit statuses `SOLVER_FAILED=1`, `NO_RECEIPT=80`.

**This is a Python native-output column-binding error after solver completion**, not an instability signal, but also **not** a stability PASS, physical reachability result, or successful c26/c27 fidelity audit. No final background arrays were retained by c29, and no physicochemical inference is supported.

## Exact patched source diagnosis

The preserved patched code `rims_o3_patch/base_parts/part02_03` adds these exact `background_output_titles` and matching columns: `rims_s`, `rims_alpha`, `rims_dalpha`, `rims_mratio`, `rims_q`, `rims_meff2`, **`rims_stab`**, `rims_closure`. The earlier `rims_o3_patch/base_parts/part01` defines `rims_stab = rims_meff2 / pow(H,2)` and enforces a minimum stability gate. The upstream CLASS physical H output is `H [1/Mpc]`. These are **grounded in frozen physical source**, not speculative guessed aliases.

## c30 correction (no new physical run)

The c30 source now requires exact fields `z`, `phi_scf`, `rims_mratio`, `rims_stab`, `rims_meff2`, `H [1/Mpc]`, stores actual available native background field names in source receipt/event, and checks for finite values, H>0, array consistency, and every-row `rims_stab ≈ rims_meff2 / H²` (rtol=5e-8, atol=1e-10). This must **fail closed** rather than silently fill with an unverified mass expression. c30 independent audit requires `c30_native_background_v6`, raw field inventory, explicit stability binding and reconstruction error; 0<=z<=3 stability threshold unchanged.

Five existing mock CLASS test files were updated to use the *actual frozen* patched output schema; **six new c30 offline regression tests** cover exact mapping, missing column, ratio mismatch, tachyonic negative margin (veto), nonfinite margin (veto), and exact frozen 81 inputs. Target suite total = **70** (previous 64 plus 6). **No PASS claim for the new suite until GitHub Actions is run and its logs are verified.**

## Manual science protocol

`.github/workflows/rims-phaseii-c30-stability-column-smoke.yml` on dedicated branch `rims-c30-native-stability-column-20261023` and registered on default branch with **workflow_dispatch only**, default `static-only`. Separately authorized `single-case` executes only `rims_000`; all other 80 cases remain `NO_RECEIPT`. Not c18 eight-start inference parity, not 81 physical trajectories, not a production posterior. Retain all first-run receipts and failure-aware audit artifacts, do not use 'Re-run' on any older branch.

Even a future full native background passing these checks is a **one-case pilot** with user-defined `z>=1000` occupancy threshold and `m_eff²/H²` linear background stability only. It does not certify all tensor/gradient safety, observational predictions, high-k/nonlinear transfer, model preference, or global novelty. Production matched Planck 2018 + DESI DR2 BAO + Pantheon+ posterior requires GetDist R−1 < 0.01 and minimum headline ESS ≥1000.
