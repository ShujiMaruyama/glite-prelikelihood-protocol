# RIMS Phase II O3 c8p1 decision rule

Status: predeclared before c8p1 results are available. This rule is diagnostic only and never replaces the frozen production gate.

## Frozen production gate

A model is production-converged only if both conditions hold after the declared 30% burn-in:

- GetDist R-1 < 0.01;
- minimum headline physical-parameter ESS >= 1000.

No posterior, evidence, Bayes factor, model preference, or detection claim is promoted before the matched-model gate is satisfied.

## c8p1 transport question

c8p1 is a fresh four-chain candidate in the exact prior-preserving periodic q_H coordinate. It is not a continuation of c6/c7, and c6/c7 samples must not be pooled into c8 headline chains.

The principal diagnostic is whether the nonlinear shear materially reduces the Omega_scf bottleneck while keeping q_H itself well transported. The c7 reference bottleneck values are frozen as:

- Scalar worst relevant Omega_scf tau_int = 181.23947942455877;
- RIMS dominant chain-2 Omega_scf tau_int = 704.9745074680679.

## Decision hierarchy

1. If the frozen production gate passes, freeze c8p1 and stop sampler tuning for that model.

2. If the production gate fails, an unchanged c8p2 continuation is allowed only when the fresh c8 geometry shows material transport improvement:
   - Scalar: worst-chain Omega_scf tau_int <= 120 (at least about 1.5x speedup versus the c7 reference);
   - RIMS: worst-chain Omega_scf tau_int <= 352.5 (at least about 2x speedup versus the c7 reference);
   - worst-chain q_H tau_int <= 200;
   - max absolute half-chain drift <= 0.75 sigma for both q_H and Omega_scf;
   - no fatal sampler/theory error and four fresh chains are present.

3. Acceptance is a warning diagnostic, not a scientific gate. Acceptance below 0.10 or above 0.70 requires inspection before continuation but does not by itself determine posterior validity.

4. If the production gate fails and the transport conditions in item 2 fail, do not blindly resume c8. Diagnose the residual transformed geometry first. A second target-preserving shear (for example a residual rims_alpha_U coordinate) may be considered only from the already-frozen c8p1 diagnostic geometry and must itself be frozen and unit-tested before any new production candidate is launched.

5. If the transformed q_H coordinate mixes rapidly but a different physical parameter becomes the new dominant bottleneck, the next intervention must target that residual bottleneck rather than further tuning H0 transport.

This hierarchy is intentionally fixed before c8p1 results so that the continuation decision is not chosen after seeing the desired outcome.
