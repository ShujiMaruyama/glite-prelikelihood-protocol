# C44 native phase-trace execution gate (pre-execution)

Base branch: rims-c43-ndf15-accepted-commit-trace-20261029.
Locked frozen case: rims_002; original CLASS upstream e85808324f51fc694d12e3ed7439552a3c3f9540.
Use original stability veto 1e-10 and original background integration tolerance 1e-10; no new physical parameters, retuning, MCMC, or automatic retries.

1. Reconstruct immutable CLASS RIMS patches and check SHA256.
2. Verify C39 source-only decomposition overlay retains original stability veto.
3. Verify C43 opt-in NDF15 source overlay and its exact upstream blob identity.
4. Run static compilation and C43 regression tests before any native execution.
5. Permit exactly one manually triggered native compute, preserving the full stderr, traceback, compiled binary hash, freeze hash, and source receipts.
6. Audit BEGIN/TRIAL/ACCEPT_GATE/COMMIT around the native veto. Fail closed if C39 or C43 telemetry is missing, inconsistent, or truncated.
7. Never interpret an uncommitted Newton trial as an accepted physical solution; a background viability or normalized solution claim requires independent physical checks.

Status: plan and locked constraints only. C44 native CLASS compute has NOT been executed or certified.
