# RIMS c24: First native physical background, manually controlled (2026-10-21)

**This folder is real runnable GitHub source, unlike c18–c23 ledger-only branches.** All files in this folder and the corresponding workflow are committed. The workflow is also registered on the default branch with an identical blob SHA. **No workflow has been dispatched.**

## Steps

1. In GitHub Actions, select **RIMS c24 native CLASS background smoke (manual only)**.
2. Use workflow from branch `rims-c24-native-execution-source-20261021`.
3. Keep `run_mode=static-only` for first dispatch. This runs only fixed 81-input regeneration, Python compilation and **synthetic tests**. It does not evaluate any physics.
4. After inspecting static result, a separately and manually selected `single-case` run will pin and patch RIMS CLASS V18.29 and execute exactly **rims_000** (pure exponential, alpha_U=0.01, Omega_phi0=0.001, s_i=0.1). All 80 other starts remain `NO_RECEIPT`. It is not the c18 matched likelihood parity run.
5. No 81-background dispatch option or automatic follow-on is registered. The full physical sweep requires separate review of the native single-case artifact **and** the unfulfilled c18 full matched-likelihood parity gate.

## Scientific and safety locks

The 2026-10-20 frozen 3×3×3×3 design is immutable, exact expected design hash `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`. Actual pinned upstream CLASS commit `e85808324f51fc694d12e3ed7439552a3c3f9540`; the two original RIMS patch SHA256 values are checked in the workflow.

The native runner no longer silently drops nonfinite fields at any z within 0..3. Failures are retained as original native receipts; the independent auditor checks native compute-start/compute-end pairing, hash, binary path, physical endpoint and stability. The source verifies the imported native CLASS module is inside the pinned patched checkout. This is file-integrity and structured-log evidence, **not a cryptographically attested external scientific validation**.

**Current status:** locally the original immutable c23 16 tests and c24's companion patched-source 11 new tests were run as **27/27 PASS** in a fake CLASS environment. The committed GitHub c24 contains its own 11 synthetic tests, which remain **not yet run in GitHub Actions**. Do not describe these local tests as verification of the GitHub run or physical RIMS CLASS. Local and repo c24 implementations share the frozen input hash and fail-closed goal; exact byte identity between the implementations has **not** been established.

**Original immutable c23 delivery** remains available as a separate archived ZIP in the user-facing c24 delivery package.

Hard gates remain: c18 actual matched numerical CLASS parity; all 81 executed physical starts with failures retained; second independent Einstein–Boltzmann code; nonlinear contamination and total covariance; matched Planck 2018 + DESI DR2 BAO + Pantheon+ production MCMC GetDist R−1<0.01, minimum headline ESS≥1000; no detection/posterior/model superiority/Bayes factor claims.
