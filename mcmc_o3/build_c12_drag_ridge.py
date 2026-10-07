#!/usr/bin/env python3
"""Build the frozen c12 RIMS transport diagnostic geometry.

This script is deliberately proposal-training/diagnostic only. It does not run MCMC,
does not alter the likelihood/theory target, and does not promote any source samples
to inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import yaml

SAMPLED = [
    "q_H", "omega_b", "omega_dm", "logA", "n_s", "tau_reio",
    "Omega_scf", "rims_alpha_U", "rims_shell_u_i", "A_planck",
]
BURN = 0.30
C10T_RUN_ID = 37248887077
C10T_ARTIFACT_ID = 11321815241
C10T_ARTIFACT_DIGEST = "sha256:5ebb566f5f816ece598ee27072dd5b3a341922a52820136069cddc404027650a"
C10T_MANIFEST_SHA256 = "02b29580d0528f0d4996d9d27f50590fcbaf3106a8190ff9f2169ca4978edb25"
C11_RUN_ID = 37281869390
C11G_ARTIFACT_ID = 11332059562
C11G_ARTIFACT_DIGEST = "sha256:a23f764b7d428c30ccdea7d749f55811f0add2212560109716d3e6e0e1a1207c"
C11G_MANIFEST_SHA256 = "79a6fe44ae6819ce839e4d6d31e700e6e97c93d494e621ddab0d44c9e7623ba6"
C11S_ARTIFACT_ID = 11334139648
C11S_ARTIFACT_DIGEST = "sha256:cee4300dfdd0f8eba0b4b3f1158061a04e22e90527b5928ed909fe4c4e0063a4"
C11S_MANIFEST_SHA256 = "92ea8dfdbac051b2069926c246ce347e44f12d487ae276417b3e260e161693ad"
C11_SELECTION_SHA256 = "c92670b0eeb0dfb3155d3b9c41e4d7daf4e4e7cf8c6e998b0ab0e2cbd1228769"
C11_COV_SHA256 = "ac7cd90a5cc60a23029c3453ebc3ac441dfc8e61f3764db2739f9fceeaab976e"
C11_SELECTED_SCALE = 5.7
PRODUCTION_RMINUS1 = 0.01
PRODUCTION_MIN_ESS = 1000.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(root: Path, expected_manifest_sha: str) -> None:
    manifest = root / "SHA256SUMS.txt"
    if not manifest.exists():
        raise FileNotFoundError(manifest)
    got = sha256(manifest)
    if got != expected_manifest_sha:
        raise RuntimeError(f"manifest hash mismatch: {root}: {got} != {expected_manifest_sha}")
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        h, rel = line.split(None, 1)
        rel = rel.strip().lstrip("*").lstrip("./")
        p = root / rel
        if not p.exists():
            raise FileNotFoundError(p)
        gh = sha256(p)
        if gh != h:
            raise RuntimeError(f"file hash mismatch: {p}: {gh} != {h}")


def read_chain(path: Path):
    first = path.read_text().splitlines()[0]
    if not first.startswith("#"):
        raise RuntimeError(f"missing header: {path}")
    names = first[1:].split()
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    if a.shape[1] != len(names):
        raise RuntimeError((path, a.shape, len(names)))
    return names, a


def reconstruct_postburn(a, names):
    wi = names.index("weight")
    w = np.rint(a[:, wi]).astype(int)
    if np.any(w < 1) or np.max(np.abs(a[:, wi] - w)) >= 1e-8:
        raise RuntimeError("non-integer Markov weights")
    full = np.repeat(a, w, axis=0)
    cut = int(math.floor(BURN * len(full)))
    return full[cut:]


def target_view(d):
    keep = ["prior", "value", "min", "max", "derived", "periodic", "drop"]
    return {
        "likelihood": d["likelihood"],
        "theory": d["theory"],
        "params": {
            k: ({x: v[x] for x in keep if x in v} if isinstance(v, dict) else v)
            for k, v in d["params"].items()
        },
    }


def pooled_within(chains, names):
    blocks = []
    means = []
    for c in chains:
        X = np.column_stack([c[:, names.index(p)] for p in SAMPLED])
        means.append(X.mean(axis=0))
        blocks.append(X - X.mean(axis=0, keepdims=True))
    Z = np.vstack(blocks)
    C = (Z.T @ Z) / float(len(Z))
    C = 0.5 * (C + C.T)
    return C, np.asarray(means)


def corr(C):
    sd = np.sqrt(np.diag(C))
    R = C / np.outer(sd, sd)
    return 0.5 * (R + R.T), sd


def generalized_between_within(W, chain_means):
    B = np.cov(chain_means, rowvar=False, ddof=1)
    ew, vw = np.linalg.eigh(0.5 * (W + W.T))
    if np.min(ew) <= 0:
        raise RuntimeError("within covariance is not SPD")
    Winvh = vw @ np.diag(1.0 / np.sqrt(ew)) @ vw.T
    G = Winvh @ B @ Winvh
    vals, vecs = np.linalg.eigh(0.5 * (G + G.T))
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    sd = np.sqrt(np.diag(W))
    physical_vec = Winvh @ vecs[:, 0]
    standardized = physical_vec * sd
    standardized /= np.linalg.norm(standardized)
    return vals, standardized


def loo_stability(chains, names, R_all, V_all):
    evals_all = np.linalg.eigvalsh(R_all)
    out = []
    for omit in range(4):
        keep = [i for i in range(4) if i != omit]
        C, _ = pooled_within([chains[i] for i in keep], names)
        R, _ = corr(C)
        ev, V = np.linalg.eigh(R)
        order = np.argsort(ev)
        ev, V = ev[order], V[:, order]
        one_cos = abs(float(np.dot(V_all[:, 0], V[:, 0])))
        U4 = V_all[:, :4]
        S4 = V[:, :4]
        singular = np.linalg.svd(U4.T @ S4, compute_uv=False)
        out.append({
            "omitted_chain": omit + 1,
            "narrowest_eigenvalue": float(ev[0]),
            "narrowest_eigenvector_abs_cosine": one_cos,
            "first4_subspace_min_cosine": float(np.min(singular)),
        })
    return evals_all, out


def parse_fast_block_factor(log_path: Path):
    if not log_path.exists():
        return None
    s = log_path.read_text(errors="replace")
    m = re.search(r"\*\s+(\d+)\s+:\s+\['A_planck'\]", s)
    return int(m.group(1)) if m else None


def write_cov(path: Path, C):
    with path.open("w") as f:
        f.write("# " + " ".join(SAMPLED) + "\n")
        np.savetxt(f, C, fmt="%.18e")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c10t-dir", required=True)
    ap.add_argument("--c11g-dir", required=True)
    ap.add_argument("--c11s-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    c10 = Path(args.c10t_dir)
    c11g = Path(args.c11g_dir)
    c11s = Path(args.c11s_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    verify_manifest(c10, C10T_MANIFEST_SHA256)
    verify_manifest(c11g, C11G_MANIFEST_SHA256)
    verify_manifest(c11s, C11S_MANIFEST_SHA256)
    if sha256(c11s / "C11S_SELECTION.json") != C11_SELECTION_SHA256:
        raise RuntimeError("c11 selection hash mismatch")
    if sha256(c11g / "rims_c11_precond.covmat") != C11_COV_SHA256:
        raise RuntimeError("c11 covariance hash mismatch")

    selection = json.loads((c11s / "C11S_SELECTION.json").read_text())
    if selection["selected_proposal_scale"] != C11_SELECTED_SCALE:
        raise RuntimeError("unexpected c11 selected scale")
    if selection["sentinel_samples_eligible_for_inference"] is not False:
        raise RuntimeError("c11s inference firewall violated")

    chains = []
    names0 = None
    for i in range(1, 5):
        names, a = read_chain(c10 / f"rims_c10t.{i}.txt")
        if names0 is None:
            names0 = names
        if names != names0:
            raise RuntimeError("chain header mismatch")
        chains.append(reconstruct_postburn(a, names))

    Craw, chain_means = pooled_within(chains, names0)
    Rraw, sd = corr(Craw)
    evals, V = np.linalg.eigh(Rraw)
    order = np.argsort(evals)
    evals, V = evals[order], V[:, order]
    raw_condition = float(evals[-1] / evals[0])
    raw_narrow = V[:, 0]

    _, loo = loo_stability(chains, names0, Rraw, V)
    min_loo_alignment = min(x["narrowest_eigenvector_abs_cosine"] for x in loo)
    min_first4_subspace = min(x["first4_subspace_min_cosine"] for x in loo)

    C11 = np.loadtxt(c11g / "rims_c11_precond.covmat")
    R11, sd11 = corr(C11)
    if np.max(np.abs(sd11 - sd)) > 5e-10:
        raise RuntimeError("c11 shrinkage unexpectedly changed marginal variances")
    raw_var = float(raw_narrow @ Rraw @ raw_narrow)
    c11_var = float(raw_narrow @ R11 @ raw_narrow)
    ridge_inflation = c11_var / raw_var

    sep_vals, sep_vec = generalized_between_within(Craw, chain_means)
    mean_span = {}
    for j, p in enumerate(SAMPLED):
        mean_span[p] = float((np.max(chain_means[:, j]) - np.min(chain_means[:, j])) / sd[j])

    sign11, ld11 = np.linalg.slogdet(C11)
    signr, ldr = np.linalg.slogdet(Craw)
    if sign11 <= 0 or signr <= 0:
        raise RuntimeError("non-positive determinant")
    ridge_scale_unrounded = float(C11_SELECTED_SCALE * math.exp((ld11 - ldr) / (2 * len(SAMPLED))))
    ridge_scale = round(ridge_scale_unrounded, 1)

    cov_path = out / "rims_c12_ridge_preserving.covmat"
    write_cov(cov_path, Craw)
    c11_cov_copy = out / "rims_c11_precond.covmat"
    c11_cov_copy.write_bytes((c11g / "rims_c11_precond.covmat").read_bytes())

    base = yaml.safe_load((c11g / "rims_exp_shell_c11_preconditioned.yaml").read_text())
    frozen_target = target_view(base)
    slow = SAMPLED[:-1]

    arms = {}
    for arm, covmat, scale in [
        ("drag_only", str(c11_cov_copy), C11_SELECTED_SCALE),
        ("drag_ridge", str(cov_path), ridge_scale),
    ]:
        y = json.loads(json.dumps(base))
        y["output"] = f"chains_c12/{arm}/rims_c12_{arm}"
        m = y["sampler"]["mcmc"]
        m["covmat"] = covmat
        m["proposal_scale"] = float(scale)
        m["learn_proposal"] = False
        m["drag"] = True
        m["blocking"] = [[1, slow], [27, ["A_planck"]]]
        m["oversample_power"] = 0.4
        m["oversample_thin"] = True
        m["measure_speeds"] = True
        if target_view(y) != frozen_target:
            raise RuntimeError(f"target changed in {arm}")
        yp = out / f"rims_c12_{arm}.yaml"
        yp.write_text(yaml.safe_dump(y, sort_keys=False, allow_unicode=True, width=160))
        arms[arm] = {"yaml": yp.name, "proposal_scale": float(scale), "covmat": covmat}

    fast_factors = {
        "c10t": parse_fast_block_factor(c10 / "c10t.log"),
        "c11s_4p8": parse_fast_block_factor(c11s / "c11s_4p8.log"),
        "c11s_5p7": parse_fast_block_factor(c11s / "c11s_5p7.log"),
        "c11s_6p5": parse_fast_block_factor(c11s / "c11s_6p5.log"),
    }

    audit = {
        "schema": "rims-phaseii-o3-c12-drag-ridge-preflight-v1",
        "role": "nonproduction_transport_root_cause_preflight",
        "source_artifacts": {
            "c10t": {"run_id": C10T_RUN_ID, "artifact_id": C10T_ARTIFACT_ID, "digest": C10T_ARTIFACT_DIGEST},
            "c11g": {"run_id": C11_RUN_ID, "artifact_id": C11G_ARTIFACT_ID, "digest": C11G_ARTIFACT_DIGEST},
            "c11s": {"run_id": C11_RUN_ID, "artifact_id": C11S_ARTIFACT_ID, "digest": C11S_ARTIFACT_DIGEST},
        },
        "source_samples_eligible_for_inference": False,
        "target_distribution_changed": False,
        "production_gate": {"GetDist_Rminus1_lt": PRODUCTION_RMINUS1, "minimum_headline_ESS_ge": PRODUCTION_MIN_ESS},
        "baseline": {
            "repaired_c10t_GetDist_Rminus1": 80.39633775303028,
            "repaired_c10t_minimum_ESS": 11.506303744675218,
            "c11_selected_scale": C11_SELECTED_SCALE,
            "fast_block_factors": fast_factors,
        },
        "root_cause_evidence": {
            "raw_within_corr_eigenvalues": list(map(float, evals)),
            "raw_within_corr_condition": raw_condition,
            "narrowest_mode_components": dict(zip(SAMPLED, map(float, raw_narrow))),
            "leave_one_chain_out": loo,
            "minimum_loo_narrow_mode_alignment": float(min_loo_alignment),
            "minimum_loo_first4_subspace_cosine": float(min_first4_subspace),
            "c11_variance_inflation_along_stable_narrowest_mode": float(ridge_inflation),
            "leading_between_within_generalized_eigenvalue": float(sep_vals[0]),
            "leading_between_within_mode_standardized_components": dict(zip(SAMPLED, map(float, sep_vec))),
            "per_parameter_chain_mean_span_in_within_sigma": mean_span,
            "interpretation": "The tight within-chain ridge is reproducible across leave-one-chain-out audits; diagonal shrinkage inflates it strongly. A_planck is isolated as a ~26-27x fast block while chain centers remain separated, so c12 tests fast dragging and ridge preservation rather than another blind long run.",
        },
        "c12_arms": {
            "drag_only": {
                **arms["drag_only"],
                "intervention": "keep c11 covariance and selected scale; replace fast oversampling-only transport with explicit fast dragging",
            },
            "drag_ridge": {
                **arms["drag_ridge"],
                "ridge_scale_unrounded": ridge_scale_unrounded,
                "intervention": "explicit fast dragging plus raw chain-centered within-chain ridge-preserving covariance; determinant-match proposal volume to c11 scale 5.7",
            },
        },
        "diagnostic_contract": {
            "fresh_four_chains_per_arm": True,
            "minutes_per_arm": 45,
            "samples_eligible_for_inference": False,
            "automatic_follow_on": False,
            "automatic_long_run": False,
            "comparison_control": "existing c11s scale=5.7 sentinel and repaired c10t diagnostics; do not rerun control",
            "required_runtime_checks": [
                "dragging is active",
                "manual blocking is exactly slow factor 1 and A_planck factor 27",
                "no CLASS error",
                "no likelihood error",
                "no workflow error other than intentional timeout termination",
            ],
            "transport_metrics": [
                "aggregate and per-chain acceptance",
                "rank-normalized Rhat",
                "bulk and tail ESS",
                "half-chain drift",
                "between/within leading generalized eigenvalue",
                "per-parameter chain-mean span in within-chain sigma",
            ],
            "no_result_promotion_rule": "Neither arm is inference. No production claim follows from a transport improvement. Any later production run requires a separate explicit authorization and frozen contract.",
        },
        "claim_boundary": {
            "production_posterior": False,
            "Bayes_factor": False,
            "model_preference": False,
            "LambdaCDM_competitiveness_verified": False,
        },
    }

    (out / "C12_DRAG_RIDGE_PREFLIGHT.json").write_text(json.dumps(audit, indent=2, sort_keys=True))
    for p in [cov_path, c11_cov_copy, out / "rims_c12_drag_only.yaml", out / "rims_c12_drag_ridge.yaml"]:
        if not p.exists():
            raise FileNotFoundError(p)
    manifest_lines = []
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            manifest_lines.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(manifest_lines) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
