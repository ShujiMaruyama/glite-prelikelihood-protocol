# Reproducibility workflow

Run from the repository root:

```bash
pip install -r requirements.txt
python scripts/generate_all_fixtures.py
python scripts/check_artifact_manifest.py --manifest data/artifact_hash_manifest.csv --root .
```

The generator writes deterministic CSV fixtures and figures. The manifest checker verifies SHA-256 hashes for tracked source, fixture, and documentation files.
