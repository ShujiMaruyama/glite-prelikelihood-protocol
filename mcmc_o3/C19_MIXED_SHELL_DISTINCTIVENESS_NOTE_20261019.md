# RIMS c19: mixed-species shell identity + all-scale Euler consistency

**Status (2026-10-19): conditional analytic extension and synthetic verification only.** This is *not* the authoritative 2026-08-07 integrated master replacement, a physical CLASS execution, or an observational posterior. It inherits c18 source lineage at commit `c1f1efb725976acdded80000cde11add6ad7de7d`.

## Scientific extension and exact assumptions

For separately conserved coupled dust `d` and uncoupled dust `c`, the existing RIMS bounded mass map is `m_d = m_U sqrt(s)`, `s=[1+exp(-2 alpha_U (phi-phi_t))]^{-1}`. Set `C=a^3 rho_c=constant>0`, `R=a^3 rho_d=K sqrt(s)`, `D=R+C`, `W=sqrt(F_d/2)=alpha_U (1-s)` on the declared positive-coupling, high-k intrinsic-force branch. Algebraically,

`W(D)=A-B(D-C)^2`, with `A=alpha_U>0`, `B=A/K^2>0`, `C<D<C+K`, `0<W<A`.

Derivative inversion: `C=D-W'/W''` and `A=W-(W')^2/(2W'')`. Fitted quadratic `b0+b1 D+b2 D^2` gives `C=-b1/(2b2)` and `B=-b2`. The published RIMS **coupled-only** identity `W=A-B R^2` is not a new c19 result. Nor is a parabola or partial DM coupling globally new.

In Newtonian gauge the exact coupled-minus-uncoupled dust Euler equation gives

`N_E=(Theta_d-Theta_c)'+Hcal*(Theta_d-Theta_c)+[D'/(D-C)]*Theta_d-k^2*(deltaE_d-deltaN_d)=0`.

The c19 **conditional cross-channel test** is to fit C from the mixed-shell curvature, hold it fixed, and verify this *same C* in the all-k Euler identity and number–energy closure, without refitting. The bulk velocity `Theta_T=f Theta_d+(1-f)Theta_c` obeys

`Theta_T'+Hcal Theta_T-k^2 Psi=f*k^2*alpha_d*delta_phi-f*(D'/(D-C))*Theta_d+f'*(Theta_d-Theta_c)`, with `f=1-C/D`, `f'=C D'/D^2`.

Thus bulk RSD/galaxy Euler measurements cannot simply be identified with intrinsic `F_d`. This is a mathematical forward-model gate, not a directly extracted observable; galaxy tracer transfers and survey covariance are mandatory. The generic two-fluid algebra is not new; the potential candidate is the shared bounded-shell composition parameter C across channels.

## Distinctiveness ledger and strongest criticism

- Coupled quintessence: Amendola, PRD 62, 043511 (2000), DOI 10.1103/PhysRevD.62.043511 — existing.
- Partial coupled DM: Morris & Green, Phys. Lett. B 741, 51 (2015), DOI 10.1016/j.physletb.2014.12.025 — existing.
- Modified Einstein vs Euler: Bonvin & Pogosian, Nature Astronomy (2023), DOI 10.1038/s41550-023-02003-y — existing.
- Gravitational-redshift degeneracy breaking: Castello et al., PRD 110, 103523 (2024), DOI 10.1103/PhysRevD.110.103523 — existing.
- Direct DM Euler test: Grimm, Bonvin & Tutusaus, Nat. Commun. 16, 9399 (2025), DOI 10.1038/s41467-025-65100-8 — existing.
- RIMS shell affine inverse: Maruyama's August 7, 2026 frozen master — previously derived.

No claim of proof of worldwide priority or exclusion of all possible mimicking mass maps. The severe concern is observational identifiability: `D` and intrinsic `W` are not automatically separable independent survey observables. Physical covariance includes D/W cross covariance, the coupled fraction, galaxy bias, relative velocities, and survey-dependent nonlinear windows.

## Actual executed work

A deterministic **synthetic-only** 12-occupancy-bin exercise used invented `A=0.06,C=0.1,K=0.9`, covariance `sigma_W=7.5e-4,rho=0.25`, and six train versus six held-out bins. With NumPy 2.3.5, 2000 Gaussian realizations yielded 1609 positive-branch fits and **391 failures**; a deliberately quartic alternative had a marginal holdout norm ~0.547 in the chosen noise units (not a significance or forecast). The analytic inversion and manufactured Euler identity closed to ~10^-16; those are not physical solver results. Ten c19 unit tests pass. No real CLASS, production MCMC, Bayes factor, detection, or model preference.

The finished English manuscript supplement, separate `references.bib`, Python, tests, frozen original c18 ZIP and dated authoritative 40-page master PDF are in the accompanying conversation artifact `RIMS_C19_FULL_DELIVERY_20261019.zip`. Their original archival bytes are preserved. The GitHub branch presently carries this checkpoint and its machine-readable decision ledger, **not the full manuscript/source ZIP**.

## Next hard gates

1. Resolve the already frozen c18 one-start native CLASS parity and then all eight fixed starts, without automatic dispatch.
2. Reconstruct true intrinsic F_d versus bulk Euler response in the evolving two-fluid solver; hold C fixed from shell curvature; verify all-k null against both gauges and independent-code replication.
3. Complete predeclared **81-background** potential robustness scan and classified Xi regimes.
4. End-to-end mock recovery using realistic survey response, cross-covariance, nuisance, and nonlinear k_max(z), then blinded held-out data protocol.
5. Only after matched real Planck 2018 + DESI DR2 BAO + Pantheon+ MCMC satisfies **GetDist R-1<0.01 and minimum headline ESS>=1000**, consider a posterior claim. No BFs without proper evidence/prior audit.

No automatic workflow, GitHub Action, or long-running production job is created by this note.
