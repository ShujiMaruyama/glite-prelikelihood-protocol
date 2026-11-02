# RIMS C49 — source-locked passive native readiness checkpoint (2026-11-02)

Author: Shuji Maruyama, Independent Researcher (Muroran, Hokkaido, Japan); ORCID 0009-0007-5034-7634. © 2026 Shuji Maruyama. All rights reserved.

## Source lineage
- Parent C48 branch: `rims-c48-multiepoch-covariance-audit-20261102` (commit `4d8a6664080b59cfdac66f78ce51cf5198dea0ea`).
- C44 original pinned CLASS run 41000757103, native diagnostic ZIP SHA-256 `cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`.
- Complete C48 ZIP preserved unmodified, SHA-256 `1b67c57f194121f60feb1c485df02bec295d1b738367a6d59e25846b1ca5690c`.
- Frozen original case `rims_002` SHA `9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284`, original veto threshold `1e-10`, original CLASS source `e85808324f51fc694d12e3ed7439552a3c3f9540`.

## New integrated deliverable
Full self-contained local archive: `RIMS_C49_SOURCE_LOCKED_NATIVE_READINESS_20261102.zip`, SHA-256
`0a6eb6903f391df798d34d5b9c4f318c97cacdb063cd3636533ba8b5efd10676`.

Archived content: original C48 ZIP + original C44 physical artifact, C43/C45/C46/C47/C48 prior code/tests, C49 source-locked observer stack, C49 native binary/source/trace auditor, 4-page A4 single-column PDF and independent bibliography, real-source readiness run-card, new adverse-input and integrated synthetic-C tests, complete `SHA256SUMS.txt`.

Static verification executed locally on 2026-11-02:
- 105 inherited C47 tests PASS, 53 inherited C48 tests PASS.
- **24 C49 tests PASS** (21 identity/provenance and 3 **compiled C integrated observer** tests).
- **182 PASS total**; fresh extraction of final ZIP followed by `bash reproduce_all.sh` also **182 PASS**; ZIP CRC and SHA-256 manifest PASS.
- The 3 new synthetic-C tests compile, run and verify four marker streams, strict bitwise successful DERIV-to-COMMIT joining, opt-in/opt-out and unchanged original veto. A previously encountered shared-header ambiguity was in a synthetic single-translation-unit mock; the fixed test intentionally applies C46 before C43/C45 in that mock, while actual CLASS C46 and C43/C45 live in different source files.

## New physically meaningful validation boundary
C49 adds **source-locked additive-only** staging and opt-in application to a disposable exact original CLASS source checkout:
- `source/background.c` must be the C39 post-overlay SHA `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`.
- Original `tools/evolver_ndf15.c` blob SHA-1 must be `0d293723510171ae9a732c80da32adb9ee52701f`.
- C43 BEGIN/TRIAL/ACCEPT_GATE/COMMIT, C45 exact full COMMIT state, C46 successful pre-existing DERIV input and physical values, and original C39 veto are stitched into an auditable *non-mutating* source overlay.
- C49 audit **requires actual pinned source and native binary SHA attestation** plus original one-call input, count and exception; strict C47 IEEE754 same-step full-state match, not nearest-neighbor interpolation.

Original C44 archive showed **618 committed coordinates** and 845 trial evaluations. It did **NOT** measure physical mass g on the accepted states. This is still the actual evidence limit.

## Hard claim boundary
This GitHub branch currently registers this scientific checkpoint document. The **C49 new full code/tests/PDF are in the delivered ZIP, not yet committed here**. No C49 GitHub Actions execution, no new CLASS binary compile/run, no direct accepted-state g on original RIMS background, no root-bracket certification, no normalized viable solution, no production MCMC, no Bayes factor, no observation-based uniqueness, and no model preference have been established.

Next hard gate is to register the validated code into the source-locked GitHub branch, perform real CLASS source compilation in **static-only** mode first, and only afterwards request a separate one-case manually authorized `native-one` run. If no successful exact COMMIT/DERIV match, report **ACCEPTED_G_NOT_OBSERVED**, never infer or manufacture a physical stability value.

No paid infrastructure, auto-dispatch, parameter retuning, reduced stability threshold or automatic retries.
