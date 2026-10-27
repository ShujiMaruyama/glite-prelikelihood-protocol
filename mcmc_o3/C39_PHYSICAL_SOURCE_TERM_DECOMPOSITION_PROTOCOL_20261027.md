# RIMS c39 — source-term decomposition specification (27 October 2026)

This is a **diagnostic design**, not another CLASS computation. The historical c35 failure and the independent c37 reproduction remain immutable.

## Source-grounded identity

The unchanged physical code computes

```
m_eff²/H² = [V_{,phi phi} + 3 rho_idm (m_{,phi phi}/m)] / H²
```

and vetoes a background when this is smaller than minus the fixed tolerance 1e-10. This was triggered in the original frozen `rims_002`, at reported a=3.945905e-10 with m_eff²/H² approximately -1.004939e-10. The reported margin exceeded the veto tolerance by approximately 4.939e-13 (0.4939% of tolerance). These printed figures have finite output precision.

## Strict forward diagnostic requirements

1. Capture, at the **same original failing CLASS step**, raw IEEE double-precision values for scale factor, phi, occupancy s(phi), H, density rho_idm, scalar potential curvature Vpp, source mass curvature (m''/m), and the two separately normalized contributions to m_eff²/H².
2. Reconstruct the total from those two contributions, compare with the native computed margin, check all fields finite and positive H, and record cancellation ratio `(|T_V|+|T_idm|)/max(|T_V+T_idm|, tiny)` without assuming it is small. Preserve exact original units and normalization.
3. Do not change the CLASS guard condition, `rims_stability_tolerance=1e-10`, `rims_enforce_stability=yes`, frozen model parameters, potential, initial occupancy, original CLASS commit, or reference source SHA. Distinguish the hash of any diagnostic-only code modification and archive its exact diff. A log-only change still requires a new code provenance.
4. Require tests checking both positive- and negative-term cancellation, values near the threshold, non-finite fields, no model parameter changes, and *unchanged* physical-rejection behavior.
5. After source instrumentation has passed static tests, any execution must be **separately manually authorized**, bounded to a single first-normalization attempt for `rims_002` with all error logs retained. Do not launch a full background/MCMC or rerun other cases.
6. A precision study, if later undertaken, must be preregistered and report **all results**; adjusting the physical stability tolerance merely to obtain a successful numerical solve is not valid evidence for a physically stable branch.

## Scientific decision matrix

- A reproducibly negative physical contribution with converged sign suggests a genuine instability of this branch; this would not establish global RIMS failure.
- A strong cancellation with precision-sensitive sign calls for stricter numerical convergence and independent implementation tests.
- A wrong relative factor/unit or inconsistent background expansion is an implementation defect and requires an independently verified correction, not post-hoc rescue.
- A valid raw-source ratio and converged negative sign still require the integrated growth history and perturbative stability analyses before any physical exclusion.

## Frozen evidence / claim boundary

c37 successful diagnostic: GitHub Run 40277614362; original source artifact ID 12630937571. Strict old c35 frozen case status: SOLVER_FAILED. Unique physically attempted inputs 3/81; normal native backgrounds 2; failure 1; 78 never attempted. No c39 physical compute, no matched cosmological likelihood, no posterior, no Bayes factor, no claim of model superiority, and no second-code confirmation.

This note deliberately does not reclassify a historical failure as numerical noise or a physical no-go. The conditional next step is a source-preserving, diagnostic-only implementation and separately inspected tests.
