# RIMS C55 — actual source-index repair and native-run boundary (5 November 2026)

Shuji Maruyama | Independent Researcher, Muroran, Hokkaido, Japan | ORCID 0009-0007-5034-7634
© 2026 Shuji Maruyama. All rights reserved.

## What was wrong; what has been repaired

The prior C54 accepted-state algebraic reconstruction used scalar phase-space indices **(phi,phi_prime)=(0,1)** despite original CLASS integration vector beginning with conformal time tau. Original CLASS commit e85808324f51fc694d12e3ed7439552a3c3f9540: background_indices() assigns index_bi_tau=0, then optional DCDM/DR/FLD, then scalar components. In frozen rims_002 these three optional components are absent, so **tau=0, phi=1, phi_prime=2 and vector length 7**. The original C54 parser would reject a legitimate native log.

C55 corrects those source indices and adds:
- mcmc_o3/c55_accepted_g_reconstruct.py: conditional post-COMMIT physical mass *algebraic reconstruction*, with exact binary64 source-vector provenance; NO native CLASS calls.
- mcmc_o3/c55_runtime_aux_overlay.py: original pinned-source additive-only observer for the runtime shooting SCF lambda, scalar quantities and true field indices, logged only after successful original derivative calculation.
- mcmc_o3/test_c55_native_layout.py: explicit frozen-index adversarial tests.
- .github/workflows/rims-phaseii-c55-accepted-source-state.yml: manual-only, default static-only compile, separate native-one opt-in, with C55 conditional reconstruction preserved even if C52 strict exact join fails closed.

Original background source SHA256 remains 08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027 (post-C39), NDF15 upstream git blob SHA1 0d293723510171ae9a732c80da32adb9ee52701f. Original threshold and parameters unchanged.

## Actually executed independent verification (software only)

- Complete separately packaged C55 implementation/tests: **31/31 PASS**; includes 500 deterministic synthetic Friedmann comparisons; old-C54-fails/new-C55-works; malformed/duplicated input, wrong scalar index, lambda, potential, density and mass decomposition checks.
- Untouched C54 original: **34/34 PASS**.
- These software tests do not prove physical stability. The GitHub copy was registered, but its own Actions execution is not yet confirmed; local and GitHub files are distinct provenance artifacts.
- Original C44 native stderr SHA256: **9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d**.
- Original C44 native run has 618 accepted COMMIT coordinates, 845 trial evaluations, but **no accepted full state vectors**; rejected Newton trial mass ratio -1.0049389722010728e-10. C55 read-only audit of this real SHA-verified log gives **NO_ACCEPTED_STATE_VECTORS**, therefore accepted-state physical g count remains **zero**, not inferred.

## Model-specific method and explicit limitations

The conditional formula is:

g_c = [lambda_runtime² exp(-lambda_runtime phi_c) + 3 rho_idm,c alpha_U² (1-s_c)(1-3s_c)]/H_c² + 1e-10

rho_idm,c = rho_idm,e sqrt(s_c/s_e), with H_c² rebuilt from the exact CLASS scalar energy-density difference.

The runtime shooting coefficient cannot be equated to the original input 5: the CLASS source shooting initial guess sqrt(3/Omega_scf) matches the real C44 failed trial potential second derivative at phi=4.44 to the printed precision. This is a source-consistency observation, NOT a direct native runtime observation on accepted states.

Even native accepted g greater than or equal to zero is selected by the original stability veto and is not by itself physical stability proof. Independent direct accepted-state evaluation or certified numerical enclosure, unmodified source/binary trajectory parity and the fully coupled gauge-invariant stability matrix are necessary.

## What still prevents physics promotion

Local shell has no native classy binary, and git clone cannot resolve github.com. This conversation's GitHub connector supports source registration, but no workflow-dispatch operation is available. Therefore **no new pinned native CLASS compilation or compute has been performed**.

The next non-redundant action is one manual **static-only** pinned CLASS compile on:
https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c55-accepted-source-state.yml
Branch: rims-c55-native-vector-index-repair-20261105. Do not select native-one until the actual static source/binary receipt and logs are reviewed. This does not rerun historical C44.

## RIMS science baseline preserved

The authoritative integrated/transformative RIMS manuscript retains seven native perturbation modes (AD/CDI/BI/NID/NIV/RIE/RMI), all-k conservation checks, effective mass reconstruction and explicit hard gates. Future required science includes 81 full background family/charge/Omega/shell scan, converged matched Planck 2018 + DESI DR2 + Pantheon+ inference (GetDist R-1<0.01 and minimum ESS>=1000), nonlinear error/covariance, independent Einstein-Boltzmann code and a concrete radiative protection branch. None is certified by C55.

C55 is a source/implementation supplement, **not** a replacement or thinning of the full RIMS master. No detection, physical viability, normalized solution, posterior, Bayes factor or LambdaCDM superiority is claimed.

Browser-readable fallback for previously failing ChatGPT ZIP/PDF downloads.

## Final immutable local C55 package (verified)

- Filename: RIMS_C55_Source_Index_Repair_20261105.zip
- SHA-256: **3b06fd1653f555229aad3542defc27a81864426bcd8f3c61a01f63330f28f7ea**
- Bytes: **8,229,365**; contains the intact C54 parent archive, original C44 native telemetry, standalone C55 corrected source, unmodified C54 old source for adversarial old-versus-new tests, README, source/hash ledger and the runnable reproduction script.
- Independently re-extracted from final ZIP: **31/31 tests PASS**, C54/C44 immutable ZIP SHA digests PASS, original C44 stderr digest PASS, ZIP CRC and member SHA-256 manifests PASS.
- GitHub file IDs and code are separately versioned; passing local tests does not establish GitHub CI acceptance.
