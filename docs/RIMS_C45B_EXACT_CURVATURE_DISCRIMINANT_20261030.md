# RIMS C45b: source-specific analytic coupling discriminant (2026-10-30)

## Immutable source and evidence
Inherited from C45 and its C44 Run #2 original (Actions run 41000757103).
Original C44 native ZIP SHA-256: `cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`.
Frozen input `rims_002`, source-locked RIMS patch, original physical gate threshold `epsilon=1e-10`. C44 observed 618 NDF15 COMMIT records, but **no committed physical g measurement**.

## Derived exact source identities
The original RIMS mass law:
`s(phi)=1/(1+exp[-2 alpha_U (phi-phi_t)])`, `m/m_ref=sqrt(s/s_ref)`,
`alpha_d=d ln(m)/d phi=alpha_U (1-s)`,
`kappa=m''/m=alpha_U^2(1-s)(1-3s)=alpha_d(3 alpha_d-2 alpha_U)`.
Square completion:
`kappa/alpha_U^2=3(s-2/3)^2-1/3`.
Therefore for `alpha_U>0, 0<s<1`, `kappa` lies in `[-alpha_U^2/3,alpha_U^2]`, is negative iff `s>1/3`, and has unique minimum at `s=2/3`.

Using CLASS H-squared density normalization `Omega_idm=rho_idm/H^2`, original effective mass:
`R=Vpp/H^2 + 3 Omega_idm kappa`, veto `R<-epsilon`.
Define `E=Vpp/H^2`, `B=Omega_idm alpha_U^2`.
Then `g=R+epsilon=E+epsilon-B+9B(s-2/3)^2`.
For a state with fixed `E,B`, a veto is possible iff `B>E+epsilon` and
`|s-2/3|<sqrt[1-(E+epsilon)/B]/3` intersected with `0<s<1`.
This is a **conditional instantaneous parameter slice**; varying s while fixing E,B is NOT a background trajectory.

## Frozen native failed Newton trial (NOT an accepted state)
Source-locked values for `alpha_U=0.01, s=0.64999999997593583`:
- Curvature `-3.3249999999759356e-5`, = `99.75%` of most-negative logistic magnitude.
- `Omega_idm=1.0074576162489683e-6`; local `Omega_crit=1.002506265671416e-6`.
- Conditional band `0.6379875765259606<s<0.6953457568073727`.
- Original trial `R=-1.0049389722010728e-10`, signed gate `g=-4.938972201072652e-13`.
- Last COMMIT `a=3.891990717634451e-10`; failed TRIAL `a=3.9459045585355262e-10`.
No root bracket or accepted instability.

## Explicit local comparator
At same local `H,rho_idm,Vpp,m(phi*)` and first logarithmic slope `beta*=alpha_d(phi*)`, exponential `m_exp=m(phi*)exp[beta*(phi-phi*)]` has `kappa_exp=beta*^2`.
The exact RIMS curvature departure is `kappa_RIMS-kappa_exp=-2 alpha_U^2 s(1-s)`.
At the **rejected C44 trial only**, `R_exp=+3.702406740224075e-11` and
`R_RIMS-R_exp=-1.3751796462234804e-10`.
This is a fixed-state counterfactual, NOT independently evolved or observationally matched models.

## Forward falsifiers after physically accepted background exists
- Curvature phase identity/turnover at s=1/3, minimum at s=2/3.
- Physical accepted-state direct g obeys the instantaneous bound.
- Mass transfer continuity: `Q/(H rho_idm)=d ln(m_idm)/d ln(a)=0.5 d ln(s)/d ln(a)` in original CLASS convention.
- Self-consistent, evolved competitor must be compared with same data/prior/nuisance/covariance, not only the local fixed-state test.

Prior art: Amendola (Phys Rev D 62 043511, 2000; Phys Rev D 69 103524, 2004), Baldi (MNRAS 411 1077, 2011), Yang et al. (EPJC 86 1115, 2026). Varying couplings and density-dependent effective mass are known: do NOT claim first discovery.

## Execution/claim firewall
A separate local C45b reproducibility bundle (source, full C44 archive, PDF, 33 new + 31 inherited C43/C45a local tests) exists; it is not yet uploaded to this GitHub branch. There is no C45b new CLASS compute, no adopted stable background, no convergence claim, no production MCMC/posterior/Bayes factor, no observed model superiority. C45a COMMIT state-vector overlay remains synthetic-only. Must obtain physical g on actual COMMIT states before any root bracket.
