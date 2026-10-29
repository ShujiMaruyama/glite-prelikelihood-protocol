# RIMS C42-B — Pinned compilation and native import gate

**Author:** Shuji Maruyama · Independent Researcher, Muroran, Hokkaido, Japan  
**Date:** 29 October 2026  
© 2026 Shuji Maruyama. All rights reserved.

## Rationale
C41 run #3 (`tight10-one`) and run #4 (`tight100-one`) reproduced the RIMS native stability veto under tightened background integration tolerances. Neither is a numerically converged, normalized background. C42-A GitHub run #1 (ID `40805771070`) produced source-only instrumentation as an artifact and passed ten unit tests without building or running CLASS. C42-B promotes **only the source-overlay compilation/import gate**, not the physical claim.

## Frozen lineage and source constraints
- Target branch `rims-c42b-compile-only-20261029` forks C42-A `033eb927653d724a5750342e9a44e5ce4d86a505`.
- Upstream CLASS commit `e85808324f51fc694d12e3ed7439552a3c3f9540`.
- Fixed RIMS patches SHA-256 `6bb31d11bf17c300666a2c2f2b79cac42aeef0a99e9ea53cf3db87403592ad74`, `c322fb05b7414be9f88cf90ff0580694e7677c8da91d78a5480ea9cf10f2b8dc`.
- Original C39-instrumented background SHA-256 `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`.
- Source-only C42-A run #1 final prepared background SHA-256 `dbbaa6b24b2b87cc6c058b4313ba026722467f8f23e80e8fde328e60c1467b9d`; NDF15 SHA-256 `c48e0b807df2d0cc2a859e59fc06483cd866bab199b65afb3db66f3b56070f38`.
- `rims_002`, frozen 81-design, RIMS parameters, original exact stability veto, `tol_background_integration`, and all CLASS solver settings are **not retuned**.

## Single authorized manual task
One manually selected GitHub `workflow_dispatch` with branch **`rims-c42b-compile-only-20261029`**. No scheduled triggers, auto-rescue, extra compute, posterior or evidence. Pipeline:

1. run source-insertion and negative unit tests;
2. reconstruct verified original RIMS-patched CLASS and C39 diagnostic;
3. regenerate the exact C42-A source bytes, failing on different SHA-256;
4. build the native C extension and import `classy.Class` from the pinned source folder, without instantiating it or calling `CLASS.compute()`;
5. save source/build/extension SHA-256 and failure logs even on errors.

Maximum job time 20 min; native build capped at 600 seconds, no automatic re-run. The workflow only runs the job on the matching C42-B branch; it is registered also in `main` solely so GitHub shows the Run workflow control.

## Claim boundary and next gate
GitHub green Success (if obtained) establishes only reproducible compile/import of the instrumented source. It **does not** show diagnostics are reachable during actual RIMS integration, prove trajectories unchanged, validate the stability source's dynamical meaning, obtain common-epoch observations, find a stable normalized background, perform inference, or support RIMS over alternatives. A separate C42-C manual one-probe run would still be required, with trial/accepted/output labels and a normalized-background veto kept ON. The C42-C procedure is not part of this deliverable.
