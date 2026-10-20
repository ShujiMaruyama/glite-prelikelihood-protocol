# RIMS: physical 81-branch reachability — c23 correction (2026-10-20)

**Claim stage: computational protocol, no new physical run.** The 2026-08-07 RIMS master called for 3 potential families × 3 coupling values × 3 scalar-density targets × 3 initial occupancies = 81 physical cosmological backgrounds, but the material recovered here did not specify the complete numeric level set. c23 fixes those values as a **new 2026-10-20 experiment design**; it never relabels them as historically preregistered or executed.

- Potential families: pure exponential, centered quadratic, centered quartic, with CLASS scalar polynomial-exponential potential (slope λ=5; for deformations A_V=1 and B=φ_i=4.44).
- Couplings α_U = (0.01, 0.05, 0.10); present scalar fraction Ω_{φ,0} = (0.001, 0.03, 0.09); initial shell occupancies s_i=(0.10, 1/3, 0.65).
- Each initial transition coordinate is deduced from **u_i=ln(s_i/(1−s_i))=2α_U(φ_i−φ_t)**, not raw φ_t independent sampling.
- Frozen fixed background H0=68.02, ω_b=0.02246, ω_dm=0.11852, inert fraction 0.1. This is a sensitivity scan, **not** a marginalized Planck+DESI inference.
- Every input is uniquely SHA256-labelled and joined to a source/patch manifest; canonical freeze identifier **0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0**.

## Essential fix relative to c21

c21's 81-table evaluator returned a global PASS only when *all 81 physical trajectories were valid*. That conflates a complete science test with a claim of universal physical reachability and creates an incentive to drop counterexamples. c23 partitions expected attempts into **PHYSICAL_VALID, PHYSICAL_REJECT, SOLVER_FAILED, NO_RECEIPT and PROVENANCE_GATE_FAIL**. A failed numerical solve or a tachyonically rejected physical branch is retained by ID and cannot be omitted. This is reproducibility methodology, not a new cosmological theorem.

The native background runner requires the exact original CLASS commit, both pinned patch SHA256 checks, patched source modifications and the imported native CLASS path inside the checked-out source. It separately attempts up to 16 shooting backgrounds and final native CLASS background, retains **all original 0≤z≤3 stability rows** instead of smoothing narrow instabilities away, and writes native event logs/JSON receipts. The auditor checks case identity, checksum, run status, full redshift coverage, |mass normalization|<1e−8 and m_eff²/H²≥−1e−10. Code and logs are **not** cryptographic attestation of a compiled solver or proof of physical correctness: independent CLASS parity and second code remain hard gates.

## What actually ran

**16/16 new Python unit tests passed**, including synthetic 81-entry ledger with one deliberate numerical failure, mock stability veto, missing receipt and tampered native log. The authoring environment did **not** have the pinned patched native RIMS CLASS installed for physics. **Real physical backgrounds executed: 0/81.** New MCMC chains: 0. New GitHub Actions dispatches: 0. No production posterior, detection, Bayes factor, model preference or global priority statement.

## Delivered checkpoint (outside this GitHub tree)

A separately delivered ChatGPT cumulative ZIP `RIMS_C23_CUMULATIVE_DELIVERY_20261020.zip` (SHA256 `2bc9e4377f0991f05e700e91cf6eb49d5d0fe59f8af603525b2a5d646c0089e5`) contains:
1. An **11-page integrated single-column scientific supplement**, with original c22 7-page text retained and a newly derived execution-gate extension, clean-built LaTeX + separate `references.bib`, four vector figures.
2. `source/c23_freeze.py`, `source/c23_native_background.py`, `source/c23_audit.py`, **81 frozen case records**, 16 tests, checksums, logs and render inspection.
3. **Byte-for-byte original c22 FULL DELIVERY ZIP** (SHA256 `d92f32c24e9121ae029325610834e10e7673f0c5efe8a66a416efddc81e4ecdc`).

The standalone 11-page PDF SHA256 is `c2b8726a44eba87ac8a5137a03ebb242e5d55cd7f396d6b30ac49979fde34de8`. Overleaf ZIP SHA256: `7fa345f134bbb1f81567bac7ccfcafc9ab0b2e6296ee12b96f273deabb6ebbe2`.

**This GitHub branch only contains checkpoint/claim-ledger files.** Executable source and PDF are in the conversation ZIP; do not claim they are committed to GitHub unless verified. No manual workflow was registered or dispatched by this c23 extension.

## Unchanged gates

1. c18 pinned RIMS V18.29 physical parity on all 8 independent starts.
2. c23 physical 81 attempted backgrounds with all failures preserved and separate stable/unstable / Xi classification.
3. Joint observable transfer (intrinsic dark fifth force != observed bulk tracer Euler), nonlinear contamination C_NL(k,z), scale gate k_max(z), and C_tot=C_data+C_th+C_sys.
4. Independent Einstein–Boltzmann second implementation and an explicit radiative-protection branch.
5. Matched Planck 2018 + DESI DR2 BAO + Pantheon+ production MCMC **GetDist R−1 < 0.01 and minimum headline ESS ≥1000** before parameter posterior claims. Bayes factors require actual evidence and prior sensitivity.

Existing coupled-dark-energy work includes Gómez-Valent, Zheng, and Amendola, *Physical Review D* 114, 043540 (2026), DOI 10.1103/x8kc-zqzl. Testing field-dependent dark-matter masses with DESI is not novel by itself. RIMS must distinguish its cross-channel bounded-shell parameter sharing under real data, not merely reuse general coupled-quintessence effects.
