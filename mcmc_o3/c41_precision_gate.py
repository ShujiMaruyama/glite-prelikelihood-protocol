#!/usr/bin/env python3
"""Fail-closed C41 predefined precision modes, imported by native runner.

No fitting, retries, shooting changes, physics modifications or threshold changes.
This validates only the intended INPUT dictionary change; it cannot certify
how the compiled solver internally evaluates precision or shoots.
"""
import hashlib
import json
from pathlib import Path

EXPECTED_FREEZE = "0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
EXPECTED_CASE_SHA = "9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284"
EXPECTED_UPSTREAM = "e85808324f51fc694d12e3ed7439552a3c3f9540"
EXPECTED_MODES = {"tight10-one": 1e-11, "tight100-one": 1e-12}
REGISTRY = Path(__file__).with_name("C41_PINNED_PRECISION_REGISTRY_20261027.json")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_registry(path=REGISTRY):
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    if j["schema"] != "RIMS_C41_PINNED_PRECISION_TWO_RUN_PREDECLARATION_V1":
        raise ValueError("Wrong C41 registry schema")
    lineage = j["lineage"]
    if (lineage["class_upstream_commit"] != EXPECTED_UPSTREAM
            or lineage["c23_81_freeze"] != EXPECTED_FREEZE
            or lineage["frozen_case_sha256"] != EXPECTED_CASE_SHA
            or lineage["frozen_case_id"] != "rims_002"):
        raise ValueError("C41 original physics/freeze lineage changed")
    p = j["pinned_class_precision_source"]
    if not (p["tol_background_integration_default"] == 1e-10
            and p["background_Nloga_default"] == 40000
            and p["background_evolver_default"] == "ndf15"
            and p["no_sampling_change"] is True):
        raise ValueError("Different CLASS default precision semantics")
    e = j["experiment"]
    if (set(e["manual_modes"]) != set(EXPECTED_MODES)
            or e["change_only"] != "tol_background_integration"
            or e["original_veto_tolerance"] != 1e-10
            or e["original_veto_must_remain_enabled"] is not True
            or e["no_shooting_retuning"] is not True
            or e["run_mode_default"] != "static-only"
            or e["automatic_native_runs"] != 0):
        raise ValueError("Unsafe C41 registry edit")
    for mode, expected in EXPECTED_MODES.items():
        if e["manual_modes"][mode] != {"tol_background_integration":expected, "max_new_compute_calls":1}:
            raise ValueError("Mode incorrectly configured: " + mode)
    if any(j["execution_receipts"].get(k) is not False for k in
           ("two_new_native_cases_executed", "two_new_native_computes_executed", "integration_convergence_verified")):
        raise ValueError("Pre-execution registry cannot declare post-hoc work")
    return j


def precision_params(original, mode):
    """Adds exactly one admissible solver precision key to the frozen input."""
    if mode not in EXPECTED_MODES:
        raise ValueError("Unknown or non-native C41 run mode")
    base = dict(original)
    if "tol_background_integration" in base:
        raise ValueError("Precision already present in original params")
    if base.get("rims_stability_tolerance") != 1e-10:
        raise ValueError("Stability threshold not original 1e-10")
    if base.get("rims_enforce_stability") != "yes":
        raise ValueError("Original native RIMS stability veto must remain ON")
    if base.get("output") != "" or any(k in base for k in ("ic","non_linear","non linear")):
        raise ValueError("Unexpected perturbation or shooting input")
    new = {**base, "tol_background_integration": EXPECTED_MODES[mode]}
    changes = {k for k in new if k not in base or new[k] != base[k]}
    if changes != {"tol_background_integration"}:
        raise AssertionError("Input-guard violation")
    return new


def validate_native_record(d):
    """Also require the *native* diagnostic to show its original strict veto."""
    if not (d["tolerance"] == 1e-10 and d["ratio"] < -1e-10):
        raise ValueError("Not an unchanged original native stability veto")
    if not (d["matter_term"] < 0 and d["mass_curvature"] < 0):
        raise ValueError("C39 sign classification no longer matched; do not claim common sign")
    return True
