# RIMS Phase II c17 — eight-start native CLASS parity gate

**Date:** 2026-10-15  
**Stage:** static implementation and synthetic/mock verification only. **No real CLASS evaluation, no MCMC, no GitHub Actions dispatch.**

c16 established an attempted native `classy.Class.compute()` call counter for the extra RIMS background-normalization iterations and the final CLASS calculation. c17 extends this to a **baseline-versus-instrumented numerical identity test** at all eight frozen c15 start positions, with no selection of favorable starts.

The delivered ZIP `RIMS_c17_Native_CLASS_Parity_Static_Preflight_20261015.zip` has SHA-256:

`902f00cf70e9d75f4da9b1d6479b8d0cb31dea05ee269172766f524cdf9c4c2c`

Its complete editable Python source includes `c17_one_point_probe.py`, `c17_pair_audit.py`, `c17_batch_audit.py`, `test_c17_parity.py`, inherited c16 source, C15 input baseline, manifests, and a Japanese README. The **ZIP is supplied as a conversation artifact**, not imported into this GitHub branch. Do not assume these Python files exist on the branch.

## Frozen runtime checks

- Separate clean-process control and subclass-instrumented runs at *the same fixed sampled vector*.
- Cobaya v3.6.2, patched RIMS CLASS V18.29, full matched Planck 2018/DESI DR2/Pantheon+ likelihood.
- Strict physical-target hash equality with frozen c13b, unchanged priors and scalar theory.
- Compare 5 individual log-likelihoods, logpriors, logposterior, normalization phi_ref and initial parameter coordinates; numerical tolerances `atol=1e-7`, `rtol=1e-9`.
- Fail on missing/unpaired/incorrect native CLASS background or full calls, incorrect runtime target, or invalid starts.
- All eight distinct start points are mandatory: any one missing or failing causes final FAIL.

**Local tests:** c15 (6) + c16 (13) + c17 (14) = **33 PASS**. These are not physical CLASS demonstrations. There is no selected posterior or validation of model competitiveness.

**Next hard gate:** explicitly authorized, *non-MCMC* real CLASS/cosmology one-point parity; all eight physical starts must be evaluated without cherry-picking. A later matched-budget 3-step versus 27-step MCMC experiment remains a separate authorization.

**Fixed production gates:** GetDist `R-1 <0.01` and minimum headline ESS `>=1000`. No production posterior, evidence/Bayes factor, model preference, or ΛCDM competitiveness claim. No automatic long run or follow-on.

Machine-readable checkpoint: [C17_NATIVE_CLASS_PARITY_STATIC_CHECKPOINT_20261015.json](./C17_NATIVE_CLASS_PARITY_STATIC_CHECKPOINT_20261015.json).
