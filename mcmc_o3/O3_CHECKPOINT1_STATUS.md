# RIMS Phase II O3 — first matched-MCMC checkpoint

Date audited: 2026-08-19
Source workflow run: `32100667897`
Head SHA of first run: `c257972e70a8e57439f5481354ba1e89e162cba9`

All three GitHub Actions jobs completed successfully at the workflow level, including source reconstruction, likelihood installation, theory+likelihood preflight, four-chain execution, posterior analysis, and artifact packaging. Each sampler process itself reached the declared 300-minute checkpoint cutoff (`exit 124`), so workflow success must **not** be read as posterior convergence.

## Convergence checkpoint

| Model | GetDist R-1 | minimum headline ESS | production acceptance |
|---|---:|---:|---|
| flat LambdaCDM | 0.0703565 | 238.636 | FAIL |
| decoupled exponential scalar | 0.637225 | 26.3505 | FAIL |
| geometry-adapted RIMS | 1.476494 | 16.7281 | FAIL |

Pre-registered production gate:

- `R-1 < 0.01`;
- minimum headline `ESS >= 1000`;
- **all three matched models must pass** before any model-comparison headline is allowed.

## RIMS geometry-adapted checkpoint

The RIMS sampler used `(alpha_U, u_i)` rather than the old `(alpha_U, phi_t)` coordinates, with

`u_i = log[s_i/(1-s_i)]`,

`phi_t = 4.44 - u_i/(2 alpha_U)`.

The first checkpoint is still far from production convergence, but the GetDist R-1 is substantially lower than the archived old-coordinate diagnostic (~9.4). This is treated only as evidence that the geometry-adapted parameterization improves sampler conditioning; it is **not** an observational result.

## Best retained checkpoint samples — debugging only

The following are retained strictly for sampler/debug bookkeeping and may not be used as model-preference claims before convergence:

- LambdaCDM best retained chi2: `2421.8229`;
- scalar best retained chi2: `2419.4031`;
- RIMS best retained chi2: `2415.2722`.

No Delta-chi2 preference statement is promoted from these values.

## Artifact lineage

- `rims-phaseii-o3-lcdm`: artifact id `9319629006`, SHA-256 digest `d714e329d1594580372538990195ff8cfb87cc049604a92b5d16616899a6bd01`;
- `rims-phaseii-o3-scalar`: artifact id `9319638688`, SHA-256 digest `71bf91088963a0277f4a6da4e982f6443097e5db87e41b9712ed54b35ea179c2`;
- `rims-phaseii-o3-rims`: artifact id `9319642811`, SHA-256 digest `aa37997038d544c349f767ee30f9645feef36ba63cf9a45f71f0f80e6496a481`.

## Continuation

Continuation run 2 is launched from these exact four-chain checkpoints. It must recover the archived chains, remove only stale lock files, preserve the frozen likelihood/model/prior definitions, and call Cobaya with `--resume`.

## Claim boundary

Until all matched models satisfy the production gate:

- no production posterior constraints;
- no RIMS detection;
- no preference over LambdaCDM;
- no Bayes factor/evidence;
- no use of the best-sample Delta chi2 as a headline result.
