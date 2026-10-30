# C44 Run #2 independent read-only audit — C45 inherited evidence

Date: 2026-10-30. Evidence only; no new native CLASS run for this checkpoint.

- GitHub Actions source run: https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/41000757103 (run #2, original C44 branch)
- Native GitHub Artifact ID: 12952739981 (rims-c44-original-native-one-phase-trace)
- Artifact ZIP SHA-256: cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c
- Original native stderr SHA-256: 9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d
- Frozen case: rims_002; source SHA: 9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284
- Frozen 81-case set SHA: 0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0

## Reproduced forensic result

Exactly one original native CLASS compute attempt, on unmodified original physical veto threshold 1e-10 and unchanged default integration tolerance. Original shooting veto reproduced. Independent archive member SHA-256 manifest: 12/12 verified, ZIP structure valid.

Raw 2,083-line stderr yields one NDF15 BEGIN, 845 TRIAL evaluations, 618 ACCEPT_GATE and 618 COMMIT records. The last committed state is at ln(a) = -21.666930150605552 and a = 3.891990717634451e-10. A subsequent Newton iteration-1 TRIAL at ln(a) = -21.653172709521662, a = 3.945904558535526e-10 triggered the native RIMS C39 physical veto; that trial was **NOT COMMITTED**. The gap in ln(a) is 0.013757441083889432 (a_trial / a_commit - 1 = 0.013852510145205166).

At the *rejected trial*, effective mass ratio = -1.0049389722010728e-10, 0.4938972201073% beyond negative threshold -1e-10. Archived source terms verify 3*rho_idm*mass_curvature = matter_term, and (Vpp+matter_term)/H^2 = ratio, at float precision.

Read-only C44 independent package: RIMS_C44_RUN2_INDEPENDENT_FORENSIC_20261030.zip, SHA-256 = 800f51e89f40128d41dd4b91b8cce83f6a7415c7b1918428bff7dca9ecce6b43. Includes raw Run #2 archive, audit code, full 618-row committed coordinate ledger, 16 passing adversarial regression tests and C45 preregistration.

## Hard Claim Boundary

**No effective mass or stability-margin value was measured at the final committed state.** Last committed step positions and the veto's uncommitted candidate do NOT form a physical root bracket. No physical instability detection, accepted-state stability certificate, numerical convergence, normalized background, MCMC posterior, Bayes factor, or model preference is claimed. C38/C39/C40/C41/C42/C43/C44 original branches and data remain unchanged.

C45 may only promote claims after separate source-locked, side-effect-isolated measurement of original m_eff^2/H^2 on *committed* y-state(s) with identical physical parameters, with numerical and source integrity audit; no automatic native runs.
