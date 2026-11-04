# RIMS C53 — Newton-to-Commit Gap: Source-Level Forensic Result

4 November 2026 | Shuji Maruyama | Independent Researcher, Muroran, Hokkaido, Japan | ORCID 0009-0007-5034-7634

© 2026 Shuji Maruyama. All rights reserved.

## Verified integration/observability obstacle

The [fixed upstream CLASS NDF15 integrator](https://github.com/lesgourg/class_public/blob/e85808324f51fc694d12e3ed7439552a3c3f9540/tools/evolver_ndf15.c) evaluates the derivative at the current Newton candidate (source lines **382–383**), applies a subsequent Newton correction to ynew (lines **408–410**), and may declare convergence without re-evaluating the corrected state (lines **412–438**). The accepted step count is incremented at **539** and the corrected ynew is subsequently committed.

Therefore the last successful DERIV input and the finally accepted COMMIT state **need not be binary64-identical**. C52's strict state join protects against false assignments but may yield zero valid matches under normal NDF15 corrections. Physical mass ratios evaluated before a correction must never be relabeled as post-COMMIT physical values merely because the time coordinate is the same.

For differentiable g(y,a) = m_eff²/H² + 1e-10, writing δy = y_commit - y_eval,

**g_commit - g_eval = integral from 0 to 1 of grad_y g(y_eval + λ δy,a) · δy dλ.**

An independent Lipschitz bound L would imply g_commit ≥ g_eval − L ||δy||. This L has NOT been established for native RIMS, so this identity is not a numerical sign certificate. It is an observer-design result, not a claimed new gravity phenomenon.

## Original C44 native evidence, unchanged

Source run: [C44 Run #2](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/41000757103).

| Field | Real archived value |
|---|---:|
| Original native CLASS compute attempts | 1 |
| NDF15 derivative evaluations | 845 |
| Accepted COMMIT steps | 618 |
| Last accepted scale factor | 3.891990717634451e-10 |
| Next rejected Newton trial scale factor | 3.945904558535526e-10 |
| Rejected-trial-only m_eff²/H² | -1.0049389722010728e-10 |
| Accepted full-state vectors in the original C44 log | **Not recorded** |
| Accepted physical g in that original log | **Not measured** |

C44 native stderr SHA256: **9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d**.

The C53 independent read-only auditor returned **NO_ACCEPTED_VECTOR_TELEMETRY** on this verified original stderr. It does not invent any accepted-state stability values.

## New executable C53 code and reproducibility

The source program [c53_newton_gap_audit.py](../mcmc_o3/c53_newton_gap_audit.py) checks each COMMIT against the last *successful* DERIV input at the same binary64 coordinate and within the same accepted step, reporting mismatching vector components and state displacement. No derivative physical value is promoted to a physical accepted-state g.

Twelve new locally executed adversarial tests PASS, including one-ULP mismatch, exact match, same-step scoping, signed zero, malformed and nonfinite hex values and duplicate/missing sequence refusal.

A separate original C52 reproduction script completed successfully (201 + 17 + 14 inherited software/synthetic tests); it did not execute a new native CLASS compute.

- Original unchanged C52 ZIP SHA256: **f7cebafea1181a2950cb897f8c06ab9cfa65442796396a6b08f37c992c405f02**
- New C53 ZIP name: **RIMS_C53_Newton_Commit_Gap_20261104.zip**, SHA256 **d7587ca1289d519ced5f86f0005b19d927c5dee1a6e0836e1b7020dbbd311f90**
- Titled PDF: **RIMS_Newton_Commit_Gap_C53.pdf** (A4, 2 pages), SHA256 **d6fe62a5dd3c343203fe3c4987d10db34acb1675659bf08fc48b4413d9567187**
- C53 ZIP was independently re-extracted; all twelve new tests, original stderr checksum, ZIP CRC and file SHA256 checks PASS.

## Manual native-readiness gate

[C53 GitHub Actions](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c53-newton-gap.yml) is now registered on both the dedicated C53 branch and main. Default **static-only** compiles the pinned RIMS/CLASS source and performs source-regression checks **without calling CLASS.compute()**. An explicitly separate **native-one** choice is limited to the same frozen original rims_002 input and original 1e-10 veto; it has NOT been run. The C53 Newton/COMMIT gap diagnostic saves evidence even if the original exact physical-g observer correctly fails closed. No automatic retries or paid infrastructure.

Do **not** run native-one before the static preflight is reviewed.

### Hard scientific limits and next gate

No new C53 native CLASS computation, no directly measured accepted-state mass, no physical stability bracket, no healthy normalized background, no full coupled perturbation spectrum, no observational detection, no production posterior or model superiority established.

The next decisive instrument must directly and independently evaluate g on a true accepted y (with a provably isolated background workspace, or a rigorous mathematical bound), check observer-versus-original trajectory parity, and then evaluate the gauge-invariant coupled matter–scalar–metric operator.

**This browser-readable report is the delivery fallback if the ChatGPT PDF/ZIP links fail.**
