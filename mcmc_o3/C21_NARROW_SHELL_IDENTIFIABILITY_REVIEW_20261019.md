# RIMS c21: narrow-shell curvature-identifiability audit (2026-10-19)

**Status:** analytic and idealized Gaussian simulation; NO RIMS V18.29 CLASS run, NO 81 physical trajectory scan, NO MCMC, NO model-evidence claim.

The *historically executed* August 7, 2026 weak-branch RIMS benchmark is `alpha_U=0.01`, `0.128630 <= s <= 0.128846`. For the conserved coupled/inert dark dust shell, `u=(D-C)/K=sqrt(s)`, `W=sqrt(F_d/2)=A(1-u^2)`; the **intrinsic coupled-species force plateau**, not a directly observed bulk galaxy-Euler signal.

## Exact finite-window tests

Let `u_±=u_c±h` and `h=(sqrt(s_max)-sqrt(s_min))/2=0.00015050135814520527`. Then

`T_W = W(u_c)-[W(u_-)+W(u_+)]/2 = A h^2 = 2.2650658803551342e-10`.

The first-order drift is `|W(u_+)-W(u_-)|=A(smax-smin)=2.16e-6`; `W_c=0.008712620226506589`, `F_d=1.5181950242266343e-4`.

Three ideal independent equal-Gaussian `W` errors (fixed exactly known `u`) yield curvature expected `Z=A h^2/(sqrt(3/2)*sigma_W)`, which at expected one-sided 5 sigma requires per-bin fractional intrinsic `sigma_F/F ≲8.49075708e-9`. This is **only 50% Gaussian detection power**, not 95%. Five-sigma threshold with 95% power requires `sigma_F/F ≲6.38897225e-9`; the two-bin first-order drift needs only `sigma_F/F ≲7.01213003e-5`. Ratio of required precision: about 8258.5. These are idealized design bounds, **NOT DESI/Rubin/Euclid capabilities or observational forecasts**. D/W cross covariance, sample windows and galaxy bias are omitted in this bound.

For a symmetric `n`-bin quadratic design the nuisance-projected curvature Fisher information scales `I_BB ~ h^4/sigma_W^2`. A locally matched smooth competing curve can differ only at second order over this small window. This standard regression/calculus math is **not claimed as globally new**. Its quantitative application to the archived *actual RIMS model-run shell interval*, and the associated fail-closed experimental-performance criterion, are c21's incremental research deliverables.

## Completed reproducibility tasks

- 100,000 seeded Gaussian synthetic draws **per** six ideal fractional noise cases, seed 21101926; exact analytical power curve independently agrees with Monte Carlo replay.
- **22/22 local Python tests PASS** (12 c21 visibility; 10 81-scan postprocessor), **JSON replay byte-identical**.
- New **81-scan table evaluator** checks complete 3×3×3×3 family grid, physical normalization and scalar effective-mass stability, redshift endpoints, duplicate/missing trajectories, `Xi^2≈m2_over_H2`, and force-curvature leverage, without running physics. Critically a valid synthetic table is labelled `TABLE_81_VALID_PROVENANCE_UNVERIFIED`: **no physical 81 scan claimed**.
- New **9-page independent English supplement** compiled from clean Overleaf ZIP; 0 changed pixels at 0.7× for all nine clean-build PDF pages, 0 text diffs, font embedding PASS, no LaTeX undefined references or overfull/underfull.
- Frozen `RIMS_C20_CUMULATIVE_DELIVERY_20261019.zip` is **included unmodified** in c21 release with SHA256 `3a47c9a25637ae07e2dab7c9c0e741318209af62ebde1a385d22e9692230030f`.

## Delivery (ChatGPT ZIPs; executable Python and manuscript source not pushed to this branch)

- `RIMS_C21_CUMULATIVE_DELIVERY_20261019.zip`: SHA256 `4c20e9cda04727e82205b6ebf3eb09d616678810f82a34fdf7e8d113e0dd0a9a`; manifest-verified 22 members, c20 parent original archived.
- `RIMS_C21_OVERLEAF_20261019.zip`: SHA256 `f84217cb759e1a5497e2be05e2e45a7d752e2e4ae4182f91903a373e8304df36`.
- Main paper `manuscript/main.pdf` (in cumulative ZIP); SHA256 recorded in internal release audit.

## Immutable hard gates

c18 real pinned CLASS V18.29 parity at all eight starts; actually **execute** 81 potential-variation backgrounds and classify `Xi`; nonlinear `C_NL(k,z)`, `k_max(z)`, `C_total`; second independent Einstein--Boltzmann solver; survey-level joint covariance and matched comparator. Matched Planck 2018+DESI DR2+Pantheon+ inference is not production until GetDist **R-1 <0.01** and headline minimum **ESS>=1000**. Never claim production posterior, Bayes factor or model preference without qualifying executed artifacts.

No new workflow registered or dispatched by c21.
