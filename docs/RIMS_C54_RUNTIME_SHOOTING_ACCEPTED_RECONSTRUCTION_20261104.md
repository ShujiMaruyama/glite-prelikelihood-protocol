# RIMS C54 — Runtime Shooting and Accepted-State Algebraic Reconstruction

**4 November 2026 — Shuji Maruyama, Independent Researcher, Muroran, Hokkaido, Japan. ORCID 0009-0007-5034-7634.**

© 2026 Shuji Maruyama. All rights reserved.

## Core factual correction

The original frozen C44 rims_002 input supplies scalar parameter list (5,0,0,0,4.44,0), Omega_scf=0.001, and scf_tuning_index=0. The **CLASS shooting solver changes the runtime scalar-potential parameter**, using an initial high-lambda guess sqrt(3/Omega_scf). Therefore the input lambda=5 must not be used as if it were the frozen source's runtime coefficient.

The original C44 C39 veto was recorded at an **uncommitted failed Newton trial**, with phi=4.4399999947111519, Vpp=7.2704406617212974e-103, ratio=-1.0049389722010728e-10, and a=3.9459045585355262e-10.

For the original zero-polynomial-exponent scalar-potential source, V(phi;lambda)=exp(-lambda phi). **Substituting the CLASS source shooting initial guess lambda=sqrt(3000)=54.772255750516614 gives Vpp=lambda²exp(-lambda phi)=7.2704406617212974e-103**, matching the original C44 rejected trial to printed precision. Input lambda=5 would instead give 5.70955843e-9, nearly 94 orders larger. This is a **source-numerical correction**, not a claimed new gravity discovery or a direct measurement of runtime lambda on all accepted states.

## Algebraic reconstruction candidate

For a successful derivative evaluation state e and a subsequently corrected NDF15 COMMIT state c at exactly the same scale factor a, in this **specific frozen RIMS background branch**:

- s(phi) = [1+exp(-2 alpha_U (phi-phi_t))]^{-1}, mass m_d proportional to sqrt(s).
- rho_dm,c = rho_dm,e sqrt(s(phi_c)/s(phi_e)).
- Delta rho_phi = [(phi_prime_c)^2-(phi_prime_e)^2]/(6a^2) + [exp(-lambda phi_c)-exp(-lambda phi_e)]/3.
- H_c^2 = H_e^2 + (rho_dm,c-rho_dm,e) + Delta rho_phi.
- g_c(algebraic) = {lambda^2 exp(-lambda phi_c) + 3 rho_dm,c alpha_U^2 (1-s_c)(1-3s_c)} / H_c^2 + 1e-10.

**Lambda is taken from live runtime telemetry, not simply from the original input.** C54 refuses reconstruction if the runtime potential polynomial, fluid branch, NDF15 field indices, exact binary64 time-state join or source mass decomposition do not agree.

This conditional reconstruction avoids an extra call to the scientific derivative or background routine; it is **not a direct native accepted-state g measurement** and lacks a certified rounding-error enclosure. It is not yet validated for other RIMS parameter branches.

## Verified local output

- Full local source: c54_reconstruct.py, c54_source_stack.py, independent tests and original SHA-locked evidence.
- **34 local tests PASS**, including a 500-case deterministic synthetic Friedmann parity test and a C99 compiler-run smoke test of the additive-only source observer.
- The real C44 native stderr SHA256 is 9e6fb2fcc83cd47fb7e0168a83952da8ad093da86698bf8300aacb601875e42d.
- The C44 original native archive SHA256 is cf4b5165ab566210250e9c5839c0fa778e42f4b8546ab58dfa244844363f739c.
- Original C44 contained **618 committed coordinate records**, but *no* accepted-state mass values.

Release filename: **RIMS_C54_Runtime_Shooting_Audit_20261104.zip**.
Titled PDF: **RIMS_Runtime_Shooting_Accepted_State_Reconstruction_C54.pdf** (A4, three pages).
This GitHub branch also includes a standalone mathematical check under mcmc_o3/c54_runtime_shooting_math.py. The full observer/auditor and tests are preserved in the delivered ZIP, **not yet in this GitHub branch**.

The previously registered manual C53 workflow remains available for **static-only** pinned CLASS compilation at
https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c53-newton-gap.yml .
Its native-one mode must **not** be run until static validation is reviewed. No C54 workflow/native CLASS run has been performed.

## Strict scientific claim boundary

No new native CLASS execution; no committed-state g directly measured; no full shadow observer parity or rigorous floating point enclosure; no converged viable normalized cosmology; no full coupled gauge-invariant stability; no production MCMC or real-data evidence; no model superiority. The original physical veto is unchanged and may select positive g artificially. Thus C54's true contribution is the discovery and numerical audit of the hidden runtime shooting coefficient plus a source-specific, fail-closed algebraic path toward accepted-state diagnostics.

This report is browser-readable to bypass previous in-chat PDF and ZIP download failures.

## Verified final immutable delivery digests

- ZIP SHA-256: **88b05566d1da7534c177f0097daf5d0f32d0d97a2efabdc93ad1e618f1f30833** (8,163,507 bytes).
- PDF SHA-256: **29a9cee3c87b895312e815a758596e258e69a653a532efd13816f4efced86bd0** (3 pages, A4, all pages rendered and checked).
- Final ZIP re-extracted into a separate folder; 34/34 local tests, immutable C53 and C44 ZIP hashes, C44 stderr hash, ZIP CRC and all member SHA256 passed again.
- C54 source instrumentation was compiled only in a standalone mock; a real CLASS C54 binary is not yet compiled, and original/native trajectory parity remains open.
