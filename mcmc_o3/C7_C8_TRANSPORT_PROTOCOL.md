# RIMS Phase II O3 — c7/c8 transport protocol

Status: frozen diagnostic protocol, 2026-09-07

## Claim boundary

This protocol changes sampler transport only. The physical model, priors, Planck 2018 + DESI DR2 + Pantheon+ likelihood target, and production gate remain frozen. No posterior, model preference, evidence, Bayes factor, or detection claim is promoted unless all matched models satisfy the declared gate.

The matched LambdaCDM chain already passed the frozen gate at c3 (`GetDist R-1 = 0.009025481710496091`, minimum headline ESS `= 1126.0428873008107`). It is retained as the fixed production baseline and is not re-run merely to consume additional compute.

## Frozen production gate

- GetDist `R-1 < 0.01`;
- minimum headline ESS `>= 1000`;
- target distribution unchanged.

## c6 transport diagnosis

The c6 chain-level audit identifies the dominant RIMS bottleneck as `Omega_scf`, especially chain 2. With 30% burn-in removed and Cobaya multiplicity weights expanded to Markov steps:

- chain-2 `Omega_scf`: integrated autocorrelation time approximately 727, ACF ESS approximately 7.6, half-chain drift approximately -0.80 sigma;
- chain-2 `H0`: integrated autocorrelation time approximately 359;
- pooled correlation `corr(H0, Omega_scf) approximately -0.687`;
- c6-only RIMS acceptance estimate approximately 0.837.

The corresponding c5-to-c6 change in chain-2 `Omega_scf` autocorrelation time was only about `727/756 = 0.962`, demonstrating that blind continuation gives negligible transport improvement.

A posterior-geometry audit shows that the `H0`--`Omega_scf` ridge is not purely linear. A linear conditional fit explains only about 47% of the `H0` variance, while a quadratic `Omega_scf` term increases this to about 58%; a modest multivariate polynomial using `Omega_scf`, `rims_alpha_U`, and `rims_shell_u_i` reaches about 78% in-sample. A simpler six-term predictor remains stable under leave-one-chain-out tests (`R^2` approximately 0.70--0.79), so curvature is not a single-chain artifact.

## c7 intervention

c7 is a target-preserving continuation from c6 with the learned covariance retained and only persistent proposal scale changed:

- scalar: `proposal_scale 2.4 -> 3.6`;
- RIMS: `proposal_scale 2.4 -> 4.8`.

The c6 prefix must remain exact. c7 is judged using both the frozen GetDist/ESS gate and the chain-level transport audit (`audit_transport.py`).

## c7 decision rule

1. If the frozen production gate passes, freeze the c7 artifacts and stop sampler tuning.
2. If the production gate fails but the dominant RIMS ridge clearly improves (especially chain-2 `Omega_scf` autocorrelation time and ESS per added Markov weight), one further fixed-scale continuation may be justified.
3. If acceptance changes but the ridge autocorrelation remains large, or if the chain-2 bottleneck does not materially improve, do **not** launch a blind c8 resume. Promote the nonlinear transport reset below.

The chain-level transport audit is diagnostic and never replaces the frozen production gate.

## c8 nonlinear transport reset (only if c7 transport remains inadequate)

The next candidate is a fresh four-chain run, not an append to c7. c6/c7 remain tuning/diagnostic artifacts and are excluded from the new production candidate. The likelihood target and original physical parameters are unchanged.

### Exact prior-preserving modulo shear

For the original uniform prior

`H0 in [55, 82]`, width `Delta_H = 27`,

introduce a periodic sampled coordinate `q_H in [0,1)` and a frozen predictor `Hhat(Omega_scf, rims_alpha_U, rims_shell_u_i)` learned only from pre-production diagnostic chains. Define

`H0 = 55 + 27 * frac(q_H + (Hhat - H_ref)/27)`.

For any fixed values of the other parameters, the map from uniform periodic `q_H` to `H0` is a measure-preserving translation on the unit circle followed by the constant scale factor 27. Therefore

`integral_0^1 dq_H L(H0(q_H), ...) = integral_55^82 dH0/27 L(H0, ...)`,

so the original uniform `H0` prior, posterior target, and evidence integral are preserved exactly (up to a set of measure zero at the wrap point). Choosing `H_ref` near the posterior centre keeps the sampled posterior far from the wrap discontinuity.

This is a lower-triangular nonlinear transport: `Omega_scf`, `rims_alpha_U`, and `rims_shell_u_i` remain physical coordinates, while `q_H` removes the curved conditional `H0` ridge. A second periodic shear for `rims_alpha_U` may be considered only if c7/c8 diagnostics show that the residual `Omega_scf`--`rims_alpha_U` ridge remains rate-limiting.

### Frozen simple c6 predictor candidate

Using post-burn c6 samples, standardize

- `o = (Omega_scf - 0.08768051)/0.02541329`,
- `a = (rims_alpha_U - 0.04626285)/0.02051664`,
- `u = (rims_shell_u_i + 1.53784825)/0.48203115`.

A compact cross-chain-stable predictor is

`Hhat = 68.1447995 - 0.678001096 o + 0.273304965 a - 0.0397724341 u - 0.152357637 o^2 - 0.00426803887 o a`.

This predictor is a sampler coordinate map only; it is not a cosmological fit or scientific result. Before any c8 execution it must be frozen in source, hashed, unit-tested for measure preservation, and preflighted against the exact same likelihood/model/prior configuration.

## c8 production hygiene

- start four fresh, over-dispersed chains in the transformed coordinates;
- freeze the transport map before sampling;
- retain original physical parameters in output for GetDist and scientific summaries;
- verify inverse mapping numerically and verify that all original prior bounds are respected;
- record source hashes, map coefficients, random seeds, package versions, and run lineage;
- apply the same 30% burn-in convention and the same frozen production gate;
- never combine c6/c7 tuning chains with the fresh c8 production-candidate chains for headline posterior or evidence statements.

This protocol is intended to improve sampler geometry without changing the scientific target.
