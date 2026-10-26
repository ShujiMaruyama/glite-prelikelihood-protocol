# RIMS Phase II O3 matched inference

This directory freezes the production data vector and the geometry-adapted RIMS sampling coordinates.

Matched data vector:
- Planck 2018 low-l TT
- Planck 2018 low-l EE
- Planck 2018 high-l Plik TTTEEE lite native
- DESI DR2 BAO
- Pantheon+ without SH0ES

Matched primary models:
1. LambdaCDM
2. decoupled minimal-exponential canonical scalar
3. interacting minimal-exponential RIMS sampled in `(rims_alpha_U, rims_shell_u_i)`

The RIMS transition coordinate is deterministic:
`phi_t = 4.44 - u_i/(2 alpha_U)`.
The alpha_U=0 hypothesis is represented by the separate decoupled scalar comparator.

Acceptance before headline use: GetDist R-1 < 0.01 and minimum headline ESS >= 1000 for all three models.
Bayesian evidence is not computed by this workflow.
