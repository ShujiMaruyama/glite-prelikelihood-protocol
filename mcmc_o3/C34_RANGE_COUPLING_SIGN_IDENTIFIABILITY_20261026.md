# RIMS c34: source-grounded mass range, coupling and identifiability

**Created:** 2026-10-26 JST. **Author:** Shuji Maruyama, Independent Researcher, Muroran, Hokkaido, Japan. © 2026 Shuji Maruyama. All rights reserved.

## Executed evidence that must NOT be relabeled

Continue from successful actual c32 GitHub Run [40247625798](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40247625798), physically executed `rims_000` ONLY (three native CLASS normalization solves plus one final background). Original source artifact SHA256 `5263f9489ada68adcc76c6d5e756ea95b3dfff40dec2448d2f87cea0efbe85dd`; frozen 81 inputs SHA256 `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`. C26 initial occupancy, c27 full native history and c32 direct two-sided source-grid mass brackets passed. Original c24 decision **PHYSICAL_REJECT** is immutable (sole reason `z_0to3_coverage_failed`). c32 has *different*, sampled-only result `NATIVE_GRID_BRACKETED_SAMPLED_PASS`; not continuum or tensor safety. Other 80 cases still UNEXECUTED.

## New physics interpretation correction

The implemented source `rims_o3_patch/base_parts/part02_03` supplies:

```text
s(phi)   = [1+exp(-2 alpha_U (phi-phi_t))]^-1
m/m_ref  = sqrt(s/s_ref)
beta     = d ln m / d phi = alpha_U (1-s)
dbeta/dphi = -2 beta (alpha_U-beta)
(m''/m)  = alpha_U^2 (1-s)(1-3s)
```

The original c24 `visibility='shielded'` for `max_Xi<1` is only a **historical classification**, not evidence for physical fifth-force/Yukawa screening. Native c32 `Xi=sqrt(m_eff²/H²)` lies **0.062410093965..0.285068457381**: under a standard positive canonical propagator interpretation, even the shortest scalar Compton range is **>3.50793 Hubble radii**, i.e., very long-ranged in mass terms.

To avoid equating *range* to *amplitude*, derive source mass coupling on the 1,721 actual native z in [0,3] rows:

- `beta_min=0.009001553876794667`, `beta_max=0.009001785539520853`.
- Under **extra assumptions**, define a *non-observational* dark-dark, linear, canonical QS proxy `Gamma_DD^proxy(Q,z)=2 beta² Q²/(Q²+Xi²)`, where `Q=k/(aH)`. The massless-force proxy range is **0.0001620559443936742..0.0001620642857990535**, i.e. ~**0.0162%**, and its tiny z-drift `8.3414e-9` is *different* from its absolute strength. `Q>=10` yields mass factor `>=0.9991880196` for the sampled background.
- Native source z=2.99958609995 has measured `H=0.0010201447221303537 Mpc^-1`. For a conditional illustrative `k=0.01h/Mpc`, fixed `h=0.6802`: `Q=26.66796589`, Yukawa-only factor `0.99999452319`, proxy Gamma `0.0001620550568`. NOT an RSD/lensing/gravitational redshift transfer prediction.
- The c33 `1.2190e-10` *ideal three-node shape-curvature relative measurement ceiling* CANNOT be called the total dark-force detection threshold.

The factor of 2 assumes standard canonical/reduced-Planck scalar conventions and does not account for interacting/inert dark fractions, nonlinear chameleon-like screening, fluid/gauge transfer or observational nuisance covariance. **The implemented background m_eff may not equal a full gauge-correct propagating pole unless verified by perturbation analysis.** This is a disciplined testable proxy, not a full physical forward model.

## New analytical sign gate and 81 frozen-case partition

The mass curvature `m''/m=alpha_U²(1-s)(1-3s)` changes sign at **s=1/3**, a source-exact algebraic prediction *independent of the chosen scalar potential*. The frozen 81 *initial inputs*, not physical solutions, split into **27 positive (s_i=.10), 27 zero (s_i=1/3), 27 negative (s_i=.65)**. At fixed alpha, switching the initial occupancy predicts the sign of **this mass term**, but the total scalar effective mass also contains `V''` and density terms. This sign rule makes a rigorous prospective, non-cherry-picked test when full CLASS trajectories are eventually run.

The canonical hypothetical Yukawa proxy also obeys the **strict envelope** `0<Gamma_DD^proxy<2 alpha_U²` for s∈(0,1), m_eff²≥0. For frozen alpha `0.01,0.05,0.10` (27 cases each), the envelope percentages are respectively **0.02%, 0.50%, 2.00%**. These are NOT actual 81 observational amplitudes or exclusions; future percent-level Euler constraints carry their own model, bias, covariance, and parameter definitions.

## Explicit identifiability / uniqueness obstruction

For source latent `u=sqrt(s)`, RIMS beta is quadratic `beta_RIMS(u)=alpha_U(1-u²)`; the ordinary second derivative is `-2 alpha_U`. Select three nodes u_j and define `x=(u-u_min)/(u_max-u_min)`, then

```text
beta_epsilon(u)=alpha_U(1-u²)+epsilon (x-x_1)(x-x_2)(x-x_3).
```

This other smooth coupling **exactly matches all three values** and differs between them, and can be integrated into a smooth alternative mass function `m_epsilon(phi)=m_ref exp integral beta_epsilon dphi`. It is NOT a fully solved competing cosmology, but it disproves a claim that any three exact latent-force-root measurements uniquely establish RIMS. The RIMS-specific high-risk novelty is therefore a *joint constrained transfer signature* involving seven native initial modes, dark-number/energy perturbations, Euler velocity, Weyl potential and time potential, with a truly matched competitor and shared nuisance covariance; this remains **unexecuted**.

## Prior-art veto and references

Existing work already develops scalar-dependent dark mass and additional dark forces (Uzan & Pitrou, PRD 109 103505, 2024), the RSD/WL versus Euler/gravitational redshift ambiguity (Castello et al., PRD 110 103523, 2024; Nature Astronomy 2023, DOI 10.1038/s41550-023-02003-y), observational dark-motion tests (Nature Communications 2025, DOI 10.1038/s41467-025-65100-8), expanded Euler equation alternatives (Zheng et al., PRD 113 083520, 2026) and coupled DE/DM EFT (PRD 113 044053, 2026). **No priority over those general ingredients is claimed.** Need independent full source and matched numerical likelihood to establish uniqueness.

## Reproducibility and executed claim boundary

A cumulative **RIMS_C34_RANGE_COUPLING_FALSIFICATION_20261026.zip** includes the unchanged authentic c32 artifact, full independent read-only source code `c34_source_audit.py`, an English journal-neutral technical note, Japanese handoff, separate `references.bib`, three actual/conditional diagrams, numerical JSON, SHA manifest and **19 local offline regression tests (19 PASS)**. The GitHub-side short companion `mcmc_o3/c34_frozen_mass_curvature_gate.py` computes the 81 *analytic input* signs independently; it does NOT execute 81 physical backgrounds. Both scripts are complementary and have different scopes; do not assert byte identity.

**c34 physical CLASS calls=0; c34 GitHub Actions runs=0; frozen physical cases attempted overall=1/81; production MCMC=0; model preference / detection / Bayes factor = NONE.** Retain the original c32 failures and no-premature-promotion rules. The next credible phase is a manually authorized fully enumerated 81-background campaign, followed by independent perturbation/gauge-mode checks and matched competitor full likelihood. Production gate remains GetDist R-1 <0.01, minimum headline ESS >=1000.
