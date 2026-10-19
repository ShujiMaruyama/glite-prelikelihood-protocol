# RIMS c20: conditional kinetic null and correlated-identity fail-safe (2026-10-19)

**Stage:** analytical extension and synthetic numerical test; **no physical RIMS V18.29 CLASS, no real survey inference, no MCMC run**. This is an *addition* to, not a replacement of, the immutable RIMS core master dated 2026-08-07 and c19.

The c19 mixed shell assumes separately conserved number currents for an inert dust component (C=a^3\rho_c>0) and a coupled dust component (R=a^3\rho_d=K\sqrt{s}\), where (s=[1+\exp(-2\alpha_U(\phi-\phi_t))]^{-1}). Let (D=C+R), (W=\sqrt{F_d/2}=\alpha_U(1-s)>0), with (F_d=2\alpha_d^2) the *intrinsic coupled-species deep-subhorizon* force plateau, **not** observed galaxy bulk Euler response. Then (W=A-B(D-C)^2) was already derived in c19.

## Conditional cross-channel extension

Where (W, W_D, W_{DD}) are nonzero and the positive physical branch holds:

* (C=D-W_D/W_{DD}\) must be constant;
* (\phi_N=D_N W_{DD}/(W W_D)), with (N=\ln a\);
* (\Omega_K^{\mathrm{shell}}=(D_N W_{DD}/(W W_D))^2/6).

For a single canonical scalar in spatially flat Einstein GR with only dust, radiation and optional vacuum energy, independent Raychaudhuri expansion gives
[
\Omega_K^{\mathrm{geom}}=-\frac13\frac{d\ln H}{dN}-\frac12\Omega_m-\frac23\Omega_r.
]
Their difference must vanish, irrespective of the form of (V(\phi)). This is a **conditional algebraic joint null**, not a theory-unique fifth-force law or a demonstrated observational observable. Its failure, after controlling missing components, coupling assumptions and survey covariance, can falsify the minimal RIMS branch. Its apparent success does not uniquely identify RIMS.

The c19 Euler residual was constructed by setting its time derivative equal to the theoretical RHS. Thus it was **not an independent physical perturbation check**; c20 downgrades that claim explicitly. The correct next physical test requires independently evolved two-component velocities and number/energy perturbations in the pinned native CLASS hierarchy and a second code.

## Executed synthetic tests, never production

* Self-consistent toy FRW Raychaudhuri ODE integrated for 2,001 time points; the scalar potential (V(\phi)) was reconstructed, not a prescribed RIMS potential family. Analytic kinetic null max (6.94\times10^{-17}), independently finite-differenced Hubble evolution error (9.83\times10^{-8}), reconstructed KG residual (1.06\times10^{-6}). No physical CLASS model or observational preference tested.
* Correlated GLS held-out synthetic test, 12 toy shell points, six train/six held-out, 1,500 Monte Carlo realizations per hypothesis and per density-noise setting, fixed seed 20102026. Quadratic ground truth falsely rejected at nominal (\chi^2_6(0.95)) threshold: `66/1500` with `sigma_D=0`; `826/1500` when sigma_D=.01 but D errors improperly omitted vs `92/1500` when joint cross covariance included; `1481/1500` for sigma_D=.03 omitted vs `118/1500` included. First-order joint correction is **not exactly calibrated** at large sigma_D (7.9% rather than nominal 5%). A stipulated quartic competitor gets only `106/1500` joint rejects at sigma_D=.03, so **no robust model discrimination**.
* Positive-domain quadratic shell fits `1242/1500,1076/1500,741/1500` for sigma_D=0,.01,.03 respectively. All failed fits are reported, no selection-only uncertainty.
* **15/15 c20 tests PASS** (numerical identities, finite difference convergence, cross covariance, predictive-covariance Monte Carlo, branch-domain rejection). These are mathematical and synthetic checks, **not** RIMS CLASS parity.

## Prior art boundary

Coupled quintessence (Amendola 2000), partial coupled DM (Morris--Green 2015), Euler-vs-Einstein and gravitational-redshift discriminators (Bonvin--Pogosian 2023; Castello et al 2024), direct Euler tests (Grimm et al 2025), coupled-dark-sector EFT (Aoki et al 2026), generalized GLS correlated cross-validation (Baade 2018) already exist. RIMS c20 does *not* claim their components. The candidate increment is parameter-sharing across shell, GR kinetic budget and dark-fluid transfer under narrow, explicit assumptions; global novelty priority has **not** been proven.

## Files and continuity

The fully editable LaTeX with `references.bib`, three vector figures, manuscript PDF (7 pages), tested numerical Python and 15 Python tests, raw synthetic results, independent reproducibility audit, and **byte-for-byte preserved c19 full-delivery ZIP** are in the conversation artifact `RIMS_C20_CUMULATIVE_DELIVERY_20261019.zip` with SHA256 `3a47c9a25637ae07e2dab7c9c0e741318209af62ebde1a385d22e9692230030f`. Its 17 included files are SHA256-manifest verified. c19's frozen ZIP embeds the prior master and c18/c17 lineage. The separate Overleaf-ready ZIP SHA256 is `a15a3d493a8d7b114c6074ed2b32de623dcf0cffeb7e7ccee9e5344f34277937`. **This GitHub branch contains scientific ledger, not necessarily the complete source ZIP.**

The submitted PDF was clean rebuilt with pdfLaTeX+Biber, no citation/overfull/underfull warnings, rendered/inspected, fonts embedded. The c20 main mathematical result remains conditional; neither a production constraint nor a direct experimental signal is claimed.

## Immutable remaining hard gates

1. c18 true pinned RIMS V18.29 one-start and eight-start numeric parity against uninstrumented CLASS (no automatic workflow dispatch).
2. Predeclared 81-background potential-family and occupancy scan with normalization, stability and (\Xi\) shielding classification.
3. Full physical linear transfer mapping of intrinsic coupled (W), total (D), grav redshift/lensing/RSD tracer velocities with joint nuisance and covariance.
4. A second independent Einstein--Boltzmann implementation, nonlinear (C_{NL}(k,z)), (k_{max}(z)), (C_{tot}=C_{data}+C_{th}+C_{sys}).
5. Matched Planck 2018 + DESI DR2 BAO + Pantheon+ posterior only after **GetDist R-1 < 0.01** and minimum headline **ESS >= 1000**. No Bayes factor or LambdaCDM competitiveness without matching evidence.

No new GitHub Actions run, no automatic follow-on, and no long production calculation is created by this note.
