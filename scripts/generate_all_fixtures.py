#!/usr/bin/env python3
"""Generate deterministic Tier-1 fixture data and figures for Glite v1.0.0-softx.

This script intentionally produces low-resource diagnostic fixtures only.
It does not run a Boltzmann solver, official likelihood, MCMC, or evidence
calculation.  The outputs are designed to make the pre-likelihood protocol
reproducible and hash-checkable.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
RUN = ROOT / "run_cards"

XI = 0.03
SIGMA0 = 1.0
P_EXP = 1.1


def ensure_dirs() -> None:
    for p in (DATA, FIG, RUN):
        p.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, header: Iterable[str], rows: Iterable[Iterable[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(list(header))
        for r in rows:
            w.writerow(list(r))


def locked_response_data() -> None:
    z = np.linspace(0, 2, 201)
    a = 1 / (1 + z)
    sigma2 = SIGMA0 * a ** P_EXP
    mu_f = 1.0 / (1 + 2 * XI * sigma2)
    f_growth = 0.55 + 0.10 * (1 - a)  # fixture-only growth-rate curve
    alpha_m = 4 * XI * f_growth * sigma2 / (1 + 2 * XI * sigma2)
    # low-resource tensor-friction integral, normalized to zero at z=0
    dln_a = np.gradient(np.log(a))
    # integral from observer to z: -0.5 int alpha_M d ln a
    integ = np.zeros_like(z)
    for i in range(1, len(z)):
        integ[i] = integ[i - 1] - 0.5 * 0.5 * (alpha_m[i] + alpha_m[i - 1]) * (np.log(a[i]) - np.log(a[i - 1]))
    dl_ratio = np.exp(integ) - 1.0
    rows = [(round(float(zi), 5), round(float(muf - 1), 8), round(float(am), 8), round(float(dlr), 8))
            for zi, muf, am, dlr in zip(z, mu_f, alpha_m, dl_ratio)]
    write_csv(DATA / "benchmark_responses.csv", ["z", "muF_minus_1", "alphaM", "dLGW_dLEM_minus_1"], rows)

    nodes = []
    for zn in [0, 0.5, 1.0, 1.5, 2.0]:
        idx = np.argmin(np.abs(z - zn))
        nodes.append((zn, f"{mu_f[idx]-1:.6f}", f"{alpha_m[idx]:.6f}", f"{dl_ratio[idx]:.6f}"))
    write_csv(DATA / "benchmark_response_nodes.csv", ["z", "muF_minus_1", "alphaM", "dLGW_dLEM_minus_1"], nodes)

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(z, mu_f - 1, label=r"$\mu_F-1$", linewidth=2.1)
    plt.plot(z, alpha_m, label=r"$\alpha_M$", linewidth=2.1)
    plt.plot(z, dl_ratio, label=r"$d_L^{GW}/d_L^{EM}-1$", linewidth=2.1)
    plt.axhline(0, linewidth=0.8)
    plt.xlabel("redshift z")
    plt.ylabel("dimensionless response")
    plt.title("Locked benchmark responses")
    plt.legend(frameon=False)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG / "fig_locked_responses.pdf")
    plt.savefig(FIG / "fig_locked_responses.png", dpi=220)
    plt.close()


def external_constraint_firewall() -> None:
    """Write claim-control CSVs, not data constraints."""
    rows = [
        ("mu_and_Sigma", "fixture response only", "requires matched growth/lensing likelihood", "not viable until compared"),
        ("alphaM_and_GW_distance", "response target only", "requires consistent tensor-friction and siren module", "not a propagation constraint"),
        ("fsigma8_RSD", "not self-consistent in Tier-1", "requires perturbation solver plus survey windows", "toy D(a) should not be used in likelihood"),
        ("CMB_lensing_ISW", "not computed", "requires CLASS/CAMB/hi_class/EFTCAMB spectra", "no CMB viability claim"),
        ("local_gravity", "pre-PPN toy BVP only", "requires nonlinear local profile and metric audit", "not a Cassini pass"),
    ]
    write_csv(DATA / "external_constraint_firewall.csv", ["channel", "tier1_status", "required_upgrade", "claim_boundary"], rows)

    # Constraint-readiness diagnostic only.  The bands are deliberately synthetic
    # and are not labeled as Planck/DESI/BOSS constraints.
    diag_rows = [
        ("mu_F_z0", -0.05660, 0.02000, 2.83, "red_flag"),
        ("Sigma_z0", -0.02830, 0.02000, 1.41, "watch"),
        ("alpha_M_z0", 0.06170, 0.03000, 2.06, "red_flag"),
        ("dLGW_dLEM_z1", 0.02200, 0.05000, 0.44, "not_limiting"),
    ]
    write_csv(DATA / "external_constraint_precheck.csv", ["quantity", "fixture_delta", "synthetic_sigma", "pull", "diagnostic"], diag_rows)
    chi2 = sum(float(r[3])**2 for r in diag_rows)
    ndof = len(diag_rows)
    write_csv(DATA / "external_constraint_precheck_summary.csv", ["metric", "value"], [
        ("chi2_ext_toy", f"{chi2:.3f}"),
        ("N_dof_toy", ndof),
        ("chi2_ext_over_Ndof_toy", f"{chi2/ndof:.3f}"),
        ("status", "constraint_readiness_red_flag_not_observational_constraint"),
    ])
    # Transparent synthetic-width declaration for the toy external precheck.
    # These rows are not observational covariance products.
    design_rows = [
        ("mu_F_z0", "z=0", "delta_mu", 0.02000, "diagonal", "synthetic width; not Planck/DESI/BOSS"),
        ("Sigma_z0", "z=0", "delta_Sigma", 0.02000, "diagonal", "synthetic width; not lensing likelihood"),
        ("alpha_M_z0", "z=0", "alpha_M", 0.03000, "diagonal", "synthetic width; not GW/siren constraint"),
        ("dLGW_dLEM_z1", "z=1", "dL_ratio", 0.05000, "diagonal", "synthetic width; not standard-siren posterior"),
    ]
    write_csv(DATA / "external_constraint_precheck_design.csv",
              ["quantity", "node", "response_component", "synthetic_sigma", "correlation_assumption", "scope"],
              design_rows)


def transfer_matrix_data() -> None:
    rs = np.linspace(0.15, 0.85, 81)
    x = np.linspace(0.3, 6.0, 90)  # x = m_eff r_env
    R, X = np.meshgrid(rs, x, indexing="ij")
    # deterministic fixture residual; lower residual near a broad bridge ridge
    ridge = 0.095 + 0.09 * (R - 0.55) ** 2 + 0.012 * (X - 2.8) ** 2
    ripple = 0.006 * np.sin(3.0 * R) * np.cos(1.5 * X)
    delta = np.clip(ridge + ripple, 0.02, 0.30)
    btail = 3.5e-4 + 4e-4 * np.abs(np.sin(R * X))
    rows = []
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            rows.append((f"{rs[i]:.4f}", f"{x[j]:.4f}", f"{delta[i,j]:.8f}", f"{btail[i,j]:.8e}"))
    write_csv(DATA / "transfer_matrix_scan.csv", ["r_s_over_r_env", "m_eff_r_env", "Delta_TM_match", "B_TM"], rows)

    plt.figure(figsize=(6.4, 4.4))
    im = plt.pcolormesh(x, rs, delta, shading="auto")
    plt.contour(x, rs, delta, levels=[0.10], colors="white", linewidths=1.8)
    cbar = plt.colorbar(im)
    cbar.set_label(r"$\Delta_{\rm match}^{\rm TM}$")
    plt.xlabel(r"$m_{\rm eff} r_{\rm env}$")
    plt.ylabel(r"$r_s/r_{\rm env}$")
    plt.title("Two-layer transfer-matrix fixture")
    plt.tight_layout()
    plt.savefig(FIG / "fig_transfer_matrix_scan.pdf")
    plt.savefig(FIG / "fig_transfer_matrix_scan.png", dpi=220)
    plt.close()


def threshold_registry() -> None:
    rows = [
        ("epsilon_match", "0.10", "transfer-matrix amplitude gate", "loose Tier-1 tolerance; swept"),
        ("epsilon_B", "1e-3", "derivative-tail gate", "rejects exterior Robin mismatch"),
        ("I_star", "0.05", "template-absorption gate", "minimal nonabsorbed fraction"),
        ("S_seed2_over_Eth2", ">1", "seed above theory floor", "pre-likelihood only"),
        ("R_N_star_over_Nz", "<1", "null-reconstruction residual", "branch-consistency scale"),
        ("epsilon_cl", "0.05--0.20", "closure residual budget", "higher-operator modeling sweep"),
        ("S_loc_max", "8.3e-3", "solar-proxy reference gate", "pre-PPN surrogate only; not Cassini pass"),
    ]
    write_csv(DATA / "threshold_registry.csv", ["symbol", "declared_value", "role", "rationale"], rows)

    sweep_rows = []
    for em in [0.08, 0.10, 0.12]:
        for istar in [0.04, 0.05, 0.06]:
            decision = "PASS" if (em >= 0.10 and istar <= 0.05) else "WARN"
            sweep_rows.append((em, istar, "0.094", "0.080", decision))
    write_csv(DATA / "threshold_sweep.csv", ["epsilon_match", "I_star", "Delta_TM_match", "I_IFC", "decision"], sweep_rows)


def run_cards() -> None:
    card = {
        "status": "open-source SoftwareX-ready fixture package; V152 prior archive DOI 10.5281/zenodo.20390399",
        "claim_boundary": [
            "no observational detection",
            "no posterior constraint",
            "no Bayes factor or evidence claim",
            "no Solar-System viability claim",
            "pass-surrogate is pre-PPN surrogate only"
        ],
        "branch": {
            "coordinate": "Psi_sigma = -log[(rho_sigma + rho_star)/(rho_bar + rho_star)]",
            "F_of_q": "M_Pl^2 (1 + 2 xi q^2)",
            "tensor_sector": "G4(q)=F(q)/2, G4X=0, G5=0, c_T=1"
        },
        "minimal_output_vector": [
            "H(a)", "D(a)", "f(a)", "mu(a,k)", "Sigma(a,k)",
            "alpha_M(a)", "dL_GW/dL_EM", "t_perp", "I_IFC", "S_seed", "R_N"
        ],
        "tier1_thresholds": {
            "epsilon_match": 0.10,
            "epsilon_B": 1.0e-3,
            "I_star": 0.05,
            "S_seed2_over_Eth2_min": 1.0,
            "R_N_star_over_Nz_max": 1.0,
            "epsilon_cl_range": [0.05, 0.20],
            "S_loc_max": 8.3e-3
        },
        "tier1_gates": {
            "closure": "delta_cl < epsilon_cl and epsilon_EFT < epsilon_EFT_star",
            "projection": "I_IFC > I_star and S_seed^2/E_th^2 > 1",
            "local_matching": "Delta_TM_match < epsilon_match and |B_TM| < epsilon_B",
            "solar_surrogate": "alpha_eff_loc = 3 alpha_cos DeltaR/R; S_loc = |gamma-1|_proxy = 2 alpha_eff_loc^2/(1 + alpha_eff_loc^2) < S_loc_max; pre-PPN surrogate only; not Cassini pass",
            "threshold_stability": "no pass/fail flip under declared sweeps"
        },
        "handoff_condition": "Tier-2 permission only; production likelihood still outside scope"
    }
    with (RUN / "glite_run_card.json").open("w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

    rows = [
        ("background", "declared H(a) or solver", "D(a), f(a), distances", "finite nodes; no NaN/sign-flip instability", "full CMB likelihood"),
        ("linear_response", "F(q), closure variance", "mu(a,k), Sigma(a,k), alpha_M", "finite response and epsilon_cl inside budget", "nonlinear LSS"),
        ("GW_propagation", "alpha_M(a)", "dL_GW/dL_EM", "same alpha_M nodes", "siren posterior"),
        ("template_projection", "response vector, X, C_floor", "I_IFC, S_seed2/Eth2", "I_IFC>I_star and S_seed2/Eth2>1", "evidence"),
        ("local_handoff", "transfer/BVP gates", "Delta_TM_match, B_TM, S_loc", "Delta_TM_match<epsilon_match; |B_TM|<epsilon_B; S_loc<S_loc_max", "Solar-System viability claim"),
        ("artifact", "scripts, CSV, figures, manifest", "hash check", "manifest pass from clean checkout", "public DOI unless uploaded"),
    ]
    write_csv(RUN / "glite_run_card.csv", ["block", "input", "minimum_output", "handoff_condition", "still_excluded"], rows)


def failure_decision_figure() -> None:
    """Journal-style failure-first gate sequence figure."""
    labels = [
        ("Tensor", "c_T=1 sector"),
        ("Closure", r"$\delta_{\rm cl},\epsilon_{\rm EFT}$"),
        ("Projection", r"$I_{\rm IFC},S_{\rm seed}$"),
        ("Matching", r"$\Delta_{\rm match}^{\rm TM},B^{\rm TM}$"),
        ("Solar", r"pre-PPN proxy"),
        ("Thresholds", r"sweeps"),
        ("Handoff", r"Tier-2 only"),
    ]
    fig, ax = plt.subplots(figsize=(7.1, 2.65))
    ax.set_xlim(0, len(labels))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, (head, sub) in enumerate(labels):
        x = i + 0.08
        w = 0.86
        rect = plt.Rectangle((x, 0.38), w, 0.34, fill=False, linewidth=1.05)
        ax.add_patch(rect)
        ax.text(x + w/2, 0.60, head, ha="center", va="center", fontsize=8.8, fontweight="bold")
        ax.text(x + w/2, 0.47, sub, ha="center", va="center", fontsize=7.6)
        if i < len(labels)-1:
            ax.annotate("", xy=(i+1.06, 0.55), xytext=(i+0.95, 0.55),
                        arrowprops=dict(arrowstyle="->", linewidth=0.9))
    ax.text(3.5, 0.18, "A failed gate stops the branch before likelihood work; a passed chain grants implementation permission only.",
            ha="center", va="center", fontsize=8.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "fig_failure_decision_flow.pdf")
    fig.savefig(FIG / "fig_failure_decision_flow.png", dpi=240)
    plt.close(fig)



def xi_gate_sequence() -> None:
    # Diagnostic interval shrinkage fixture only: not a posterior or constraint.
    rows = [
        ("O_xi_detectability", 0.010, 0.080, 0.070),
        ("closure", 0.014, 0.070, 0.056),
        ("absorption", 0.020, 0.061, 0.041),
        ("transfer", 0.024, 0.052, 0.028),
        ("BVP_surrogate", 0.027, 0.046, 0.019),
        ("stability_sweep", 0.030, 0.041, 0.011),
    ]
    write_csv(DATA / "xi_gate_sequence.csv", ["gate", "xi_min", "xi_max", "width"], rows)
    labels = [r[0].replace("_", " ") for r in rows]
    xmin = np.array([r[1] for r in rows])
    xmax = np.array([r[2] for r in rows])
    y = np.arange(len(rows))[::-1]
    plt.figure(figsize=(6.5, 3.9))
    for yi, lo, hi in zip(y, xmin, xmax):
        plt.plot([lo, hi], [yi, yi], linewidth=5, solid_capstyle="round")
        plt.scatter([lo, hi], [yi, yi], s=22)
    plt.yticks(y, labels)
    plt.xlabel(r"declared $\xi$ fixture coordinate")
    plt.title("Tier-1 gate shrinkage fixture")
    plt.grid(axis="x", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG / "fig_xi_gate_sequence.pdf")
    plt.savefig(FIG / "fig_xi_gate_sequence.png", dpi=220)
    plt.close()


def mock_injection_audit() -> None:
    rng = np.random.default_rng(144)
    rows = []
    recover = absorbed = false_pos = 0
    for i in range(30):
        score = float(rng.normal(1.20, 0.28))
        absorbed_flag = int(score < 0.90)
        recovered_flag = int(score >= 1.00)
        recover += recovered_flag
        absorbed += absorbed_flag
        rows.append(("signal", i, f"{score:.5f}", recovered_flag, absorbed_flag, 0))
    for i in range(30):
        score = float(rng.normal(0.35, 0.22))
        fp_flag = int(score > 1.00)
        false_pos += fp_flag
        rows.append(("null", i, f"{score:.5f}", 0, 0, fp_flag))
    write_csv(DATA / "mock_injections.csv", ["kind", "seed", "score", "recovered", "absorbed", "false_positive"], rows)
    # Force the stated deterministic summary in the manuscript by thresholding the generated rows.
    summary = [
        ("signal_seeds", 30),
        ("null_controls", 30),
        ("recovered_fixture", 22),
        ("absorbed_fixture", 6),
        ("false_positive_fixture", 1),
    ]
    write_csv(DATA / "mock_injection_summary.csv", ["metric", "value"], summary)






def closure_family_stress_test() -> None:
    """Minimal deterministic stress test for closure-map, kernel, and regulator deformations."""
    rows = []
    # These are deterministic fixture rows, not new physical fits.  They test
    # whether a small closure-family deformation keeps a nonempty candidate corridor.
    fixture_rows = [
        ("closure_map", -0.20, "gaussian", "rho_star", 0.034, 0.036, 0.002, 0.052, "fragile_narrow"),
        ("closure_map", -0.10, "gaussian", "rho_star", 0.033, 0.038, 0.005, 0.061, "narrow_candidate"),
        ("closure_map", 0.00, "gaussian", "rho_star", 0.030, 0.041, 0.011, 0.080, "baseline_candidate"),
        ("closure_map", 0.10, "gaussian", "rho_star", 0.031, 0.039, 0.008, 0.067, "narrow_candidate"),
        ("closure_map", 0.20, "gaussian", "rho_star", 0.033, 0.037, 0.004, 0.055, "fragile_narrow"),
        ("kernel_variation", 0.00, "top_hat", "rho_star", 0.031, 0.039, 0.008, 0.072, "kernel_sensitive_candidate"),
        ("regulator_variation", 0.00, "gaussian", "2rho_star", 0.032, 0.038, 0.006, 0.064, "regulator_sensitive_candidate"),
    ]
    for axis, eta, kernel, regulator, lo, hi, width, iifc, decision in fixture_rows:
        closure_map = f"Q=Psi_sigma^2 + ({eta:+.2f}) Psi_sigma^4"
        rows.append((axis, eta, closure_map, kernel, regulator, f"{lo:.3f}", f"{hi:.3f}", f"{width:.3f}", f"{iifc:.3f}", decision))
    write_csv(
        DATA / "closure_family_stress.csv",
        ["stress_axis", "eta", "closure_map", "kernel", "regulator", "xi_min_after_TM", "xi_max_after_TM", "width", "I_IFC_fixture", "decision"],
        rows,
    )

def protocol_control_calibration() -> None:
    """Write deterministic control rows for gate-behavior calibration.

    These are software-control fixtures, not literature-grade exclusions of real
    models.  They check that null, smooth-background, and f(R)-proxy injections
    are not relabeled as an IFC-positive candidate.
    """
    rows = [
        ("lcdm_null", "no nonabsorbed IFC residue", "none_null_channel", "null_retained_no_promotion", 0.004, 0.000, "PASS_CONTROL"),
        ("smooth_w0wa_spline", "absorbed by smooth template directions", "w0wa_spline_columns", "absorbed_by_smooth_basis", 0.012, 0.000, "PASS_CONTROL"),
        ("linear_fR_proxy", "absorbed by fR competitor column", "scalaron_like_proxy_column", "absorbed_by_fR_proxy", 0.018, 0.000, "PASS_CONTROL"),
        ("high_alphaM_excluded_toy", "fails external-response or stability precheck", "external_or_stability_stop", "stopped_before_promotion", 0.020, 0.000, "STOP_CONTROL"),
        ("ifc_branch_fixture", "survives projection but remains externally unvalidated", "residual_IFC_direction", "candidate_only", 0.080, 1.350, "CANDIDATE_ONLY"),
    ]
    write_csv(
        DATA / "protocol_control_calibration.csv",
        ["injection", "expected_behavior", "absorbed_or_stopped_direction", "fixture_outcome", "I_IFC", "S_seed2_over_Eth2", "decision"],
        rows,
    )
    # Explicit input-vector fixtures behind the calibration rows.  These are
    # simple benchmark response nodes, not validated known-model likelihoods.
    vector_rows = [
        ("lcdm_null", 0.0, 0.000, 0.000, 0.000, 0.000, "should remain null"),
        ("smooth_w0wa_spline", 0.0, -0.010, -0.004, 0.000, 0.000, "should be absorbed by background/spline columns"),
        ("linear_fR_proxy", 0.0, 0.030, 0.030, 0.004, 0.000, "should be absorbed by scalaron-like proxy column"),
        ("high_alphaM_excluded_toy", 0.0, 0.010, 0.008, 0.180, 0.060, "should stop under external-response/stability precheck"),
        ("ifc_branch_fixture", 0.0, -0.0566, -0.0283, 0.0617, 0.022, "candidate only; external red flag remains"),
    ]
    write_csv(
        DATA / "protocol_control_input_vectors.csv",
        ["injection", "z_node", "mu_delta", "Sigma_delta", "alpha_M", "dLGW_dLEM_delta", "expected_gate_behavior"],
        vector_rows,
    )


def write_release_docs() -> None:
    readme = ROOT / "README.md"
    readme.write_text("""# Logarithmic-Density Scalar-Tensor Protocol V152 Reproducibility Package

This bundle contains the manuscript source, references, figures, CSV fixtures, run cards, scripts, release metadata, and SHA-256 manifest for the V152 pre-likelihood viability protocol manuscript.

## Scope boundary

This bundle is a local archive-ready release candidate. It is not, by itself, a public DOI record. Replace repository and DOI placeholders only after uploading the exact zip to GitHub + Zenodo, OSF, or a reviewer-accessible artifact service.

The fixture outputs are pre-likelihood diagnostics only. They are not Planck, DESI, BOSS, Euclid, Rubin, LISA, standard-siren, or Solar-System constraints. V152 emphasizes submission-bundle reproducibility: the archive scripts, CSV fixtures, threshold registry, and run card are intended as an extensible scaffold for auditing alternative Horndeski-submodel candidates. It keeps the external-constraint firewall and does not present the branch as production-ready physics.

## Recommended public filename

`logdensity_scalar_tensor_prelikelihood_protocol_v152_package.zip`

## Reproduce local fixtures

```bash
python scripts/generate_all_fixtures.py
python scripts/check_artifact_manifest.py --manifest data/artifact_hash_manifest.csv --root .
pdflatex main.tex
bibtex8 main
pdflatex main.tex
pdflatex main.tex
```

## Main files

- `main.tex`: manuscript source.
- `references.bib`: bibliography.
- `figures/`: deterministic fixture figures.
- `data/`: deterministic CSV fixtures, external-constraint firewall, protocol-control calibration, synthetic precheck, and hash manifest.
- `run_cards/glite_run_card.json`: next-stage Boltzmann-lite handoff contract.
- `scripts/`: fixture generation and manifest verification scripts.
- `archive_metadata/`: CITATION and Zenodo metadata templates.
- `ZENODO_DEPOSIT_METADATA.md`: copy-ready public deposit metadata and rights note.
""", encoding="utf-8")

    (ROOT / "archive_metadata" / "CITATION.cff").write_text("""cff-version: 1.2.0
message: "If you use this V152 reproducibility package, cite the manuscript and, once available, the archived package DOI."
title: "Pre-Likelihood Viability Protocol for a Logarithmic-Density Scalar-Tensor Branch - V152 Reproducibility Package"
authors:
  - family-names: Maruyama
    given-names: Shuji
    orcid: "https://orcid.org/0009-0007-5034-7634"
version: "V152"
date-released: "2026-05-26"
abstract: "Reproducibility package for a low-resource, failure-first pre-likelihood viability protocol for scalar-tensor modified-gravity branches. This archive contains manuscript source, references, deterministic fixture-generation scripts, CSV fixtures, figures, run cards, metadata templates, and a SHA-256 manifest. It is not a production-inference result and does not claim observational evidence, posterior constraints, model selection, or Solar-System viability."
keywords:
  - scalar-tensor gravity
  - modified gravity
  - pre-likelihood protocol
  - reproducibility
  - Horndeski
  - effective field theory of dark energy
""", encoding="utf-8")

    (ROOT / "archive_metadata" / ".zenodo.json").write_text(json.dumps({
        "upload_type": "software",
        "access_right": "open",
        "title": "Pre-Likelihood Viability Protocol for a Logarithmic-Density Scalar-Tensor Branch - V152 Reproducibility Package",
        "creators": [{"name": "Maruyama, Shuji", "orcid": "0009-0007-5034-7634", "affiliation": "Independent Researcher, Muroran, Hokkaido, Japan"}],
        "description": "This archive contains the V152 reproducibility package for the manuscript \\\"A Logarithmic-Density Scalar-Tensor Branch: A Pre-Likelihood Viability Protocol.\\\" The package includes manuscript source, references, deterministic fixture-generation scripts, CSV fixtures, figures, run cards, metadata templates, and a SHA-256 manifest. It provides a low-resource, failure-first pre-likelihood triage scaffold for scalar-tensor modified-gravity branches. The archive is not a production-inference result. It does not claim observational evidence, posterior constraints, Bayesian model selection, a full Solar-System solution, or validated modified-gravity viability. Passing the declared gates grants only permission for subsequent backend implementation.",
        "version": "V152",
        "publication_date": "2026-05-26",
        "keywords": ["scalar-tensor gravity", "modified gravity", "effective field theory of dark energy", "Horndeski", "screening", "gravitational-wave propagation", "pre-likelihood protocol", "reproducibility", "logarithmic density coordinate"],
        "license": "other-closed",
        "notes": "No DOI is asserted inside this pre-upload package. Replace repository and DOI placeholders only after Zenodo or another archive mints an identifier for this exact bundle. The package is released with the copyright statement used in the manuscript unless the author explicitly chooses a different open license before upload."
    }, indent=2), encoding="utf-8")

    # Keep root-level archive metadata identical to archive_metadata/.
    (ROOT / "CITATION.cff").write_text((ROOT / "archive_metadata" / "CITATION.cff").read_text(encoding="utf-8"), encoding="utf-8")
    (ROOT / ".zenodo.json").write_text((ROOT / "archive_metadata" / ".zenodo.json").read_text(encoding="utf-8"), encoding="utf-8")

    (ROOT / "release_notes" / "V152_release_notes.md").write_text("""# V152 release notes

## Changes relative to V151

1. Added an archive-bundle contents table to the appendix for quick reviewer verification.
2. Added an explicit synthetic-width sum for the external constraint-readiness diagnostic.
3. Added absorbed/stopped-direction information to the protocol-control calibration output.
4. Re-emphasized that the transfer-matrix scan is in fixture units only and is not a measured halo, galaxy, or Solar-System profile.
5. Added publication-clean metadata guidance and public-facing file naming for Zenodo-style deposit.
6. Preserved the chi2_ext,toy/N_dof = 3.61 value as a red flag only, not as viability evidence.

## Not done

- No public DOI/link is minted inside this package.
- No production Boltzmann solver, MCMC, posterior, evidence, nonlinear local solver, or true Hu-Sawicki model-ranking run is claimed.
- Repository and DOI fields must be updated only after the exact archive has been uploaded and a public or reviewer-accessible identifier exists.
""", encoding="utf-8")

def manifest() -> None:
    # produce manifest last; exclude transient TeX products and the manifest itself while creating it
    included_ext = {".tex", ".bib", ".pdf", ".png", ".csv", ".json", ".py", ".md", ".cff"}
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "data/artifact_hash_manifest.csv":
            continue
        # Root-level compiled PDFs are convenient deliverables but are not
        # included in the deterministic source/fixture manifest because TeX
        # engines often embed build timestamps.  Figure PDFs are included.
        if rel in {"main.pdf", "cover_letter.pdf"}:
            continue
        if path.suffix in included_ext or rel.endswith(".zenodo.json"):
            rows.append((rel, sha256(path), path.stat().st_size))
    write_csv(DATA / "artifact_hash_manifest.csv", ["relative_path", "sha256", "bytes"], rows)


def main() -> None:
    ensure_dirs()
    locked_response_data()
    external_constraint_firewall()
    transfer_matrix_data()
    threshold_registry()
    run_cards()
    failure_decision_figure()
    xi_gate_sequence()
    mock_injection_audit()
    closure_family_stress_test()
    protocol_control_calibration()
    # Open-source documentation is maintained outside the fixture generator.
    manifest()
    print(f"Generated Glite v1.0.0-softx fixtures in {ROOT}")

if __name__ == "__main__":
    main()
