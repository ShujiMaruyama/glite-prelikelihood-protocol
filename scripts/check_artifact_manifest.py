#!/usr/bin/env python3
"""Verify SHA-256 hashes in the Glite artifact manifest."""
from __future__ import annotations
import argparse, csv, hashlib, sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/artifact_hash_manifest.csv")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    manifest = (root / args.manifest).resolve()
    errors = []
    with manifest.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rel = row["relative_path"]
            path = root / rel
            if not path.exists():
                errors.append(f"MISSING {rel}")
                continue
            got = sha256(path)
            if got != row["sha256"]:
                errors.append(f"HASH_MISMATCH {rel} expected={row['sha256']} got={got}")
    if errors:
        print("Manifest verification FAILED")
        for e in errors:
            print(e)
        return 1
    print("Manifest verification PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
