from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from getdist.mcsamples import loadMCSamples

RHAT_MAX = 0.01
ESS_MIN = 1000.0


def weighted_quantile(values, weights, q):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cdf = np.cumsum(weights)
    cdf /= cdf[-1]
    return float(np.interp(q, cdf, values))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    samples = loadMCSamples(str(root), settings={"ignore_rows": 0.30}, no_cache=True)
    names = [p.name for p in samples.getParamNames().names]
    weights = np.asarray(samples.weights, dtype=float)

    sampled_interest = [
        "H0", "omega_b", "omega_cdm", "omega_dm", "logA", "n_s", "tau_reio",
        "Omega_scf", "rims_alpha_U", "rims_shell_u_i", "rims_s_i",
        "rims_phi_transition", "A_planck", "Omega_m", "sigma8", "S8",
    ]
    rows = []
    ess_values = []
    for name in sampled_interest:
        if name not in names:
            continue
        j = names.index(name)
        vals = samples.samples[:, j]
        ess = float(samples.getEffectiveSamples(j))
        ess_values.append(ess)
        mean = float(np.average(vals, weights=weights))
        rows.append({
            "parameter": name,
            "mean": mean,
            "std": float(np.sqrt(np.average((vals - mean) ** 2, weights=weights))),
            "q025": weighted_quantile(vals, weights, 0.025),
            "q16": weighted_quantile(vals, weights, 0.16),
            "q50": weighted_quantile(vals, weights, 0.50),
            "q84": weighted_quantile(vals, weights, 0.84),
            "q975": weighted_quantile(vals, weights, 0.975),
            "ESS": ess,
        })
    pd.DataFrame(rows).to_csv(out / "posterior_summary.csv", index=False)

    try:
        rminus1 = float(samples.getGelmanRubin())
    except Exception:
        rminus1 = float("nan")

    best_index = int(np.argmin(samples.loglikes))
    best_params = {
        name: float(samples.samples[best_index, names.index(name)])
        for name in names
        if name != "chi2" and not name.startswith("chi2__")
    }
    aggregate = {"chi2__CMB", "chi2__BAO", "chi2__SN"}
    leaves = [name for name in names if name.startswith("chi2__") and name not in aggregate]
    components = {
        name: float(samples.samples[best_index, names.index(name)])
        for name in leaves
    }
    if "chi2" in names:
        best_chi2 = float(samples.samples[best_index, names.index("chi2")])
    elif components:
        best_chi2 = float(sum(components.values()))
    else:
        best_chi2 = float("nan")

    extra = {}
    if "rims_alpha_U" in names:
        vals = samples.samples[:, names.index("rims_alpha_U")]
        extra["P_alpha_lt_0p005"] = float(np.sum(weights[vals < 0.005]) / np.sum(weights))
        extra["P_alpha_lt_0p01"] = float(np.sum(weights[vals < 0.01]) / np.sum(weights))
        extra["alpha_95_upper"] = weighted_quantile(vals, weights, 0.95)

    miness = float(min(ess_values)) if ess_values else None
    accepted = bool(
        np.isfinite(rminus1)
        and rminus1 < RHAT_MAX
        and miness is not None
        and miness >= ESS_MIN
    )

    summary = {
        "model": args.model,
        "burnin_fraction_removed": 0.30,
        "weighted_samples_after_burnin": float(np.sum(weights)),
        "distinct_rows_after_burnin": int(len(weights)),
        "getdist_Rminus1": rminus1,
        "minimum_parameter_ESS": miness,
        "declared_Rminus1_max": RHAT_MAX,
        "declared_min_ESS": ESS_MIN,
        "production_acceptance": accepted,
        "best_sample_minuslogpost": float(samples.loglikes[best_index]),
        "best_sample_chi2_sum": best_chi2,
        "best_sample_chi2_components": components,
        "best_sample_parameters": best_params,
        **extra,
    }
    (out / "mcmc_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
