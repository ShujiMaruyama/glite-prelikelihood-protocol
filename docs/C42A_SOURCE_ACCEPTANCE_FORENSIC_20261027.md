# RIMS C42-A — Accepted-step versus trial-veto source forensics

**Shuji Maruyama**, Independent Researcher, Muroran, Hokkaido, Japan  
ORCID: 0009-0007-5034-7634  
27 October 2026  
© 2026 Shuji Maruyama. All rights reserved.

## Scope, evidence, and headline finding

This **source-only** C42-A successor preserves the C40/C41 native failure chain. The pinned repository is `lesgourg/class_public` commit `e85808324f51fc694d12e3ed7439552a3c3f9540`, patched with unchanged RIMS V18.23 and V18.29 diffs, plus C39 source-only stderr instrumentation. The source and commit were retrieved via GitHub. The C41 experiments `tight10-one` (run #3) and `tight100-one` (run #4) each returned `SHOOTING_FAILED_WITH_VETO`, not a normalized background solution. Both were originally **archival successes**, not scientific successes.

**Source-localized finding:** at upstream `tools/evolver_ndf15.c` line 382, `(*derivs)(tnew,ynew+1,...)` runs *before* the successful-step branch (`stepstat[0] += 1` near line 539). The RIMS source stability veto occurs in `background_functions`, called from `background_derivs`. Consequently, the C39 native veto print is **not evidence of an accepted state**. The rejection occurs within a derivative trial evaluation and can stop the solver before acceptance.

The upstream `background_solve` instead calls `background_initial_conditions()` and obtains `loga_ini`, sets an output grid of `background_Nloga=40000` points from `loga_ini` to zero, then calls `evolver_ndf15`. The upstream `background_sources` callback obtains its values using `background_functions` and is called from `evolver_ndf15` *after* its successful-step count increases; its output can be interpolated from the accepted integration step. The diagnostic therefore distinguishes **initialization success**, **integrator accepted steps**, and **successful output-grid callbacks**, and never conflates a candidate derivative with a completed step.

## Important correction to prior C42 feasibility note

The pinned upstream `include/precisions.h` defines `a_ini_over_a_today_default = 1.e-14` (line 11), not approximately `4e-10`. The initial conditions routine starts with this default, but potentially modifies `a` when necessary (e.g. species-specific criteria). Therefore the earlier phrase *“these early vetoes occur very close to the apparent initial background epoch”* was **not established**. The native `a_ini` must be recorded before deciding whether the pre-veto accepted interval is empty. The C41 first-veto epochs around `3.95e-10` do not by themselves establish the first accepted step or the absence of common output times.

## C42-A instrumented-source contract — source-only preparation

The `c42a_source_probe.py` program accepts only two exact source identities:

- C39 overlay `source/background.c`: SHA-256 `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`.
- Untouched upstream `tools/evolver_ndf15.c`: Git blob SHA-1 `0d293723510171ae9a732c80da32adb9ee52701f`.

It inserts diagnostics without changing the numerical equations, the original veto, the parameters, or the control-flow branches. It verifies byte-identical reversibility by deleting *exactly* the inserted text from prepared sources. Source modifications *can still affect floating-point runtime indirectly* (logging/timing), so trajectory invariance is not claimed. Prepared source files are **not compiled or run** by this preflight.

Marker taxonomy:

| Marker | Meaning | Does **not** establish |
|---|---|---|
| `RIMS_C42A_INIT_ENTER_V1` | RIMS background initialization called | Initial conditions succeeded |
| `RIMS_C42A_INIT_OK_V1` | Background initial conditions returned; actual `a_ini` printed | Converged background |
| `RIMS_C42A_NDF_ENTER_V1` | Generic NDF evolver called; its initial time printed | Successful step / RIMS-only invocation |
| `RIMS_C42A_NDF_STEP_OK_V1` | Generic NDF step passed its local error gate (first 64 per call) | Returned final background / full history |
| `RIMS_C42A_OUTPUT_OK_V1` | Successful post-step output callback with physical fields (first 16 grid indices) | That grid point equals an NDF step endpoint |
| `RIMS_C39_TERMS_V1` | Vetoed source evaluation retained as originally instrumented | Accepted-step state |

Both instrumentation files must be associated by chronological and shooting-attempt context before scientific interpretation. The generic NDF markers alone do not identify which CLASS subsystem they represent. If an event sequence is ambiguous, classify `AMBIGUOUS_CONTEXT` instead of claiming common epochs. Candidate stable overlap should be defined through common, **source-confirmed output-grid callback** epochs for frozen inputs, not through `a_veto` cross-run interpolation.

## Executed and unexecuted boundary

Executed: pinned upstream/hunk source forensics; C40/C41 receipt review; C42-A overlay authoring; ten local *synthetic-source* insertion and negative tests; archive integrity packaging. NOT executed: preflight against live reconstructed full upstream in GitHub Actions; C42-A modified CLASS native build or native run; actual `a_ini` logging; accepted-step or post-step native samples; same-a convergence; branch viability; likelihood/MCMC; observational preference.

The registered C42-A **GitHub source-only workflow** may later execute: reconstruct original patched sources, apply the already-audited C39 stderr overlay, run ten local tests and the exact source-only C42-A overlay preparation, upload the audit/modified source as an artifact. It does not call CLASS `compute()` or start fitting. Further native computation would require an independently preregistered follow-up mode and manual authorization.

## Scientific go/no-go plan

1. Source-only preflight passes exact two-file lineage, unique anchor and reversal checks. Failure stops without CLASS compute.
2. Only in a separately declared native execution: record `a_ini` and source-timestamped NDF accepted steps and output callbacks. If no output callbacks occur before the veto, declare the common-a data gate blocked; a lack of first-16 callback markers is **not proof** of zero accepted steps, because markers are capped.
3. Reject trial-only points as convergence nodes. Check identical, predetermined output-grid nodes in C40/C41 family, accounting for possibly different `a_ini` and internal shooting calls.
4. Require source-level arithmetic closure, error bar/bound, full step-grid provenance and enough common-a observations before convergence claims. Never disable the original RIMS veto, retune `rims_002`, run 81 cases, or convert archival exit code 0 into physical viability.

## Reproducibility and fixed ancestor

The package preserves original C42 read-only ZIP, C41 source provenance, code, unit tests, a JSON continuity ledger, and per-file SHA-256. The new C42-A source code is a prospective source-only diagnostic artifact. Previous C42 status remains accurate; no outputs were overwritten.
