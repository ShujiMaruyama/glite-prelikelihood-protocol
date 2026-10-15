# c18 — Native CLASS eight-start parity (2026-10-15)

**Current status: OFFLINE source-ready only.** This branch stores a frozen decision/claim ledger, **not yet executable source**. The complete source + manual-only workflow and all prior c15/c16/c17 packages are in the ChatGPT conversation artifact `RIMS_c18_full_native_parity_action_ready_20261015.zip` (SHA256 `7efd06d6587ac06ba6203224345d15b91a6a0f74f43a00096af64bbfcea341bb`).

## Implemented in the external, checksum-verified ZIP

* Fixed 8 genuinely distinct source vectors and input YAML hashes, locked by `C18_FROZEN_START_MANIFEST.json` SHA256 `3c49def1a71e63188fc81e3bd5853534dae16b64c4d366fea23dd9cee704e658`.
* `c18_source_gate.py`: strict 8-YAML and 10-dimensional start identity, no substituted or duplicated input.
* `c18_verified_pair.py`: rerun c17 component parity using the exact frozen source hash and start identity.
* `c18_eight_start_gate.py`: rerun all eight and independently match raw source JSON/telemetry to saved audit.
* `run_c18_onepoints.sh` and `.github/workflows/rims-phaseii-o3-c18-native-parity.yml`: manual-only, safe default `static-only`, separate `single-pair` and `eight-start` modes, **NO MCMC and no automatic follow-on**.
* Offline unit tests PASSED **45/45**: c15 6, c16 13, c17 15, c18 11. These **do not** demonstrate real pinned CLASS V18.29 compatibility or physical posterior parity.
* SHA256 manifest in the ZIP covers every file, including the exact prior c15/c16/c17 ZIPs. Total ZIP files: 74.

## Pending action, not completed

A compatible operator must first commit the ZIP-contained `mcmc_o3/c18/` and workflow source into this dedicated branch, **then** register the workflow file on the repository default branch. Neither upload/registration nor workflow dispatch has been performed by c18. The actual pinned RIMS V18.29 CLASS and Planck 2018 + DESI DR2 + Pantheon+ evaluations remain **zero**. We must never report a run ID or any runtime numerical parity result until verified from GitHub.

The first authorized action should be a manual `static-only` dispatch, followed by a separate `single-pair` dispatch after approval, and `eight-start` only after inspecting the physical/safety logs. If any input point is non-finite, preserve the failure and return to the predeclared design; do not drop it from the batch.

**Fixed production gates:** GetDist `R-1 < 0.01`, headline ESS minimum `>=1000`. There is no production posterior, Bayes factor, model preference, or ΛCDM competitiveness claim.
