# RIMS C42 — Common-Epoch Accessibility and Source-Locked Convergence Gate

**Author:** Shuji Maruyama · Independent Researcher, Muroran, Hokkaido, Japan · ORCID 0009-0007-5034-7634  
**Date:** 27 October 2026  
© 2026 Shuji Maruyama. All rights reserved.

## 1. Scope and provenance

This branch continues C40 original physical veto for `rims_002` and the two executed C41, GitHub Actions runs #3 (tight10) and #4 (tight100). It performs a new **read-only numerical identity and accessibility audit** on the immutable ZIPs. All three original veto calls end with shooting rejection; there is no normalized cosmological background, convergence certificate, MCMC or observation-likelihood result.

- C40 original: `RIMS_C40_EXACT_LOCAL_VETO_ENVELOPE_20261027.zip`; SHA256 `6d17d50f2079a94a58ed27867ab43ec9fc1b0d1d3cd702fe158b94824459df6b`.
- C41 native tight10: GitHub run 40465268375, SHA256 `4c0e398da317f78e38ca867405c3a0587ad4d82a93b3782c0a2d16c926c7b795`.
- C41 native tight100: GitHub run 40468067745, SHA256 `c83b962f3a83b7e789485e466487c1fd9ec772ecb3d7395647cee0b6303532db`.
- Scientific case frozen hash `9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284`; 81-case design SHA256 `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.

## 2. New mathematical diagnostic (not numerical-convergence evidence)

The patched physical-source formula, **including its factor of three**, is

\[
R(a)\equiv \frac{m_{\rm eff}^2}{H^2} = \frac{V_{,\phi\phi}+3\rho_{\rm idm}C_m(s)}{H^2},\qquad C_m=\alpha_U^2(1-s)(1-3s).
\]

The three measured veto calls have `Vpp/H² ~ 4e-129`, an approximately constant `C_m ≈ −3.325e-5`, and show `rho_idm * a³` conserved across the three recorded (but different) epochs at a relative range `2.01e-14`, while `H * a²` has relative range `7.13e-10`. The source relations imply a *conditional* radiation-branch relation:

\[
\rho_{\rm idm}(a)\approx Q a^{-3},\quad H(a)\approx S a^{-2}
\ \Longrightarrow\ R(a)\approx \frac{3 Q C_m}{S^2} a\equiv K a.
\]

On the observed points `K = R(a)/a ≈ −0.254678986` has relative range `1.425e-9`. This is a strong **source and background scaling consistency** check across the archived rejection calls, not evidence of numerical convergence at the same scale factor. It can arise because the same analytic source identities control all three outputs. The equations must not be treated as a fully calibrated radiation-era cosmological solution.

Within this *conditional* extrapolation only, the original unaltered stability veto `R < −1e-10` begins at

\[
a_{\rm gate}^{\rm conditional} \approx \frac{10^{-10}}{|K|}
= 3.92651163\times10^{-10}.
\]

This is a **post-hoc algebraic extrapolation**, not an observed zero crossing, root bracket, evidence of physical tachyonic behavior or a pre-registered cosmological forecast. The actual detected veto candidates occurred at `a=3.94590456e-10`, `3.95012823e-10` and `3.94693517e-10` respectively; all are later than the conditional gate onset. A future native run must independently establish `a_ini` and whether an accepted, shared, pre-veto interval exists.

## 3. Critical CLASS source detail

The original native traceback locates the rejection in:

`evolver_ndf15: (*derivs)(tnew, ynew+1, f0+1, ...) → background_derivs → background_functions → RIMS stability gate`.

The value printed by the C39 diagnostic is thus recorded **inside a derivative evaluation**; it is not independently certified to be an **accepted-step history**. Therefore, comparing veto calls at three unequal `a` values, or interpolating them with a source-model relation, does **not** provide a common-epoch convergence test.

## 4. Hard-gated native successor (NOT YET EXECUTED)

A future, separately authorized **C42-A source-only preflight** must first establish:

1. That `a_ini` and the initialization/shooting stage of each run have been recorded; distinguish beginning of each shooting attempt and background integration from trial derivative evaluations and accepted steps.
2. That an interval of *accepted, physically evaluated* `a` exists in all three precision settings **before** the unmodified stability veto; if the common interval is empty, classify `NO_COMMON_ACCEPTED_EPOCH` and stop, rather than altering start epoch, solver precision, physical input or stability veto to manufacture a shared interval.
3. That any sampling uses identical, *pre-declared* epoch nodes for all precisions within their demonstrably overlapping accepted domains. Preserve native columns `Vpp`, `rho_idm`, `C_m`, `H`, `s`, and algebraic reconstruction; retain the source-only SHA and classification of each sample as `TRIAL`/`ACCEPTED`.
4. That the original veto remains enforced (`rims_enforce_stability=yes`, `rims_stability_tolerance=1e-10`). Keep `rims_002`, 81-case manifest, origin patches, shooting input, initial conditions and CLASS commit frozen. No rescue retune, widening threshold, backdoor disabling, rerun of C41, 81-case scan or production MCMC.
5. That a prospective convergence gate can compute, **at the same accepted a**, the differences \(\Delta_{10,100}(a)\), independent residuals, and a pre-declared accuracy bound. If accepted common-a data are absent, report `BLOCKED` without inferring convergence from `R/a` agreement.
6. That unexpected failures, `stderr`, compiled source/patch digests, and artifacts are retained even when the control program returns a successful archival exit code; solver success and scientifically successful inference remain separate.

**Important feasibility warning:** These early vetoes occur very close to the apparent initial background epoch. The common-epoch test may be unattainable under the unmodified native gate. If so, the defensible result is a precise initialization/accessibility obstruction, not a successful convergence measurement.

## 5. Executed / unexecuted ledger

| Item | Status |
|---|---|
| C40/C41 source archive SHA and ZIP CRC | executed; verified |
| C42 source identity and drift statistics | executed; verified from original archive records |
| C42 conditional onset estimate | executed; algebraic **only** |
| C42 seven negative/source consistency tests | executed; pass |
| C42 *native* initialization / accepted-step sampling | **NOT EXECUTED** |
| Same-a convergence, integration error bounds | **NOT DEMONSTRATED** |
| RIMS stable normalized physical branch | **NOT DEMONSTRATED** |
| Cosmological production likelihood / independent code | **NOT EXECUTED** |

## 6. Reproduction (no CLASS runs)

From the extracted package root, with Python 3.10+ standard library only:

```bash
python c42_readonly_common_epoch_gate.py --input-dir evidence --output C42_REPLAY.json
python -m unittest discover -v
```

The read-only program refuses wrong archive digests, corrupted ZIP, mismatched frozen-parameter SHA, tampered native stderr, altered original stability threshold or inflated convergence/viability claims. Original archive ZIPs remain byte-identical, unmodified evidence.

## C42-A source localization addendum (2026-10-27; no new CLASS compute)

Pinned upstream CLASS `include/precisions.h` sets `a_ini_over_a_today_default=1.e-14`. The initializer `background_initial_conditions` starts from that value but may modify it; the C41 recorded first-veto values (~3.95e-10) cannot be equated to `a_ini`. Therefore the earlier feasibility warning about being "very close" to an apparent initial epoch was **unsupported**. Actual initialization scale factors require future source-marked evidence.

Pinned `tools/evolver_ndf15.c` calls `(*derivs)(tnew,ynew,...)` in the adaptive trial prior to the acceptance marker `stepstat[0] += 1`; only after acceptance does it dispatch output-grid callbacks, possibly via interpolation. The C39 native veto print within `background_functions` belongs to the derivative-stage failure chain; it is not an accepted-step measurement. A future C42-A source-only instrumentation preflight must register output-callback vs NDF-accepted-step vs initialization events separately. This addendum is **source review only**: no C42-A native execution, no same-a convergence, and no physical viability conclusion.
