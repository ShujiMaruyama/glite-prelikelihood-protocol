# RIMS c31 — first complete physical CLASS background, bracketed redshift endpoint (2026-10-23)

**Read-only forensic audit of the REAL c30 run; not an additional CLASS simulation and not a release of a physical-model viability claim.** Source of truth: [GitHub Actions Run #2, ID 39915717996](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39915717996), original artifact ID **12484613205**, downloaded unmodified ZIP SHA256 **87d50a33bd0a1e8d5cddbe760dce458aadcd185fc9772607a2e636e353a32c74**.

- Frozen 81-design hash \`0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0\`; case \`rims_000\` SHA256 \`e95f274bbafd51e117c9286480da1be42278c1e4def4aae447c1968dc0471e61\`.
- Pinned original CLASS and patched compiled implementation succeeded, all 4 real native \`Class.compute()\` calls completed, native runner \`run_status=solver_completed\`. Three mass normalization solves plus full final background; normalized \`mratio-1=2.346995930935236e-10\`.
- Native source history has 40,000 preserved redshift+scalar samples; original c27 history file hash matches receipt and original archive manifest hash checks passed. Earliest input occupancy recomputed from the source is \`0.10000000000000003\` (target 0.1; c26 initial-fidelity gate independently recoverable).
- 1,721 native redshift samples within 0≤z≤3 cover [0, **2.9995860999538064**]; sampled stability ratio \(m_\mathrm{eff}^2/H^2\) ranges **0.0038950198287496926..0.08126402539365145**, all positive and finite. Sampled shell occupancy ranges **0.09982144604791479..0.09984461232053336**.
- The original c30 independent auditor returned **PHYSICAL_REJECT**, with exactly one reason: \`z_0to3_coverage_failed\`. The criterion \`max(z_native_inside) ≥ 3 - 10^-6\` is inappropriately tied to native grid placement. Direct inspection of the original complete redshift history locates native points **2.9995860999538064** and **3.0028107653487153**, properly bracketing z=3 with spacing 0.0032246653949088433.
- As a *diagnostic only*, interpolate the saved **scalar phi** between these native points: \`s(z=3)≈0.09984461475979732\`. **Neither an exact native z=3 CLASS solve nor m_eff²/H² at z=3 is independently recorded in this archive**; no such value was invented.
- The shell's tiny span yields a c21–c22 idealized intrinsic-force curvature sagitta \(3.359836126067812\times 10^{-12}\); idealized independent three-node 5σ 50%-power relative \(F\) noise ceiling \(\approx1.2190159369663574\times10^{-10}\). This is a strictly **idealized design diagnostic**, not an actual DESI/Euclid capability forecast, fifth-force detection or model-vs-model separation.
- **Keep original status immutable:** \`PHYSICAL_REJECT=1, NO_RECEIPT=80\`. The observed data positively validates native solver completion, input occupancy source identity and sampled-grid non-tachyonicity; it does **not** fulfill the strict interval-endpoint criterion, continuum/tensor/gradient stability, separate solver or cosmological likelihood.

## Reproducible read-only follow-up

A ChatGPT-delivered archived \`RIMS_C31_REAL_CLASS_READONLY_FORENSIC_20261023.zip\` SHA256 **57d55a586764be6a9b45a3c19ee0427f97a356559d095876ec37041359c134f3** includes:
1. The **byte-unmodified original GitHub c30 artifact ZIP**, SHA256 above.
2. Independent Python \`c31_read_only_audit.py\`, its JSON output, five archive-integrity/frozen-source mutation tests, and \`README.md\`.
3. Six-file outer SHA256 manifest checked. **Five new local tests PASS; not run on GitHub Actions.**

This branch is a research/evidence checkpoint. **Executable c31 forensic source is in the ZIP, not committed to GitHub**.

## Physics-first next step

Fix the endpoint criterion **without silently relabeling interpolation as a native CLASS sample**, e.g. use bracketed native points and a resolution gate and report \`GRID_BRACKETED_INTERPOLATED\` distinctly, or directly request the CLASS background interpolation at exactly z=3 with traceable source. Then independently run and preserve c26/c27 audits even if a disjoint physical gate fails. Do not rerun c30 unmodified; new code and a static preflight must precede a separately authorized one-case physical execution. No full 81 run, MCMC, evidence or automatic workflow dispatch has been initiated.

The longstanding Phase-II gates remain: 81 actual potential/universality trajectories with all failures retained; independent matched CLASS parity; nonlinear \(C_{NL}\)/\(k_\max\), full survey covariance; a second Einstein–Boltzmann code; matched Planck2018 + DESI DR2 BAO + Pantheon+ posterior convergence GetDist R−1 <0.01 and minimum headline ESS≥1000; no ΛCDM preference or Bayes-factor claim without real inference evidence.
