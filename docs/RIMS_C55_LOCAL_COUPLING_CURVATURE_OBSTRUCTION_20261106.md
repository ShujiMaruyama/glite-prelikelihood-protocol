# RIMS C55: Real-C44 source-constrained coupling-curvature obstruction (2026-11-06)

Shuji Maruyama — Independent Researcher, Muroran, Hokkaido, Japan — ORCID 0009-0007-5034-7634  
© 2026 Shuji Maruyama. All rights reserved.

This is a scientifically bounded new calculation on the **real original pinned native CLASS C44 rejected Newton trial**; it is NOT a new native CLASS execution, accepted-state measurement, detection, or model-wide no-go result.

## Original native evidence

Source: https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/41000757103

Original C44 stderr SHA256: **9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d**.

Original C44 evidence: 618 committed NDF15 coordinates, 845 trial evaluations, then the first Newton evaluation at the next proposed scale factor rejected under the **unchanged** source cutoff −1e−10. No accepted-state effective-mass measurement is present.

Recorded UNCOMMITTED trial:
- phi = 4.4399999947111519; s = 0.64999999997593583.
- H² = 1.9196310273959685e26; rho_idm = 1.9339468989379002e20.
- kappa = −3.3249999999759356e−5; 3 rho_idm kappa = −1.9291120316765940e16.
- V'' = 7.2704406617212974e−103.
- m_eff²/H² = −1.0049389722010728e−10.

## An exact source-coupling result

Original logistic source:

s = [1 + exp(−2 alpha_U (phi−phi_t))]^−1,

kappa = m_d''/m_d = alpha_U² (1−s)(1−3s)
= alpha_U² [3(s−2/3)²−1/3].

Thus kappa >= −alpha_U²/3, with minimum at s=2/3. **The real trial's kappa is 99.75% as negative as this global lower bound.** The ratio V'' / |3 rho_idm kappa| = 3.76880167784e−119.

## Quantified local, positive-slope-only obstruction

For the ORIGINAL UNIT-AMPLITUDE, ZERO-POLYNOMIAL-EXPONENT potential branch V(phi;lambda)=exp(−lambda phi), phi>0, lambda>0, calculus proves:

V'' = lambda² exp(−lambda phi) <= 4 exp(−2)/phi²,

attained at lambda*=2/phi. At the recorded trial field, **V'' maximum over all positive lambda is 0.02746028803649**; the source would need **9.4810042806252e13** to satisfy the original fixed-state stability cutoff.

The proof remains valid after allowing the source Friedmann H² to respond consistently to the potential difference, since, at fixed a, phi, phi', rho_idm and other densities:

H²(lambda) = H²(original) + [exp(−lambda phi)−exp(−lambda_original phi)]/3 <= H²(original)+1/3.

For all positive lambda, the original gate-pass inequality is strictly impossible:

3 rho_idm kappa + V'' + 1e−10 H²(lambda)
<= 3 rho_idm kappa + 4 exp(−2)/phi² + 1e−10 [H²(original)+1/3]
= approximately **−9.4810042806253e13 < 0**.

This is a **source-specific frozen-local-trial theorem**, NOT an exclusion of all parameter-dependent cosmological trajectories: changing lambda in a real CLASS cosmological solution also changes its shooting and evolving background.

## Numerical uncertainty robustness

Even granting separate worst-case ±0.1% relative variation of rho_idm, kappa, phi, H² (conservative independent input box), the upper bound on the gate-pass expression is **−3.7050783019e13 < 0**. The sufficient interval certificate stops being negative at about 0.164182% independent relative variation; this is **not** a physical transition.

Source-local conditional calculations show the trial density ratio rho_idm/H² = 1.00745761625e−6 and the limit for approximate veto passage = 1.00250626567e−6. A same-epoch hypothetical phi adjustment would reach g=0 near phi=3.4697604; it is not a measured Newton correction or accepted value. A radiation-like crossing estimate a≈3.92651e−10 is not a validated accepted root bracket.

## Independently executed tests and full deliverable

**16/16 software/math checks PASS.** Full ORIGINAL 2083-line SHA-locked native C44 stderr was analyzed with two independent programs, 80-digit Decimal and 100-digit mpmath, which agreed to much better than 1e−40 relative on the physical upper bounds. Original-source tamper refusal and 400 positive-slope samples were also tested. ZIP was extracted into a separate directory; all SHA-256 member checks, CRC and rerun tests PASSED. These are software tests, not 16 physical runs.

- Finished six-page, A4, single-column, visually verified technical PDF titled **RIMS_Source_Constrained_Curvature_Obstruction_C55.pdf** (SHA256 **d976da9eef7c66d3b8b3488097e930d7f562331f20d96a40f6405ea2bc774d5a**).
- Complete audit ZIP **RIMS_C55_Physical_Curvature_Obstruction_20261106.zip** (9,412,655 bytes; SHA256 **1faaf37ccc8ae6abf9eb1813d0fc978b915c35dfc31e6107411cf2febb7b6974**), containing the original raw C44 log, two independent programs, 16 tests, deterministic JSON, two true source-derived graphs, paper/main.tex, separate paper/references.bib, titled PDF, SHA manifest and reproducibility shell script. It also includes unchanged prior C55 provenance ZIP SHA256 **9f32711560181feb9dc11f5325ddd6a9ba56ec318ed2659bdc3152be705f4913**.

**Only this browser-readable Markdown is being committed to GitHub here.** The complete executable and PDF are in the separate ZIP delivery; do not assume they were pushed to GitHub.

## Open physics hard gates

C55 real CLASS static compilation **not yet performed**; no new native compute; no accepted-state g; no observer-vs-original parity; no normalized background, coupled gauge-invariant stability result, 81 background trajectories, independent Einstein–Boltzmann parity, production Planck/DESI/Pantheon+ posterior, Bayes factor, observational superiority or detection. Next: compile the pinned native C55 observer (manual static-only, original threshold unchanged), then separately authorize and audit one frozen real CLASS case, then solve the actual coupled perturbation operator. Do not treat source-defined negative local m_eff² as measured fast physical instability.

The original full RIMS manuscript is not replaced, abridged or claimed to be newly completed by this focused supplementary theorem.
