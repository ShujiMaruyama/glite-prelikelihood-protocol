# C40 original evidence (fail-closed)

The C41 static test requires the **original, unchanged** file:

`evidence/RIMS_C40_EXACT_LOCAL_VETO_ENVELOPE_20261027.zip`

- Expected size: **74,199 bytes**
- SHA-256: **`6d17d50f2079a94a58ed27867ab43ec9fc1b0d1d3cd702fe158b94824459df6b`**
- Integrity: ZIP CRC check passed during independent reconstruction from the saved original C40 artifact, and the same bytes were found nested in the original C41 distribution.

Do not invent, modify, regenerate, rename, or substitute the C40 archive.  Its absence is an **artifact-preservation failure**, not a CLASS physics result. Keep the `test_c40_original_is_preserved` test enabled.

Upload the verified ZIP into this folder on **`rims-c41-pinned-precision-convergence-20261027`**, then re-run **only `static-only`**. The manifest's frozen input, tolerances and solver settings are not modified.
