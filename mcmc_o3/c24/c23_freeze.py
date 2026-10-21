#!/usr/bin/env python3
"""Frozen 81 RIMS backgrounds. Values fixed 2026-10-20, not an old executed scan."""
import argparse,hashlib,itertools,json,math
from pathlib import Path
FAMILIES={
    "exponential":{"scf_polynomial_power":0,"scf_A":0.0,"scf_B":0.0},
    "quadratic":{"scf_polynomial_power":2,"scf_A":1.0,"scf_B":4.44},
    "quartic":{"scf_polynomial_power":4,"scf_A":1.0,"scf_B":4.44},
}
ALPHAS=[0.01,0.05,0.10]
OMEGAS=[0.001,0.03,0.09]
OCCUPANCIES=[0.10,1/3,0.65]
UPSTREAM="e85808324f51fc694d12e3ed7439552a3c3f9540"
PATCHES=["6bb31d11bf17c300666a2c2f2b79cac42aeef0a99e9ea53cf3db87403592ad74","c322fb05b7414be9f88cf90ff0580694e7677c8da91d78a5480ea9cf10f2b8dc"]
FROZEN_HASH="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
def stable(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(o):return hashlib.sha256(stable(o).encode()).hexdigest()
def build_manifest():
    rows=[]
    for family,alpha,omega,si in itertools.product(FAMILIES,ALPHAS,OMEGAS,OCCUPANCIES):
        i=len(rows);phi_i=4.44
        u=math.log(si/(1-si));phi_t=phi_i-u/(2*alpha);pot=FAMILIES[family]
        scf=[5.0,pot['scf_polynomial_power'],pot['scf_A'],pot['scf_B'],phi_i,0.0]
        row={"id":f"rims_{i:03d}","potential":family,"alpha_U":alpha,"omega_phi0":omega,
             "s_i":si,"u_i":u,"phi_t":phi_t,"phi_i":phi_i,
             "scf_parameters":", ".join(f"{float(v):.16g}" for v in scf),
             "fixed_background":{"H0":68.02,"omega_b":0.02246,"omega_dm":0.11852,
                                 "inert_fraction":0.1,"tau_reio":0.0544,"N_ur":3.044},
             "redshift_domain":[0.0,3.0],"validity_policy":"all_attempts_retained_no_cherry_picking"}
        row["input_sha256"]=digest(row);rows.append(row)
    assert len(rows)==81 and len({x["input_sha256"] for x in rows})==81
    base={"schema":"rims-c23-81-physical-attempt-plan-v1","freeze_date":"2026-10-20",
          "status":"INPUT_DESIGN_ONLY_NO_PHYSICAL_TRAJECTORIES",
          "grid_levels":{"potential":list(FAMILIES),"alpha_U":ALPHAS,"omega_phi0":OMEGAS,"s_i":OCCUPANCIES},
          "fixed_potential_rule":"CLASS polynomial-times-exponential: V=V_p exp(-5 phi), centered A=1,B=phi_i for quadratic/quartic",
          "Class_upstream_commit":UPSTREAM,"RIMS_patch_sha256":PATCHES,
          "model_assumptions":{"conserved_dark_number":True,"one_canonical_scalar":True,"separate_inert_dark_fraction":0.1,"target_is_81_backgrounds_not_CMB_likelihood":True},
          "run_policy":{"manual_dispatch_only":True,"automatic_follow_on":False,"MCMC":False,"retain_failed_attempts":True,"no_first_success_selection":True},
          "production_gate":{"GetDist_Rminus1_strict_lt":0.01,"min_headline_ESS_ge":1000},
          "cases":rows}
    base["freeze_hash"]=digest(base)
    if base["freeze_hash"]!=FROZEN_HASH:raise RuntimeError("frozen c23 81-grid hash mismatched: fail closed")
    return base
def verify(m):
    if m!=build_manifest():raise ValueError("c23 frozen 81-grid differs")
    return True
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    d=build_manifest()
    if a.output.exists():
        if json.loads(a.output.read_text())!=d:raise RuntimeError("refusing to overwrite different manifest")
    else:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("STATIC_81_INPUTS_ONLY",d["freeze_hash"])
