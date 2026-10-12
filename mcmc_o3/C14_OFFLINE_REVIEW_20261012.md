# RIMS c14 — offline root-cause decision (2026-10-12)

This is a **read-only review**, not a new MCMC campaign or a production posterior. It replays the existing c13b run [38189596230](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/38189596230) and the c12 drag-ridge artifact from run [37874107719](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/37874107719).

## Newly established diagnostic facts

* For c13b proposal scale **4.0**, the mean weighted-chain χ² in the final quarter minus the first quarter was **−24.50, −28.78, −6.01, −42.82** (chains 1–4). All twelve c13b chains, across proposal scales 4.0, 4.8 and 5.7, showed a negative quarter difference.
* For scale **4.0**, final-quarter *chain mean* χ² values still span **about 42.29**; the leading between/within covariance eigenvalue is **about 189** under the independently replayed definition. The widest within-chain-standardized center separation is **A_planck ≈7.47 σ**.
* Covariance evidence is nuanced: the pooled narrowest eigenmode's leave-one-chain-out cosine is **≥0.978** at scale 4.0, yet individual-chain split-half correlation matrices differ by Frobenius norm **5.87–9.79**. Very short chains and repeated weighted states can make split covariance matrices nearly singular.
* The **27-step fast-dragging runtime marker was present in all three scales**. However, the c12 and c13b runs are not matched by initialization, duration, seed and slow-theory evaluation budget: there is **no defensible causal conclusion** about the value of increased dragging.
* Frozen parsed `params`, `theory` and `likelihood` sections agree across the compared YAMLs. The source ZIP and per-file SHA256 checks passed.

## Claim boundary and next gate

These are **retrospective descriptive diagnostics**, not a predeclared test, inference, or calibrated stationarity test. Apparent downward χ² trends are consistent with incomplete burn-in; no posterior, model selection, evidence, or ΛCDM competitiveness may be claimed. Do **not** train a new production covariance on these short chains.

An eventual *separately authorized* diagnostic should distinguish the overdispersed independent-start exploration challenge from a labelled local warm-start transport study, and explicitly match 3-step and 27-step arms on target, starting points, proposal geometry, proposal scale, time/slow-theory evaluation budget and recorded RNG scheme. Posterior transforms must preserve priors/support and Jacobians. There is **no automated follow-on**.

Production gates remain **GetDist R−1 <0.01** and **minimum headline ESS ≥1000**. No c14 workflow, Actions run or inference sample promotion was initiated by this audit.

JSON decision ledger: [C14_OFFLINE_ROOT_CAUSE_DECISION_20261012.json](./C14_OFFLINE_ROOT_CAUSE_DECISION_20261012.json).
