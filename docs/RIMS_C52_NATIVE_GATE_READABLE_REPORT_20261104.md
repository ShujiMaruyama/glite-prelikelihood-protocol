# RIMS C52 — Accepted-State Physical Stability Gates (4 November 2026)

**Author:** Shuji Maruyama, ORCID 0009-0007-5034-7634  
Independent Researcher, Muroran, Hokkaido, Japan  
© 2026 Shuji Maruyama. All rights reserved.

This is the **readable fallback on GitHub** for users whose ChatGPT PDF/ZIP downloads fail. C52 deliberately moves beyond an endless series of synthetic tests: it registers code and a manual workflow capable of compiling pinned CLASS with a strict full-state physical observer and, with separate user authorization, probing the original `rims_002` case once. The workflow has **NOT YET RUN**. Registration is not proof of successful compilation.

## Grounded native result (C44 only)

| Observation | Real C44 value |
|---|---:|
| Frozen native `Class.compute()` attempts | 1 |
| NDF15 Newton trial evaluations | 845 |
| NDF15 ACCEPT_GATE / COMMIT pairs | 618 / 618 |
| Last committed `a` | `3.891990717634451e-10` |
| Next rejected Newton-trial `a` | `3.945904558535526e-10` |
| Trial-only `m_eff²/H²` | `-1.0049389722010728e-10` |
| Original physical cutoff | `-1e-10` |
| Accepted-state `m_eff²/H²` | **NOT MEASURED** |

Original native artifact SHA-256:
`cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`. No prior RIMS result or parameter was modified.

## New hard finding: source-veto censoring

Let `g=(m_eff²/H²)+1e-10` and assume original source rejects a derivative evaluation when `g<0`. Recording physical `g` only after that derivative routine **succeeds** mechanically selects `g>=0`. Hence:

**Success-selected accepted `g>=0` is NOT independent proof that unrestricted RIMS evolution is physically stable.**

This is a conditional inference/selection theorem, **not a new fundamental physical law**. The exact-state bitwise join verifies source provenance of a measured accepted state; it does not remove the selection bias. The full coupled, gauge-invariant scalar/matter/metric perturbation operator still needs independent stability checks.

## Actual implemented C52 workflow

- `mcmc_o3/c52_instrument.py`: Source-locked, insertion-only C43 NDF15 phase, C45 full COMMIT and C50 full derivative terminal-success loggers; original C39 veto retained.
- `mcmc_o3/c52_native_audit.py`: Strict hexadecimal binary64 full-`(loga,y)` per-step join; independently recomputes original mass relation; rejects source/binary/input/trace drift and physically inconsistent accepted negative `g`. No interpolation, retuning or shadow evaluation.
- `mcmc_o3/test_c52_static.py`: additional fail-closed tests. Registered, **GitHub CI unexecuted**.
- `.github/workflows/rims-phaseii-c52-accepted-g-native.yml`: Registered on both this branch and `main`; **manual workflow_dispatch only**. Default `static-only` compiles actual pinned RIMS/CLASS with overlays but calls **zero CLASS computes**. Separate `native-one` mode can perform **one frozen original `rims_002`** compute, after static preflight; it preserves failures as artifacts and makes no automatic retries. No paid services are required under ordinary public GitHub Actions availability.

Original underlying source:
- CLASS upstream commit `e85808324f51fc694d12e3ed7439552a3c3f9540`
- Original C39 `source/background.c` SHA256 `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`
- Original NDF15 git blob SHA1 `0d293723510171ae9a732c80da32adb9ee52701f`
- Original `rims_002` input digest `ed66e920d52e9f7f63c0778c3d1681e732007c99afd5b4ac816160056909f340`

## Local reproducibility evidence

The *separate local* C50 archive was extracted and its 201 tests rerun successfully. C51 conditional toy: 17 tests passed. A local independent C52 implementation adds 14 verified regression tests, **232 total PASS**. Local C52 and GitHub C52 implementations are different code artifacts; the GitHub version still requires its own CI test and native source compilation before its behavior can be promoted. No CLASS C52 run has been claimed.

## Source-specific analytical relations (not unique observations)

The logistic RIMS dark-matter mass model has
```
s(phi) = 1 / (1 + exp(-2*alpha_U*(phi - phi_t)))
beta = alpha_U*(1-s)
kappa = m''/m = 3*beta**2 - 2*alpha_U*beta
g = Vpp/H**2 + 3*rho_idm*kappa/H**2 + 1e-10
N_ij = beta_j*(3*beta_i**2-kappa_i) - beta_i*(3*beta_j**2-kappa_j)
```
Only an independently reconstructed, physically calibrated multi-epoch `beta,kappa` with full covariance and native coupled perturbation evolution can make this a falsifiable observational test. Other interacting-DE models can share parts of the relation. Prior art includes Amendola, Phys. Rev. D 62, 043511 (2000), and Aoki et al., Phys. Rev. D 113, 044053 (2026).

## Run instructions (one operation at a time)

1. Open [the C52 GitHub Actions page](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c52-accepted-g-native.yml).
2. Click **Run workflow**. Branch: `rims-c52-accepted-physical-g-native-gate-20261104`. `run_mode: static-only`.
3. Once the static run has completed, review **source/binary receipt, test log and compile failures**, not just the green check.
4. **Do not select `native-one` until preflight success has been independently audited.** It is opt-in, at most one frozen case; code preserves failure with original physical veto unchanged.

## Claim ledger

Not established: C52 production execution, C52 accepted-state g, an accepted physical root bracket, physical stability, a normalized viable background, independent Boltzmann-code parity, full production likelihood, MCMC, Bayesian evidence, detected gravity modification or model superiority.

This repository entry is intentionally readable directly in a browser if PDF/ZIP delivery from ChatGPT fails.
