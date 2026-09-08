# RIMS Phase II O3 c9 preconditioned fresh-production protocol

## Status

c8p1 is frozen as a transport diagnostic and is not a production posterior. The predeclared c8 continuation gate failed because half-chain drift exceeded 0.75 sigma and Scalar marginally exceeded the `Omega_scf` autocorrelation threshold.

The first c9 execution attempt (run `34095616513`) stopped **before the disposable sentinel and before production**. Both Scalar and RIMS c7 artifacts passed their internal SHA-256 manifests exactly. The stop was caused solely by a raw-byte SHA assertion on a regenerated floating-point covariance text file. No c9 posterior samples were generated. The correction is recorded in `C9_REPRODUCIBILITY_GATE_AMENDMENT_20260907.json` and changes only the software reproducibility guard, not the statistical target or the c9 intervention.

## c9 intervention

The physical target is unchanged. The c8 periodic, measure-preserving `H0 -> q_H` map is retained exactly. Only the proposal metric and initialization references are changed. The proposal metric is frozen before c9 from c7 diagnostic chains transformed to c8 coordinates. To avoid importing chain-to-chain nonconvergence, only within-chain weighted covariance is averaged; between-chain offsets are excluded. A 15% diagonal shrinkage is applied. The c7 posterior samples are **not** reused as c9 posterior samples.

## Fail-fast geometry audit

Geometry reconstruction is performed in a dedicated job **before** CLASS compilation and likelihood installation. The c7 artifacts are recovered from immutable run ID `34074123144` and must pass their own `SHA256SUMS.txt` exactly.

The regenerated proposal covariance is then checked semantically rather than by brittle raw floating-point file bytes. The frozen numerical contract requires:

- exact sampled-parameter order;
- finite matrix entries and strictly positive diagonal;
- symmetric covariance;
- minimum correlation-matrix eigenvalue at least `0.10`;
- correlation condition number at most `25`;
- an 8-decimal scientific-notation canonical fingerprint equal to the predeclared model-specific digest in the amendment;
- runtime/version metadata recorded in the geometry artifact.

The raw covariance SHA-256 is still recorded for provenance, but it is not a pass/fail criterion. The generated geometry artifact contains the covariance, c9 YAML, metadata, and c7 source-manifest provenance, but **not the c7 chain samples**.

## Disposable sentinel

A 15-minute four-chain geometry sentinel is run first with the frozen metric. Sentinel samples are destroyed and never enter the production posterior. Production is allowed only if:

- all four chains write at least 10 rows;
- aggregate acceptance lies in `[0.15, 0.60]`;
- each chain acceptance lies in `[0.10, 0.70]`;
- the geometry artifact and c8-to-c9 target-equivalence audits pass.

After the sentinel, its sample directory is deleted and absence is asserted. Production then starts from a newly empty output directory with four fresh chains for a bounded 90-minute segment.

## Frozen production gate

Headline promotion still requires

`GetDist R-1 < 0.01` and `minimum headline ESS >= 1000`

for every matched model. Evidence, Bayes factors, detections, model preference, or competitiveness claims remain forbidden before that gate passes.
