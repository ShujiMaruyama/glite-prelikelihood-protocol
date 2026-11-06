# RIMS C55 — Authentic pinned CLASS C/Cython compilation PASS (2026-11-06)

**Author:** Shuji Maruyama — Independent Researcher, Muroran, Hokkaido, Japan. ORCID 0009-0007-5034-7634.  
© 2026 Shuji Maruyama. All rights reserved.

This is the first **real integrated C55 GitHub Actions CLASS build**, distinct from synthetic test fixtures and from the original C44 physical execution. The original C39 physical veto is not modified or relaxed; no new native Class.compute() call occurred.

## Live and independently checked evidence

Successful **GitHub Actions run #42147946504**:  
https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/42147946504

Original **GitHub artifact #13470788351**:  
https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/42147946504/artifacts/13470788351

Its ZIP digest, independently verified after downloading: **SHA256 a96a56fd31cf96d432b094c7f3a6d03e0d5676e5325048a145997a0c6265ed8b** (7,305 bytes). ZIP CRC check PASS; six member files were read directly: C23_FROZEN_81.json, SHA256SUMS.txt, c43_source_lock.json, c52_source_lock.json, compile_attestation.json, pytest.txt. The GitHub job log independently reports a genuine C compiler/Cython native build and a native extension import check.

### First FAILED run and concrete fix (not concealed)

Original run #42147765913: https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/runs/42147765913

**55/56 tests passed, one failed.** In the old C52 native audit input parser, an out-of-range hexadecimal float produced OverflowError, not the mandated ValueError. This failure occurred before CLASS compilation and was not a RIMS numerical or physical failure. The fail-closed exception handling was corrected in commit d6cf9a9a518d6b8b180c457c6eeb3d40e33fa403. The static-only workflow was retriggered in commit a586aa20e8614a55260be50f7dd9099f5506e384.

On successful run #42147946504:
- **56 / 56 Python tests PASS** (pytest: 56 passed in 0.39 s).
- Original frozen 81-case manifest source SHA and individual rim_002 case SHA checked.
- Original CLASS source downloaded and checked out at exact frozen commit.
- Original RIMS source patches, original physical threshold, and C39 source-lock PASS.
- The C43/C45/C50/C55 passive instrumentation was inserted and source digests recorded.
- **Real CLASS C/Cython compilation, installation and native extension import PASS**.
- Compiled binary checksum recorded in an immutable uploaded GitHub Actions artifact.
- Explicitly **zero** physical Class.compute() invocations; no real RIMS background trajectory was run.

### Recorded source and binary provenance from successful actual CI artifact

| Field | Recorded value |
|---|---|
| Original CLASS commit | e85808324f51fc694d12e3ed7439552a3c3f9540 |
| Original C39 post-overlay background SHA256 | 08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027 |
| Original NDF15 Git blob SHA1 | 0d293723510171ae9a732c80da32adb9ee52701f |
| C55 instrumented background.c SHA256 | **29dabf28d9d72e3d6cd7415a845cc4b44c985fd20ff3a025a9a98765d8afaad2** |
| C55 instrumented evolver_ndf15.c SHA256 | **e952e95612c19b163046b41aac8b0a6c2f6025390bc20e0b4b8a97570f270a36** |
| **Actually compiled classy native extension SHA256** | **35a5f7e1affdec1c09a565ec596dbd3337eea4e06a6d1904faff5d7c9925ccbf** |
| CI software tests | **56 PASS, 0 FAIL** |
| Native full CLASS computations | **0** |
| Accepted-state physical mass observations | **0** |
| Completed normalized physical background | **NO** |

The one-shot static-only push workflow was registered under .github/workflows/rims-c55-static-one-shot-source-build.yml and filters on explicit file paths; this report commit will not trigger another job. There is no physical native-one route in that push-triggered workflow.

## Interpretation and next science gate

The previously outstanding question — **does the integrated source-locked CLASS instrumented C55 actually build in a real native compiler environment?** — now has an **executed positive answer with a binary SHA256 receipt**.

That is an implementation milestone, NOT evidence of RIMS cosmological viability. C44 still has 618 committed coordinates, a failed uncommitted Newton trial m_eff²/H² = -1.0049389722010728e-10, and no accepted full state vectors. The observer success-selected g values are censored by the source veto. RIMS physical stability, viable normalization, coupled perturbation spectrum and independent code comparison remain unverified.

The next hard gate is a **separately explicitly authorized one-case native Class.compute() for the frozen rims_002 case** with original veto and C55 runtime lambda+post-COMMIT diagnostics, followed by matching the authentic C44 618-step baseline and measuring or rigorously bounding accepted g. The existing manual-only workflow is:
https://github.com/ShujiMaruyama/glite-prelikelihood-protocol/actions/workflows/rims-phaseii-c55-accepted-source-state.yml

The full RIMS journal-neutral theoretical master and Phase-II 81-case, four-chain matched inference, nonlinear covariance, independent Einstein-Boltzmann and radiative protection hard gates remain intact. Do not substitute this 56-test/compile receipt for real physics, posterior, Bayes factor, detection, or model preference. This is a browser-readable, direct-download-independent audit trail.
