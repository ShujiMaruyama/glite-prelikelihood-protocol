# RIMS Phase II O3 c9 preconditioned fresh-production protocol

## Status

c8p1 is frozen as a transport diagnostic and is not a production posterior. The predeclared c8 continuation gate failed because half-chain drift exceeded 0.75 sigma and Scalar marginally exceeded the Omega_scf tau threshold.

## c9 intervention

The physical target is unchanged. The c8 periodic, measure-preserving H0 -> q_H map is retained exactly. Only the proposal metric and initialization references are changed. The proposal metric is frozen before c9 from c7 diagnostic chains transformed to c8 coordinates. To avoid importing chain-to-chain nonconvergence, only within-chain weighted covariance is averaged; between-chain offsets are excluded. A 15% diagonal shrinkage is applied.

The c7 artifacts are recovered by immutable run ID 34074123144 and verified against their internal SHA256 manifest. The proposal covariance is regenerated on the runner, and its SHA-256 must equal the predeclared digest before any c9 likelihood sampling can proceed.

A 15-minute four-chain geometry sentinel is run first with the frozen metric. Sentinel samples are destroyed and never enter the posterior. Production is allowed only when aggregate acceptance lies in [0.15, 0.60], all four chains write samples, and the covariance SPD audit passes. Production then starts from a newly empty output directory with four fresh chains for a bounded 90-minute segment.

## Frozen production gate

Headline promotion requires GetDist R-1 < 0.01 and minimum headline ESS >= 1000 for every matched model. Evidence, Bayes factors, detections, model preference, or competitiveness claims remain forbidden before that gate passes.
