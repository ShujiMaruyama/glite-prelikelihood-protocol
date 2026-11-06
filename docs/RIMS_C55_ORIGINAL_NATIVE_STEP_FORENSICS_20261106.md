# RIMS C55: newly extracted **real native** terminal-step behavior (6 November 2026)

Author: Shuji Maruyama · Independent Researcher, Muroran, Hokkaido, Japan · ORCID 0009-0007-5034-7634  
© 2026 Shuji Maruyama. All rights reserved.

## Why this is different from 31 synthetic C55 tests

This is a new quantitative analysis of the *original actually executed* C44 Run #2, not another generated toy. We read its full **2,083-line** raw GitHub Actions native stderr; SHA-256:
`9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d`.
Original native artifact ZIP SHA-256:
`cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`.

Source [C44 GitHub Actions Run #2](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/41000757103), previously completed with a *captured original shooting failure*, not a completed normalized RIMS universe.

### Verified phase and adaptive-step results

| Measured quantity | Value |
|---|---:|
| NDF15 BEGIN markers | 1 |
| Newton TRIAL records | 845 |
| ACCEPT_GATE records | 618 |
| COMMIT records | 618 |
| Original C39 physical-veto events | 1 |
| Last accepted log scale factor `x=ln a` | -21.666930150605552 |
| Rejected Newton trial `x` | -21.653172709521662 |
| **Last 100 accepted log-step spacings** | **all 0.013757441083889432**, at recorded binary64 subtraction precision |
| Last 100 accepted step order | 5, all |
| Last 100 trial records per accepted step | 2, all |
| **Additional NDF failed-step-counter increments in last 100 accepted steps** | **0** |
| Last increase in NDF failed-step counter | by COMMIT #464 |
| Accepted COMMITs after last failed-counter increase | 154 |
| Terminal *uncommitted* proposal `delta(ln a)` | 0.013757441083889432, **equal to the preceding accepted spacing** |
| Terminal Newton iteration | 1 |
| Terminal uncommitted `a` | 3.9459045585355262e-10 |
| Full accepted state vectors | 0: not logged in original C44 |
| Direct accepted-state physical g measurements | **0** |

**New grounded conclusion:** the original C44 run did not display adaptive step-spacing collapse before the terminal stability rejection. Its last 100 recorded accepted step spacings are identical, order 5 continues, no NDF failed-step counter is added, and the attempted terminal interval is the same size. The terminal stop is explicitly the source C39 mass veto during the **first Newton trial**, not a committed physical evolution point.

The original last trial gives

```text
H²                 = 1.9196310273959685e+26
Vpp                = 7.2704406617212974e-103
rho_idm            = 1.9339468989379002e+20
mass_curvature     = -3.3249999999759356e-05
3*rho_idm*curvature= -1.9291120316765940e+16
m_eff²/H²          = -1.0049389722010728e-10
original veto      = -1e-10
excess magnitude   = 0.4938972201%
```

An independently coded parser reproduced this original trace summary. A separate strict parser checks the exact SHA, entire gate-COMMIT chronology, monotonic counters, C39 term arithmetic, original veto and last proposed step. **14 read-only adversarial/unit tests PASS** on the pinned raw bytes, including corrupted counters, missing markers, source-physics decomposition tampering and deterministic CSV/JSON output.

## Important negative boundary

This supports **"termination by the source physical veto at a normal proposed interval"**, not **"RIMS has demonstrated a physical instability"**. The model can still have numerical or shooting issues, and full post-COMMIT vectors and source-attested physical masses were not logged. If `g(y_trial)<0`, this alone does not imply `g(y_commit)<0`. The exact change obeys

`g(y_commit)-g(y_eval) = integral_0^1 grad_y g[y_eval+t(y_commit-y_eval)] dot (y_commit-y_eval) dt`,

but the necessary state displacement and certified derivative bound are unavailable in C44. The original normalization flag was not set to require a viable normalized universe. No observational preference, model detection, production posterior or Bayes factor is established.

## Reproducibility and next physical gate

The full new local audit package (distributed separately) contains the immutable C44 stderr, a 618-row COMMIT CSV, an 845-row TRIAL CSV, both independently implemented Python parsers, 14 tests, two native-data plots, precise summary JSON, titled four-page PDF **RIMS_Native_Step_Plateau_Physical_Veto_C55.pdf**, separately maintained references.bib and original C55 ZIP as unmodified parent evidence. This GitHub [independent script](../mcmc_o3/c55_native_step_crosscheck.py) runs read-only against the original stderr and requires its exact SHA-256.

**Hard gate still not executed:** compile the current source-locked native CLASS implementation and collect exact post-COMMIT vector and live runtime coefficient. The last GitHub Actions run visible as of 6 November 2026 was the old 30 October C44 run; no C55 Actions execution is verified. This chat's GitHub connector does not provide workflow dispatch, and the local runtime cannot clone or compile the original pinned CLASS source. The [manual-only static preflight](https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c55-accepted-source-state.yml) remains required before one explicitly authorized original native-case invocation. Do not weaken the physical veto, change the frozen parameters, or claim accepted-state stability from veto-selected successful evaluations.

The full RIMS theory/mode hierarchy, 81 background family scan, matched Planck/DESI/Pantheon+ inference, independent Boltzmann parity, radiative-protection branch and nonlinear covariance hard gates remain intact. This evidence is a **technical supplement to the full master, never a replacement or compression**.

## Verified local deliverable manifest (2026-11-06)

- **Titled PDF:** `RIMS_Native_Step_Plateau_Physical_Veto_C55.pdf`, A4 single-column **4 pages**, SHA-256 `3199431786ea93dab6d4513e0b6952f449f77770c72eb0fc23370d562d012303`. Rendered and inspected; reference list on page 4, no isolated reference page and no overfull boxes.
- **Supplement + unchanged full C55 parent ZIP:** `RIMS_C55_Real_Native_Step_Forensics_20261106.zip`, 8,750,622 bytes, SHA-256 `9f32711560181feb9dc11f5325ddd6a9ba56ec318ed2659bdc3152be705f4913`.
- The package includes the original C55 ZIP (unmodified SHA256 `3b06fd1653f555229aad3542defc27a81864426bcd8f3c61a01f63330f28f7ea`), the original C44 native stderr, 618 accepted-coordinate CSV rows, 845 trial-event CSV rows, two independent parsers, result JSON, two graphs, 14 adversarial tests, a bilingual README, this 4-page note and separate `references.bib`.
- Fresh ZIP extraction, all 14 tests, original C44/C55 SHA checks, independent parser numeric parity, deterministic CSV/JSON reproduction, archive CRC and member SHA-256 verification: **PASS**.
- **C55 GitHub workflow status:** Not yet run; no new native CLASS compute, post-COMMIT mass measurement or physics-promotion claim.
