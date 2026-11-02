# RIMS C48 — cross-state null test, full covariance, statistical audit (2026-11-02)

Author: Shuji Maruyama, ORCID 0009-0007-5034-7634.
Independent Researcher, Muroran, Hokkaido, Japan.
© 2026 Shuji Maruyama. All rights reserved.

This new branch preserves C47 unchanged and is an **audit-only evidence pointer**, not an applied data-analysis or CLASS-compute result. The complete source/bibliography/PDF/figures/tests and immutable parent C47 archive are stored in a separately delivered C48 ZIP, not yet tracked as GitHub source files.

## Exact conditional identities

With fixed RIMS mass law `s(phi)=1/(1+exp(-2 alpha_U*(phi-phi_t)))` and `m(phi)/m_ref=sqrt(s(phi)/s_ref)`,
- `beta=dlnm/dphi=alpha_U*(1-s)`;
- `kappa=m''/m=3*beta**2-2*alpha_U*beta`;
- `A_i=(3*beta_i**2-kappa_i)/(2*beta_i)=alpha_U` for beta_i>0;
- parameter-eliminated multi-state null: `N_ij=beta_j*(3*beta_i**2-kappa_i)-beta_i*(3*beta_j**2-kappa_j)=0`.

These are testable only if beta/kappa at multiple states can be independently reconstructed with calibrated covariance and a physical observational forward model. They are not generally unique to RIMS; a constant-beta exponential model can pass the null trivially while failing an additional resolved-interior criterion.

## Actually executed numerical tests

The intact parent C47 archive (SHA256 `0829726ae108732e25b396f7bf9025395291ad333c436dd018096048fb0aefbc`) was separately reexecuted: **105 tests PASS**.

C48 full 2n-by-2n covariance, generalized least-squares/delta-method and adversarial tests: **47 PASS**, plus **six additional calibration-audit tests PASS**, total C48 **53 PASS**; cross-run aggregate **158 PASS**. These are software/fixture tests, not native CLASS computes.

Synthetic null under exactly specified Gaussian five-state full covariance (alpha truth 0.01):
- 3,000 originally selected seed=4802: 122 rejected at nominal p<0.05, fraction 4.0667%; exact-binomial two-sided p under 5% is 0.01888.
- Additional **post-hoc exploratory** seed=4813, 20,000 draws: 986 rejected, fraction 4.93%, exact-binomial 95% interval [4.634%,5.239%] and two-sided p=0.6614.
- No survey data or physical CLASS runs under C48. Chi-squared p is a conditional linearized approximation, not a calibrated observational likelihood.
- Full deterministic reproduction verified by separate fresh reexecution, SHA256 file hashes and re-openable ZIP.

## Distribution

C48 complete local ZIP name: `RIMS_C48_MULTIEPOCH_COVARIANCE_AUDIT_20261102.zip`.
ZIP SHA256: `1b67c57f194121f60feb1c485df02bec295d1b738367a6d59e25846b1ca5690c`.
Paper: `paper/main.pdf`, A4 single column, **3 pages**, no orphan references page.
Reproducible code: `src/c48_multiepoch.py`, `tests/test_c48_multiepoch.py`, `tests/test_c48_calibration_audit.py`, `reproduce_all.sh`, and `SHA256SUMS.txt`.
`paper/references.bib` is separate from `main.tex`.

## Non-negotiable claim gate

C44's 618 NDF15 committed coordinates are real execution evidence, but m_eff2/H2 was **not measured on the committed states**. The C45-C47 exact-state joins are synthetic tested, not validated in a native CLASS run. Consequently no accepted-state stability, healthy normalized background, independent Boltzmann parity, production matched inference, real observational detection, model superiority, model comparison evidence or Bayes factor is demonstrated.

Next C49 hard gate is to integrate source-locked C46/C47 bitwise exact-state telemetry into pinned CLASS, verify no source or numerical noninterference break, and execute a **single authorized frozen-case original `rims_002` compute** (with original gate unchanged). Fail closed if accepted-state full-vector match is absent. Do not promote a rejected Newton trial to an accepted physical instability.

No additional paid infrastructure, new automatic job, GitHub workflow, or new CLASS compute was registered for C48.
