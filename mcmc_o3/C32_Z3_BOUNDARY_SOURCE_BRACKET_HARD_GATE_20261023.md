# RIMS c32 — native bracketing of the z=3 boundary, without false physical promotion

**Date:** 2026-10-23. **Status:** implementation committed; separate manual GitHub Actions static and single-case tests are NOT dispatched by this checkpoint. This is the same RIMS Phase II project, separate from IFC, PORG and Hawking studies.

## Source of truth and fixed negative decision

The archived, already executed physical CLASS native-run artifact is GitHub c30 Run #2 [39915717996](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39915717996), original GitHub artifact **12484613205**, SHA256 \`87d50a33bd0a1e8d5cddbe760dce458aadcd185fc9772607a2e636e353a32c74\`. **The original c30 status remains \`PHYSICAL_REJECT\`**, with exactly \`z_0to3_coverage_failed\`. Never rewrite that historical verdict to PHYSICAL_VALID.

The real patched CLASS solved three normalization backgrounds and the final physical background without exceptions, with a 40,000-row native z/phi history, 1,721 native z≤3 rows, \`rims_stab\` minimum **0.0038950198287496926**, original final z≤3 sample **2.9995860999538064**, next actual native z **3.0028107653487153**, source-derived initial occupancy **0.10000000000000003**. Only the upper boundary row inclusion rule failed. Crucially, the archived native history above z3 contains *z and phi only*, not m_eff²/H² at the first source point above 3, so **one cannot certify its stability from the old archive**.

## c32 new solution, forward-only

The new native runner \`c32_native_background_v7\` stores **the actual adjacent original source rows straddling z3** before filtering the CLASS table. Each row includes original native row index, z, phi, shell occupancy, native \`rims_stab\`, \`rims_meff2\`, \`H [1/Mpc]\` and the RIMS mass ratio. The canonical JSON of the pair is SHA256-locked to both the receipt and the native event log. The original full history z/phi SHA256 is separately verified, with no changed source columns.

The standalone \`c32_bracketed_endpoint_audit.py\` fails closed unless ALL of:
- Exact original 81-case freeze and source-case ID, native CLASS v7 receipt, native compute event pairing, original physical-audit record, and 80 preserved \`NO_RECEIPT\` cases.
- Original c24 conservative \`PHYSICAL_REJECT\` has **only** \`z_0to3_coverage_failed\` for a straddling endpoint, or the distinct \`PHYSICAL_VALID\` case with an exactly sampled native z3.
- c26 initial occupancy and independent c27 complete native z/phi provenance pass from independently reparsed raw source, NOT from a recap field alone.
- The bracket pair is the exact **adjacent** pair around z3 in the original full 40,000-row CLASS time series. Gaps of more than **Δz=0.01** are rejected; this is a declared diagnostic resolution tolerance, not a cosmic physical constraint.
- Both mass ratios are finite and satisfy \`rims_stab≈rims_meff2/H²\` (relative tolerance 5e−8, absolute 1e−10), \`H>0\`, \`m_eff²/H²≥−1e−10\`; original in-window stability, occupancy and normalization requirements are unchanged. A negative right-hand native mass or physical veto unrelated to native endpoint sampling blocks any promotion.
- The native bracket JSON is tied by SHA256 to a unique native-log event, with original row indices and source z, phi matching the independently preserved full history. Tampered/rehashed receipts or nonadjacent handpicked bracket rows fail.

Outputs distinguish:
- **\`NATIVE_GRID_BRACKETED_SAMPLED_PASS\`**: two native grid points genuinely straddle z3; an explicitly labeled *linear diagnostic* can be computed at z3.
- **\`NATIVE_Z3_EXACT_MESH_SAMPLED_PASS\`**: z3 itself exists as an exact original native CLASS sample; **not** called interpolated.
- Any provenance, initial occupancy, parameter lock, stability, normalization or grid resolution failure: **FAIL**, with no new physical pass label.

**Neither PASS means continuous-in-z non-tachyonicity, tensor/gradient safety, independently coded second Einstein–Boltzmann validation or observational model preference.** No z3 interpolation is described as a direct CLASS solve. The original c24 status is written and retained separately.

## Verification status and next actions

The c30 GitHub static suite **70/70 passed** on [Run 39915487540](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/39915487540). c32 adds 11 new **synthetic** source/row/tamper/negative-mass tests (and adjusts c30-version-assertion tests), making **81 intended static tests**, with **no verified c32 GitHub Actions PASS yet**. The c32 workflow \`.github/workflows/rims-phaseii-c32-native-bracket-smoke.yml\` is registered on \`main\` and this branch, byte-identically; it is \`workflow_dispatch\` **only**, \`run_mode=static-only\` **default**, optional \`single-case\` exclusively \`rims_000\`, without cron, 81-case physical batch, MCMC or automatic next stage.

**Research progression:** first inspect c32 static result, then explicitly authorize exactly one real c32 physical background computation. Only if independent native history and bracketing pass may this pilot enter the broader reachability design. c18 full eight-start independent numerical matched parity, actual 81 physical backgrounds with all failures preserved, cross-channel observables/nonlinear theory covariance and independent second solver remain unexecuted production gates.

The c30 weak-shell pilot already indicates a very small intrinsic force-root curvature; no detection, successful ΛCDM comparison, Bayes factor, world-first priority or competitive observational posterior is claimed. GetDist production gate unchanged: R−1 <0.01 and minimum headline ESS >=1000.
