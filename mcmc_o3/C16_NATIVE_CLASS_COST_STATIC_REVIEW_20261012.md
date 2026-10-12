# RIMS c16 — precise CLASS compute-call instrumentation (static audit, 2026-10-12)

The c15 obstacle is **not only** the Cobaya cache. The actual RIMS subclass `RIMSShellClassy.set()` performs up to 16 normalization background `Class.compute()` attempts per cache miss, followed (if successful) by one full `Class.compute()` inside Cobaya's inherited `Classy.calculate()`. A single cache miss therefore does not equal one native CLASS call. Both types and durations must be recorded separately.

### Instrumentation design audit

A proposed `sys.setprofile(c_call)` probe was **rejected after testing**: an independent locally compiled Cython `cdef class Class / cpdef compute` did not emit these profile events. Instead c16 prototypes a small **Python subclass of the imported Cython `Class`**, whose overridden `compute()` delegates directly to `super().compute()` and records before/after timestamps, classification, success and failure. Cobaya's CLASS module loader is intercepted before it instantiates `Class`; the RIMS normalization scope is tagged `background`, normal Cobaya calculation scope `full`. No theory/kernel/likelihood/parameter definition is intentionally changed. However, compatibility and numerical equivalence with **actual pinned RIMS V18.29** have not been executed; the synthetic Cython surrogate does **not** satisfy that gate.

A fail-closed auditor rejects a missing native subclass installation event, a surrogate presented as real, incomplete per-rank JSONL, unpaired entries/exits, missing Cobaya pinned version or YAML digest, missing nonzero native background/full calls, unexpected calls outside these categories, or a mismatched resolved physical-target digest. The one-point preflight command can evaluate each frozen start without MCMC **only after separate authorization**.

### Completed and uncompleted work

**Local executed only:** c15 6 regression tests + c16 13 new synthetic tests = **19 PASS**; ZIP package SHA256 checks pass. Original c15 inputs and c13b `updated.yaml` copied with source integrity. c13b resolved-target reference digest (selected physical keys) = `518909ad2f1b31fd6882aebf0325d6604ae9626f353827d94aa916c5fa4368b9`.

**Still unexecuted:** real CLASS subclass compatibility/smoke, actual eight start points' RIMS-CLASS and likelihood finite checks, runtime resolved target identity and numerical equivalence against uninstrumented baseline, per-rank CLASS native call enumeration, overhead calibration, call-budget-matched 3/27 dragging test, production MCMC. No c16 Actions workflow or run was created.

Source-and-tests package is delivered as the accompanying conversation attachment `RIMS_c16_NATIVE_CLASS_COST_PREFLIGHT_20261012.zip` (SHA256 `d28233c2a3096a76a85b29f5878930d0ceef29e9d702c4bf8e924ad2790720a6`). **The GitHub branch records the frozen decision, not the full Python source package**.

No automatic follow-on; no promotion of any c10t–c16 samples to inference. Production hard gates remain **GetDist R−1 < 0.01** and **minimum headline ESS >= 1000**. No production posterior, Bayes factor, model preference or ΛCDM competitiveness claim.
