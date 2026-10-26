# RIMS c33 — Actual CLASS pilot identifiability and adversarial prior-art boundary

**Date:** 2026-10-26 (JST). This is a science-first, read-only audit built on the executed c32 pilot, NOT a new physical CLASS run, an 81-case trajectory scan, a DESI cosmological likelihood, a detection, or a production model comparison. Distinguish RIMS from IFC, PORG, PBH/Hawking, and all other research branches.

## Source ledger

Original successful c32 physical GitHub Run #3: [40247625798](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/40247625798), source SHA `1e79b4add46cbd13643c1933e18fcfc952b1c206`, original artifact ZIP SHA256 `5263f9489ada68adcc76c6d5e756ea95b3dfff40dec2448d2f87cea0efbe85dd`, inner SHA manifest verified. Original 81-case frozen SHA `0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0`.

`rims_000`: exponential potential, alpha_U 0.01, omega_phi0 0.001, initial s_i 0.1. Native patched CLASS computed 3 mass-normalization backgrounds plus the final background. Total final z/phi history 40,000 native points; 0<=z<=3 has 1,721 native physical samples. Independent c26 initial occupancy gate and c27 raw source-history audit passed. c32 source-native z3 mass bracket passed. **Original strict c24 status stays PHYSICAL_REJECT (sole issue z_0to3_coverage_failed)**; the independent c32 *sampled bracket* classification is `NATIVE_GRID_BRACKETED_SAMPLED_PASS`. Neither is a continuous-field or perturbation safety theorem. 80 frozen cases remain UNATTEMPTED.

## Calculated, source-bound pilot discriminants

Derived from the saved complete c32 sampled `background` array, with `Xi(z)=sqrt(max(0,m_eff²/H²))`:

- min Xi = 0.06241009396523685; **max Xi = 0.28506845738112**. Under previously frozen classification thresholds, **shielded (max Xi<1)**, neither transitional nor resolved-QS.
- s_min = 0.09982144604791479, s_max = 0.09984461232053336; Δs = **2.3166272618571626e−5**.
- With `u=sqrt(s)`, `W(u)=alpha_U(1-u²)`, native root half-span `h=(sqrt(s_max)-sqrt(s_min))/2`, midpoint `u_c=(sqrt(s_max)+sqrt(s_min))/2`, `S_W=alpha_U h² = 3.359836126067812e−12`.
- Fractional sagitta `h²/(1-u_c²)=3.7324587923603964e−10`, and idealized three independent equal-error points at 5σ, 50%-power ceiling `2 h²/[5 sqrt(3/2) (1-u_c²)] = 1.2190159369663571e−10`.
- Relative full intrinsic-force-root W drift across 0<=z<=3 native samples ~2.5735461097782362e−5.

**Interpretation:** This one corner is genuinely source-audited as a *weak-response / narrow-shell* native pilot. Its intrinsic W curvature is extremely difficult to resolve in this idealized design. No galaxy-velocity, lensing, gravitational-redshift, or Euler-force observable has yet been calculated from W, so these numbers must NOT be marketed as a survey precision forecast or a direct fifth-force constraint. No dominance over LCDM or generic coupled scalar models is established.

## Overlap / novelty veto

Prior art already covers (1) a dark matter mass depending on a scalar, (2) a dark-sector fifth force, and (3) lensing/RSD versus modified-gravity degeneracies. RIMS cannot claim any of these ideas alone as first of its kind.

- Antusch, King & Wang, **Coupled Dark Energy and Dark Matter for DESI: An Effective Guide to the Phantom Divide**, JCAP 09(2026)115; DOI https://doi.org/10.1088/1475-7516/2026/09/115. Uses `m(phi)` field-dependent DM mass and shows late-time effective crossing without a phantom field.
- **Disentangling modified gravity from a dark force with gravitational redshift**, Phys. Rev. D 110 103523 (2024), DOI https://doi.org/10.1103/PhysRevD.110.103523. RSD+weak lensing+CMB can be degenerate between dark force and modified gravity; gravitational redshift is relevant to separating them.
- **Comparing the motion of dark matter and standard model particles on cosmological scales**, Nature Communications (2025), DOI https://doi.org/10.1038/s41467-025-65100-8. Provides a direct Euler-response fifth-force test. RIMS would have to compare with its actual observable force parameter, not pretend the intrinsic root W is that measured parameter.

**Eligible, still conditional RIMS research novelty:** the theory-specific bounded shell-closing mass relation PLUS genuinely native nonadiabatic modes PLUS a single matched metric/matter/radiation/Euler/Weyl/velocity/galaxy-bias/gravitational-redshift transfer chain, yielding distinctive shared-redshift/scale null relations that no competitor under matched nuisance freedom reproduces. These conditions have NOT been demonstrated and should be falsified, not declared unique.

## Non-negotiable next campaign

Execute all predeclared 3 potential families x 3 alpha_U x 3 omega_phi0 x 3 initial occupancies = 81 native background trajectories; retain every failed attempt and no cherry-picking. At each source-validated trajectory record max_z Xi (<1, 1–10, >=10), native mass minima, s span, z=3 exact-vs-bracket and source hashes, with a 81-row coverage ledger. Failures are data, not deletions. Do not start full 81 automatically, and do not collapse pilot-only Xi classifications into a global theorem. A second independent CLASS/Boltzmann implementation, c18 all-eight matched parity, nonlinear cuts and C_tot matching must precede production interpretation. Inference gate remains GetDist R−1 < 0.01, minimum headline ESS >= 1000.

## Executable source

`mcmc_o3/c33_pilot_identifiability.py` consumes the original GitHub artifact ZIP supplied as `--source-zip` and writes a fresh JSON output using `--output`. It checks outer and inner original artifact digests, exact frozen source, historical c24 rejection, independent c26/c27/c32 statuses and computes Xi/W indicators directly from all native z<=3 samples. **It never opens CLASS or starts MCMC**. The separate full local replay package `RIMS_C33_IDENTIFIABILITY_READONLY_20261026.zip` contains the original artifact, expanded diagnostics, two native-only figures, 81-case CSV coverage ledger, and eight additional local synthetic/integrity tests (8/8 local pass). The local script and GitHub script are equivalent read-only audits but have distinct layouts; do not assert byte identity or GitHub Actions pass for c33 unless checked.
