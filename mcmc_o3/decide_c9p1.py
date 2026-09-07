from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

PROD_RM1_MAX = 0.01
PROD_ESS_MIN = 1000.0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest(root: Path) -> dict[str, Any]:
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        return {"ok": False, "reason": "missing SHA256SUMS.txt"}
    bad: list[dict[str, str]] = []
    checked = 0
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        expected, rel = raw.split(maxsplit=1)
        rel = rel.lstrip("*")
        p = root / rel
        if not p.is_file():
            bad.append({"file": rel, "error": "missing"})
            continue
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        checked += 1
        if got != expected:
            bad.append({"file": rel, "expected": expected, "got": got})
    return {"ok": not bad, "checked_files": checked, "failures": bad}


def read_chain(path: Path) -> np.ndarray:
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    return a


def chain_integrity(root: Path, chain_root: str) -> dict[str, Any]:
    out: dict[str, Any] = {"all_four_present": True, "all_nonempty": True, "chains": {}}
    for i in range(1, 5):
        p = root / "chains_c9" / f"{chain_root}.{i}.txt"
        if not p.is_file():
            out["all_four_present"] = False
            out["all_nonempty"] = False
            out["chains"][str(i)] = {"present": False}
            continue
        a = read_chain(p)
        rows = int(len(a))
        weight = float(a[:, 0].sum()) if rows else 0.0
        acc = float(rows / weight) if weight > 0 else None
        if rows == 0:
            out["all_nonempty"] = False
        out["chains"][str(i)] = {
            "present": True,
            "rows": rows,
            "weight_sum": weight,
            "acceptance_estimate": acc,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
    vals = [v["acceptance_estimate"] for v in out["chains"].values()
            if v.get("acceptance_estimate") is not None]
    out["mean_chain_acceptance_estimate"] = float(np.mean(vals)) if vals else None
    return out


def transport_extrema(transport: dict[str, Any]) -> dict[str, Any]:
    max_drift = 0.0
    worst_tau = 0.0
    min_acf_ess = float("inf")
    worst_drift_rec = None
    worst_tau_rec = None
    min_ess_rec = None
    for chain, c in transport.get("chains", {}).items():
        for param, d in c.get("parameters", {}).items():
            drift = abs(float(d.get("half_drift_sigma", 0.0)))
            tau = float(d.get("tau_int", 0.0))
            ess = float(d.get("ess_acf", float("inf")))
            rec = {"chain": int(chain), "parameter": param}
            if drift >= max_drift:
                max_drift = drift
                worst_drift_rec = {**rec, "abs_half_drift_sigma": drift}
            if tau >= worst_tau:
                worst_tau = tau
                worst_tau_rec = {**rec, "tau_int": tau}
            if ess <= min_acf_ess:
                min_acf_ess = ess
                min_ess_rec = {**rec, "ess_acf": ess}
    return {
        "max_abs_half_drift_sigma": max_drift,
        "worst_half_drift": worst_drift_rec,
        "worst_tau_int": worst_tau,
        "worst_tau": worst_tau_rec,
        "minimum_acf_ess": None if not np.isfinite(min_acf_ess) else min_acf_ess,
        "minimum_acf_ess_record": min_ess_rec,
    }


def model_audit(model: str, root: Path, chain_root: str) -> dict[str, Any]:
    result: dict[str, Any] = {"model": model, "artifact": str(root)}
    result["manifest"] = verify_manifest(root)
    required = {
        "summary": root / f"analysis_{model}_c9p1" / "mcmc_summary.json",
        "transport": root / f"transport_{model}_c9p1.json",
        "sentinel": root / f"C9_SENTINEL_{model}.json",
        "contract": root / f"C9_EXECUTION_CONTRACT_{model}.json",
    }
    missing = [k for k, p in required.items() if not p.is_file()]
    result["missing_required"] = missing
    result["chains"] = chain_integrity(root, chain_root)

    if missing:
        result["decision"] = "STOP_INTEGRITY_FAILURE"
        return result

    summary = load_json(required["summary"])
    transport = load_json(required["transport"])
    sentinel = load_json(required["sentinel"])
    contract = load_json(required["contract"])

    result["summary"] = {
        "getdist_Rminus1": summary.get("getdist_Rminus1"),
        "minimum_parameter_ESS": summary.get("minimum_parameter_ESS"),
        "production_acceptance": summary.get("production_acceptance"),
        "weighted_samples_after_burnin": summary.get("weighted_samples_after_burnin"),
        "distinct_rows_after_burnin": summary.get("distinct_rows_after_burnin"),
    }
    result["transport_extrema"] = transport_extrema(transport)
    result["sentinel"] = sentinel
    result["contract_checks"] = {
        "target_distribution_unchanged": contract.get("target_distribution_changed") is False,
        "coordinate_map_unchanged_from_c8": contract.get("coordinate_map_changed_from_c8") is False,
        "sentinel_discarded": contract.get("sentinel_discarded") is True,
        "proposal_scale_2p4": abs(float(contract.get("proposal_scale", -1)) - 2.4) < 1e-12,
        "learn_proposal_false": contract.get("learn_proposal") is False,
        "production_gate_unchanged": (
            contract.get("production_gate", {}).get("GetDist_Rminus1_lt") == PROD_RM1_MAX
            and contract.get("production_gate", {}).get("minimum_headline_ESS_ge") == PROD_ESS_MIN
        ),
    }

    integrity_ok = (
        result["manifest"]["ok"]
        and not result["missing_required"]
        and result["chains"]["all_four_present"]
        and result["chains"]["all_nonempty"]
        and all(result["contract_checks"].values())
    )
    r = summary.get("getdist_Rminus1")
    e = summary.get("minimum_parameter_ESS")
    prod = (
        r is not None and np.isfinite(float(r)) and float(r) < PROD_RM1_MAX
        and e is not None and float(e) >= PROD_ESS_MIN
    )
    result["recomputed_production_gate"] = bool(prod)

    if not integrity_ok:
        result["decision"] = "STOP_INTEGRITY_FAILURE"
    elif prod:
        result["decision"] = "FREEZE_PRODUCTION_ACCEPTED"
    else:
        result["decision"] = "ALLOW_ONE_C9P2_SAME_GEOMETRY_RESUME"
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit frozen c9p1 artifacts and apply the predeclared c9p2 rule.")
    ap.add_argument("--scalar-artifact", required=True)
    ap.add_argument("--rims-artifact", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    models = {
        "scalar": model_audit("scalar", Path(args.scalar_artifact), "scalar_c9"),
        "rims": model_audit("rims", Path(args.rims_artifact), "rims_c9"),
    }
    decisions = {k: v["decision"] for k, v in models.items()}

    if all(v == "FREEZE_PRODUCTION_ACCEPTED" for v in decisions.values()):
        joint = "FREEZE_JOINT_PRODUCTION_ACCEPTED"
    elif any(v == "STOP_INTEGRITY_FAILURE" for v in decisions.values()):
        joint = "STOP_BEFORE_FURTHER_SAMPLING"
    else:
        joint = "ALLOW_C9P2_ONLY_FOR_MODELS_NOT_YET_ACCEPTED"

    out = {
        "schema": "rims-phaseii-o3-c9p1-decision-audit-v1",
        "production_gate": {
            "GetDist_Rminus1_lt": PROD_RM1_MAX,
            "minimum_headline_ESS_ge": PROD_ESS_MIN,
        },
        "models": models,
        "joint_decision": joint,
        "claim_boundary": (
            "No posterior/evidence/detection/model-preference claim is authorized for any model "
            "whose recomputed production gate is false."
        ),
    }
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "joint_decision": joint,
        "model_decisions": decisions,
        "headline": {
            k: {
                "Rminus1": v.get("summary", {}).get("getdist_Rminus1"),
                "min_ESS": v.get("summary", {}).get("minimum_parameter_ESS"),
                "mean_acceptance": v.get("chains", {}).get("mean_chain_acceptance_estimate"),
                "max_abs_half_drift_sigma": v.get("transport_extrema", {}).get("max_abs_half_drift_sigma"),
                "min_acf_ess": v.get("transport_extrema", {}).get("minimum_acf_ess"),
            } for k, v in models.items()
        }
    }, indent=2))


if __name__ == "__main__":
    main()
