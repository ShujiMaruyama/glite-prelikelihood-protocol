#!/usr/bin/env python3
"""Exact analytic input-only RIMS c34 gates; no CLASS / no observation / no MCMC."""
import argparse,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
from c23_freeze import build_manifest,verify

def locked_gates(manifest):
    verify(manifest)
    rows=[]
    for c in manifest["cases"]:
        a=float(c["alpha_U"]);s=float(c["s_i"])
        if not(a>0 and 0<s<1):raise ValueError("Outside analytically certified s/alpha branch")
        beta=a*(1-s)
        curvature=a*a*(1-s)*(1-3*s)
        sign="ZERO" if abs(s-1/3)<1e-14 else ("POSITIVE" if curvature>0 else "NEGATIVE")
        rows.append({
            "case_id":c["id"],"case_sha256":c["input_sha256"],
            "potential":c["potential"],"alpha_U":a,
            "omega_phi0":c["omega_phi0"],"s_i":s,
            "beta_i_from_source_mass_law":beta,
            "mass_second_derivative_over_m":curvature,
            "mass_curvature_sign":sign,
            "conditional_Gamma_max_exclusive":2*a*a,
            "actual_background_ran":c["id"]=="rims_000",
            "transfer_or_observation_computed":False})
    counts={k:sum(v["mass_curvature_sign"]==k for v in rows)
            for k in ("POSITIVE","ZERO","NEGATIVE")}
    if counts!={"POSITIVE":27,"ZERO":27,"NEGATIVE":27}:
        raise ValueError("Source-sign partition changed")
    return {"schema":"rims-c34-analytic-input-not-81-physical-solves-v1",
        "frozen_sha256":manifest["freeze_hash"],"case_count":81,
        "source_gates":{
            "beta":"alpha_U*(1-s)",
            "dbeta_dphi":"-2*beta*(alpha_U-beta)",
            "mass_curvature":"alpha_U^2*(1-s)*(1-3*s)",
            "mass_curvature_zero_at_s_one_third":True,
            "canonical_QS_Gamma_strict_upper":"2*alpha_U^2 (conditional)"},
        "sign_counts":counts,"cases":rows,
        "physical_backgrounds_executed_prior_to_c34":1,
        "unexecuted_physical_cases":80,
        "production_inference":False,"any_observational_detection":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.output.exists():raise SystemExit("Refusing to overwrite source-locked result")
    result=locked_gates(build_manifest())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("81 theoretical inputs, 27/27/27 signs; ONLY ONE prior native CLASS background")
if __name__=="__main__":main()
