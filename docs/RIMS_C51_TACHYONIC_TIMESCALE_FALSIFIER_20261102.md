# RIMS C51 — quantitative tachyonic timescale versus source veto (2026-11-02)

Author: Shuji Maruyama; Independent Researcher, Muroran, Hokkaido, Japan. ORCID 0009-0007-5034-7634.
© 2026 Shuji Maruyama. All rights reserved.

## A real, previously observed native datum — restricted to UNCOMMITTED Newton trial

C44 Run2, frozen native case `rims_002`, original stability cutoff `-1e-10`, SHA-locked input. The C44 independent audit archive is SHA-256 `800f51e89f40128d41dd4b91b8cce83f6a7415c7b1918428bff7dca9ecce6b43` and contains original native artifact SHA-256 `cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c`.
- The failed candidate (Newton trial, NOT a committed state) had `R=m_eff^2/H^2=-1.0049389722010728e-10` at `a=3.945904558535526e-10`.
- 618 accepted/committed state coordinates were archived, but **the original physical mass ratio has not been measured at these commits**.
- The old C44 physical veto remains unchanged. No C51 CLASS run, accepted-state stability, normalized cosmology or matched inference has been executed.

## New C51 exact conditional toy consequences

For an isolated *canonical scalar only*, no metric/dark-matter perturbation coupling, `u_NN+gamma u_N+[(k/aH)^2+R]u=0`, with `gamma=3-epsilon_H>0`, the instantaneous growing root for negative `R=-mu^2` and `q=k/(aH)<mu` is

`lambda_plus=2(mu^2-q^2)/[gamma+sqrt(gamma^2+4(mu^2-q^2))]`.

With the **uncommitted C44 trial** held constant hypothetically, `mu=1.0024664444264819e-5`; for a radiation-like background `epsilon_H=2` and homogeneous `q=0`, `lambda_plus=1.0049389721000826e-10` per e-fold and a hypothetical 10-e-fold modal amplitude increase of `1.0049389726050337e-9`. With exact initial rest condition `u_N(0)=0`, the increase is `9.044496377301028e-10`. Neither is a RIMS observable or physical accepted-state growth.

At the same candidate, the **instantaneous scalar-only** gradient crossover is `k/(aH)=mu~1.0024664e-5`. Using the CLASS-internal inverse-Mpc H value, the formal trial `kcritical=0.05480564602652219/Mpc`. This is a super-Hubble modal condition, NOT a surveyed galaxy-scale instability or a transfer-function forecast.

Radiation-like `q(N)=q0 exp(N)` would move a mode starting at `q0=mu/2` outside the instantaneous negative-frequency region after only `ln2=0.6931471805599453` e-folds (under frozen mass ratio). The full coupled system may have different eigenvalues, friction, sound speeds and gauge behavior.

An explicit arbitrary 2x2 mixing counterexample `[[-1e-10,1e-2],[1e-2,1]]` has smallest matrix eigenvalue approximately `-1e-4`, demonstrating that a tiny isolated diagonal does not bound a coupled physical spectrum. This matrix is NOT a derived RIMS operator.

Prior work: Gsponer and Noller, PRD 105, 064002 (2022), DOI 10.1103/PhysRevD.105.064002; Wolf and Lagos, PRD 100, 084035 (2019), DOI 10.1103/PhysRevD.100.084035. A negative-mass timescale distinction is existing physics, not a first discovery.

## Executed software and release

Fresh C51 conditional numeric integration and 17 adversarial/math/source-lock Python tests: **17/17 PASS**. A fail-closed original C44 SHA verifier and stable small-mass lambda formula were run, including a tested floating-point correction at the exact momentum threshold. A new Figure, PDF, and BIB/LaTeX source were produced. The final release was extracted to a separate directory and rerun: **17 PASS, C44/C50 original ZIP hashes PASS, deterministic C51 JSON PASS, C51 source SHA manifest PASS**.

Release `RIMS_C51_TACHYONIC_GROWTH_AUDIT_20261102.zip` SHA-256:
`a43ef6ebd4bde37b56f9eaa452f9237880a486d914188faa0288d069c4748e72`.
PDF name follows user request: **`RIMS_Tachyonic_Timescale_Diagnostic_C51.pdf`**, three A4 single-column pages; separate `paper/main.tex` and `paper/references.bib` in ZIP, full original C50 ZIP unmodified inside.

## Next unavoidable hard gates

(1) Real pinned CLASS C50 terminal-success accepted-state g measurements; (2) observer-vs-unobserved native trajectory parity; (3) source-derived gauge-invariant coupled matter-radiation-metric-scalar perturbation spectrum and a second code; (4) then properly matched Planck/DESI/SNe/large-scale-structure likelihoods. No prior source, model, physical threshold or claims retroactively altered. No auto-runs or paid services.

**This GitHub entry is the immutable C51 audit ledger, not an executed C51 native CLASS run. Executable C51 scripts/tests and originals are in the released ZIP, not committed to this branch.**
