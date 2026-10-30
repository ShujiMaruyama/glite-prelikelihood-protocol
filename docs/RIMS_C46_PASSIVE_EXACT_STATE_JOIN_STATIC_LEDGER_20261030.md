# C46: passive exact-state physical-mass observer — STATIC RESEARCH CHECKPOINT (2026-10-30)

Source baseline: `rims-c45b-exact-curvature-discriminant-20261030` commit `810dc0b298d2f37bc1da1ea412d4210217eeb2ca`. The original C38–C45b branches remain unchanged.

## Newly implemented and locally tested — not yet uploaded source
- C45a established lossless `%a` capture of full NDF15 committed state vectors after COMMIT, with no additional derivative call.
- C46 source-only, explicitly opt-in `RIMS_C46_PASSIVE_TRACE=1`, records only the input full state `y` and `H,Vpp,rho_idm,phi,m_eff2/H2` from **already successful** original `background_derivs -> background_functions` calls. The patcher requires C39 post-overlay `background.c` SHA-256 `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`. No new background evaluations or numerical rescue.
- An independent auditor joins prior derivative-evaluation events to COMMIT snapshots only for identical full hexadecimal `(x,y)` in the same original NDF15 scope. No exact match -> `ACCEPTED_G_NOT_OBSERVED`. Matching masses require original term decomposition and strict source consistency. Accepted sign changes require **adjacent accepted measured** points; missing intermediate measurements are not interpolated.
- Local suite: 61 PASS (C43 17, C45a 14, C46 30), including synthetic C compilation/trace, corrupted-log tests, exact physics decomposition and local original C44 artifact SHA audit. These are **synthetic/local tests, not production CLASS**.

## Exact new conditional source predictions
`beta=alpha_U(1-s)`, `kappa=m''/m=3 beta^2 - 2 alpha_U beta`,
`beta_{,phi}=-2 beta(alpha_U-beta)`.
For `x=ln m` (beta != 0), `d^2 beta/dx^2=2 d beta/dx`.
This parameter-free written null relation is not unique if `d beta/dx=0`; the constant-coupling exponential case also passes trivially. Only joint nonzero-evolution and full physical forward comparisons would discriminate.

Original C44 rejected Newton trial (not accepted): s=0.64999999997593583, kappa=-3.3249999999759356e-05, m_eff2/H2=-1.0049389722010728e-10; 618 COMMIT positions exist but their g was not measured. Absolute archive SHA-256:
`cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`.

## Exact claim boundary and work needed
This GitHub checkpoint currently contains this *research ledger* only. Complete C46 Python/C patchers, 61 local tests, the original C44/C45a/C45b evidence and four-page single-column PDF are in the separately generated C46 local delivery ZIP; **those files have not yet been uploaded to this repository**. No C46 GitHub Actions workflow is registered, and no C46 native CLASS compute has run.

Hard gate: compile exact pinned source with all C39/C43/C45/C46 additive overlays and run a single manually authorized frozen RIMS_002 native attempt. Preserve native stderr and exact-match audit. Any mismatch or lack of matches fails closed; never retune threshold, infer accepted values by interpolation, or present a physical stability or numerical convergence proof. Future explicit observables require proper Planck/DESI/Pantheon+ matched solver/inference; no model superiority or Bayes factors are claimed.

No subscription, purchase, or paid infrastructure is needed for this static checkpoint.
