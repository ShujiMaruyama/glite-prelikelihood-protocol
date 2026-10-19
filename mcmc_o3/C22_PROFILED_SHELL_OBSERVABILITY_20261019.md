# RIMS c22 — covariance-profiled identifiability and exact nuisance degeneracy (2026-10-19)

**Stage:** mathematical and synthetic Gaussian diagnostics only; NO native CLASS, NO 81-trajectory physical scan, NO production posterior, Bayes factor or model preference.

## Frozen background and equation

From the archived August 7, 2026 RIMS weak model-run benchmark: alpha_U=0.01, s in [0.128630,0.128846]. Write u=sqrt(s), u_c=mean of sqrt-endpoints, h=half their separation, W=sqrt(F_d/2)=A(1-u²). W is the intrinsic force-root on the coupled-species high-k plateau, NOT a galaxy Euler measurement. The sagitta Ah²=2.2650658803551342e-10 was already in c21.

Profile an arbitrary intercept and slope: x_i=u_i-u_c, q_i=x_i², X=(1,x), y=beta_0+beta_1*x-B*q+epsilon. For positive-definite covariance Sigma, the curvature Fisher information is q^T P q, where P=Sigma^-1 -Sigma^-1 X (X^T Sigma^-1 X)^-1 X^T Sigma^-1. The expected Gaussian test separation is Z=|B|sqrt(q^T P q). This is standard GLS/Schur-complement mathematics, NOT a newly discovered statistics theorem.

## Conditional quantitative results

Under n independent equal-variance known-u observations over a symmetric window, I <= n*h^4/(4 sigmaW²), saturated for 50% at center and 25% at each endpoint in continuous weights. Uniform continuous allocation has 4n*h^4/(45 sigmaW²) and limiting information ratio 45/16. The actual n=21 illustrative comparison (5 endpoint-left + 11 center + 5 endpoint-right vs 21 distinct uniform nodes) has information improvement 2.33503012189. Expected one-sided Z=5 at 50% detection power in this **idealized model** requires per-bin intrinsic relative force precision sigmaF/F <= 2.3800097745e-8; uniform needs <= 1.5575159291e-8 (the higher permitted error means better efficiency).

If repeat measurements at exactly the same shell state have shared-noise correlation in the toy covariance Sigma_ij=sigmaW²[(1-rho)delta_ij+rho 1(x_i=x_j)], the information ratio is 0.86027 already at rho=0.25 and 0.32560 at rho=0.9. These numbers do not model real cosmic variance.

If an **unconstrained** nuisance shape equals the quadratic residual after removing the intercept and linear slope, the curvature coefficient is not identifiable at any sample count. An externally Gaussian-constrained shape of systematic std =0.1 times the physical projected signal lowers toy expected Z=5 to 4.472; std equal to the signal lowers Z to 0.981. Generic rank non-identifiability, not a new physics theorem.

Noisy shell coordinates require the first-order joint residual covariance SigmaWW+J SigmaUU J^T-SigmaWU J^T-J SigmaUW (J=diag W'(u)); second-order errors-in-variables biases remain. For the predeclared example, independent sigma_u=1e-8 lowers expected Z=5 to about 4.1113; sigma_u=1e-7 to 0.715. These are calibration sensitivity toy results, not instrument forecasts.

## Reproducibility and immutable parent

The delivered c22 manuscript is a seven-page English supplement, with four vector figures, independently separated references.bib, code and test results. Local c22 18 tests + original c21 22 tests = **40 PASS**; seeded 20,000 synthetic draws per each of six noise/design settings. Clean LaTeX+Biber compilation showed all seven rendered pages identical and identical extracted text, with no unresolved citations, overfull or underfull warnings and all fonts embedded.

The full c22 ZIP retains c21 FULL DELIVERY as an unchanged parent with SHA256 4c20e9cda04727e82205b6ebf3eb09d616678810f82a34fdf7e8d113e0dd0a9a. **Executable source and generated PDF live in ChatGPT conversation ZIP; this GitHub branch is a decision checkpoint only**. Do not claim it is an uploaded source repo or a production Actions run.

## Hard gates and claims prohibited

First obtain c18 pinned RIMS CLASS V18.29 baseline-versus-instrumented physical parity at all eight starts. Then really execute all predeclared 3x3x3x3=81 potential-family physical trajectories, retaining all normalization/stability failures and the Xi classifications. A full observable transfer from dark force to galaxy, lensing, redshift drift and joint covariance is required, plus nonlinear theory error and independently evolved second Einstein-Boltzmann implementation. Matched Planck 2018 + DESI DR2 BAO + Pantheon+ production MCMC gate is GetDist R-1 **strictly below 0.01** and minimum headline ESS **at least 1000**. No production posterior, observation, Bayes factor, LCDM competitiveness, globally first novelty or transformative discovery is claimed. No automatic new workflow or Actions dispatch.
