# RIMS C50 — terminal successful derivative provenance (2026-11-02)

Shuji Maruyama | Independent Researcher, Muroran, Japan | ORCID 0009-0007-5034-7634.
© 2026 Shuji Maruyama. All rights reserved.

Parent: `rims-c49-pinned-accepted-state-integration-20261102` HEAD `a4683bcf0a1d316ac18351ca2585bacdbe4a3f6f`. No prior C38-C49 results or original physical veto were altered.

## Concrete audit hole fixed

C46's successful `DERIV` observer was inserted immediately after the nested call `background_functions()` in `background_derivs()`. The enclosing routine still performs further derivative computations/checks; it can fail after the C46 log. Thus the old C46 event meant **inner background-function success only**, not full derivative-function success. Previously this distinction was not enforced in C46-to-C49 provenance discussions.

C50's replacement observer is positioned immediately before the unique original `background_derivs` terminal `return _SUCCESS_;`. It preserves the C46 hexadecimal input-vector/physical-field trace schema and exact-state C47 bitwise COMMIT join, leaving all RIMS equations, veto settings and the original derivative instructions untouched.

The replacement source patcher requires the C39-post-overlay background SHA256 `08f6bad70c6c479bc5d6946d2a6332263bca47f8a8d7f7dcc87d9c93df681027`; the C43/C45 NDF15 overlay bytes are identical to C49. It rejects a mismatched source, unexpected terminal-exit structure and duplicate logger. Original CLASS source version remains `e85808324f51fc694d12e3ed7439552a3c3f9540`.

## Actually executed evidence

Synthetic-C adversarial fixture, same input/source under old and new observers:
- Inner and full derivative success: old emits 1, C50 emits 1.
- Inner success followed by later `background_derivs` error 7: old emits **1 misleading** success record; C50 emits **0**.
- Disabled observer: neither emits.
- Existing C46 successful-derivative record parser accepts the C50 hexadecimal schema.

C50: **19 new tests PASS**. Original unmodified C49 archive, freshly extracted: **182/182 tests PASS**. **201 software/synthetic-C tests PASS in total**; original C49 ZIP SHA256 `0a6eb6903f391df798d34d5b9c4f318c97cacdb063cd3636533ba8b5efd10676`. Re-extracting the final C50 ZIP and executing `bash reproduce_all.sh` reproduced all 201 PASS; its CRC and embedded file SHA manifests passed.

## Immutable distribution

Full self-contained release `RIMS_C50_TERMINAL_SUCCESS_AUDIT_20261102.zip`:
SHA256 `fc857072259d797e15eec96321a8c66e309555ed3f068b08863bf9240ccd8e41`.

**User naming request implemented:** the 4-page A4 single-column PDF is named
`RIMS_Terminal_Success_Observer_C50.pdf`, *not main.pdf*.
Its Overleaf-rebuild sources retain conventional `paper/main.tex` + separate `paper/references.bib`. PDF pages were rendered and visually checked, with no final LaTeX box overflow warnings.

Release includes intact C49 ZIP, C50 new patcher `src/c50_terminal_success_observer.py`, successor stack `src/c50_source_stack.py`, 19 adversarial regression tests, inherited C49 source reference copies, `reproduce_all.sh`, `paper/build_pdf.sh`, SHA256SUMS, README and titled PDF.

## Strict scientific limits

This GitHub commit only registers this reproducible scientific ledger; the C50 source and executable package are in the release ZIP and are NOT committed to GitHub. There is **no new native full-CLASS compilation/run**, **no newly measured g on 618 C44 COMMITs**, no accepted-trajectory root bracket, no certified normalized viable background, no production Planck/DESI/RSD/Pantheon+ inference, no independent Boltzmann implementation, no observational detection and no model preference.

Next hard gate: register executable source and static-only CI on C50 branch; compile an original pinned disposable CLASS checkout in static-only mode, audit full source/binary provenance, then consider a separate, manually authorized one-case native run with no parameter relaxation. A new native run must fail closed on missing exact terminal-success+same-step COMMIT match. No automatic reruns, paid services or retuning.
