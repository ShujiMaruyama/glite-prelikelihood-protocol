#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np

SAMPLED = [
    "q_H", "omega_b", "omega_dm", "logA", "n_s", "tau_reio",
    "Omega_scf", "rims_alpha_U", "rims_shell_u_i", "A_planck",
]
BURN = 0.30


def read_chain(path: Path):
    first = path.read_text().splitlines()[0]
    if not first.startswith("#"):
        raise RuntimeError(f"missing header: {path}")
    names = first[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    return names, a


def reconstruct(a, names):
    wi = names.index("weight")
    w = np.rint(a[:, wi]).astype(int)
    if np.any(w < 1) or np.max(np.abs(a[:, wi] - w)) >= 1e-8:
        raise RuntimeError("weights are not positive integers")
    full = np.repeat(a, w, axis=0)
    cut = int(math.floor(BURN * len(full)))
    return full[cut:], int(len(a)), int(w.sum())


def between_within(C, means):
    B = np.cov(means, rowvar=False, ddof=1)
    ew, vw = np.linalg.eigh(0.5 * (C + C.T))
    if np.min(ew) <= 0:
        return None
    Wih = vw @ np.diag(1 / np.sqrt(ew)) @ vw.T
    G = Wih @ B @ Wih
    ev = np.linalg.eigvalsh(0.5 * (G + G.T))
    return float(np.max(ev))


def scan_log(path: Path):
    if not path or not path.exists():
        return {"path": str(path) if path else None, "fatal_markers": [], "drag_markers": [], "blocking_markers": []}
    lines = path.read_text(errors="replace").splitlines()
    fatal = []
    drag = []
    blocking = []
    fatal_re = re.compile(r"(Traceback|Segmentation fault|MPI_ABORT|Error in function|Likelihood.*error|CLASS.*error|exception occurred)", re.I)
    for line in lines:
        if fatal_re.search(line):
            fatal.append(line[-500:])
        if re.search(r"drag", line, re.I):
            drag.append(line[-500:])
        if "A_planck" in line and ("*" in line or "block" in line.lower()):
            blocking.append(line[-500:])
    return {
        "path": str(path),
        "fatal_markers": fatal[:100],
        "drag_markers": drag[:100],
        "blocking_markers": blocking[:100],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="chain root without .1.txt suffix")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--log")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    chains = []
    names0 = None
    rows_total = 0
    weights_total = 0
    chain_stats = {}
    for i in range(1, 5):
        p = Path(f"{root}.{i}.txt")
        if not p.exists() or p.stat().st_size == 0:
            raise FileNotFoundError(p)
        names, a = read_chain(p)
        if names0 is None:
            names0 = names
        if names != names0:
            raise RuntimeError("header mismatch")
        full, rows, wsum = reconstruct(a, names)
        chains.append(full)
        rows_total += rows
        weights_total += wsum
        chain_stats[str(i)] = {
            "distinct_rows": rows,
            "weight_sum": wsum,
            "acceptance": float(rows / wsum),
            "postburn_reconstructed_steps": int(len(full)),
        }

    min_draws = min(len(c) for c in chains)
    eq = [c[-min_draws:] for c in chains]

    import arviz as az
    diagnostics = {}
    Xcentered = []
    means = []
    for c in chains:
        X = np.column_stack([c[:, names0.index(p)] for p in SAMPLED])
        means.append(X.mean(axis=0))
        Xcentered.append(X - X.mean(axis=0, keepdims=True))
    means = np.asarray(means)
    Z = np.vstack(Xcentered)
    C = (Z.T @ Z) / len(Z)
    sd = np.sqrt(np.diag(C))

    for j, p in enumerate(SAMPLED):
        arr = np.stack([c[:, names0.index(p)] for c in eq], axis=0)
        rhat = float(np.asarray(az.rhat(arr, method="rank")))
        bulk = float(np.asarray(az.ess(arr, method="bulk")))
        tail = float(np.asarray(az.ess(arr, method="tail", prob=(0.05, 0.95))))
        drifts = []
        for c in chains:
            v = c[:, names0.index(p)]
            h = len(v) // 2
            s = float(np.std(v, ddof=1))
            d = float(abs(np.mean(v[-h:]) - np.mean(v[:h])) / s) if s > 0 and h > 0 else 0.0
            drifts.append(d)
        span = float((np.max(means[:, j]) - np.min(means[:, j])) / sd[j]) if sd[j] > 0 else None
        diagnostics[p] = {
            "rank_Rhat": rhat,
            "bulk_ESS": bulk,
            "tail_ESS": tail,
            "max_half_chain_drift_sigma": max(drifts),
            "chain_mean_span_within_sigma": span,
        }

    worst_r = max(diagnostics.items(), key=lambda kv: kv[1]["rank_Rhat"])
    min_bulk = min(diagnostics.items(), key=lambda kv: kv[1]["bulk_ESS"])
    min_tail = min(diagnostics.items(), key=lambda kv: kv[1]["tail_ESS"])
    max_span = max(diagnostics.items(), key=lambda kv: kv[1]["chain_mean_span_within_sigma"])

    out = {
        "schema": "rims-phaseii-o3-c12-arm-audit-v1",
        "arm": args.arm,
        "eligible_for_inference": False,
        "burnin_fraction": BURN,
        "aggregate_acceptance": float(rows_total / weights_total),
        "chains": chain_stats,
        "equalized_tail_draws_per_chain": int(min_draws),
        "diagnostics": diagnostics,
        "worst_rank_Rhat": {"parameter": worst_r[0], **worst_r[1]},
        "minimum_bulk_ESS": {"parameter": min_bulk[0], **min_bulk[1]},
        "minimum_tail_ESS": {"parameter": min_tail[0], **min_tail[1]},
        "maximum_chain_mean_span": {"parameter": max_span[0], **max_span[1]},
        "leading_between_within_generalized_eigenvalue": between_within(C, means),
        "log_audit": scan_log(Path(args.log) if args.log else None),
        "production_gate": {"GetDist_Rminus1_lt": 0.01, "minimum_headline_ESS_ge": 1000.0},
        "claim_boundary": {
            "production_posterior": False,
            "Bayes_factor": False,
            "model_preference": False,
            "LambdaCDM_competitiveness_verified": False,
        },
    }
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
