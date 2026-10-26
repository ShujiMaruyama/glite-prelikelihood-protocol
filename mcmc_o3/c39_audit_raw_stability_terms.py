#!/usr/bin/env python3
"""Independent C39 source-level rejection decomposition (no CLASS execution).

Reads original first-compute c37-style receipt, original stderr and C39
source-change lock. Never interprets reproduced solver failure as viability.
"""
import argparse,hashlib,json,math
from pathlib import Path

FIELDS=("a","phi","s","H","Vpp","rho_idm","mass_curvature","matter_term",
        "raw_meff2","h2","ratio","tolerance")
PREFIX="RIMS_C39_TERMS_V1"
CASE_SHA="9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284"
FREEZE="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
PRIOR_PREFIX_SHA="eb8b7a6e5e52cec209141a7c359c5e6947b5479bb076df592558853b41b4beaf"

def close_decomp(x,y,scale):
    return abs(x-y) <= 5e-13*max(abs(scale),1e-300)

def parse_line(line):
    if not line.startswith(PREFIX+" "):
        raise ValueError("Unknown native diagnostic marker")
    pairs=line[len(PREFIX)+1:].split()
    if len(pairs)!=len(FIELDS):raise ValueError("Incomplete native C diagnostic line")
    d={}
    for field,pair in zip(FIELDS,pairs):
        key,sep,value=pair.partition("=")
        if sep!="=" or key!=field:raise ValueError("Unexpected native field order")
        n=float(value)
        if not math.isfinite(n):raise ValueError("Nonfinite physical diagnostic "+field)
        d[field]=n
    if not (0<d["a"]<1 and 0<d["s"]<1 and d["H"]>0 and d["h2"]>0
            and d["rho_idm"]>=0 and d["tolerance"]==1e-10):
        raise ValueError("Unphysical or retuned native veto inputs")
    if not close_decomp(d["h2"],d["H"]**2,d["h2"]):
        raise ValueError("H² mismatch")
    term=3*d["rho_idm"]*d["mass_curvature"]
    if not close_decomp(term,d["matter_term"],term):
        raise ValueError("Matter term mismatch")
    combined=d["Vpp"]+d["matter_term"]
    scale=max(abs(d["Vpp"]),abs(d["matter_term"]),abs(d["raw_meff2"]))
    if not close_decomp(combined,d["raw_meff2"],scale):
        raise ValueError("Vpp+matter source sum disagrees with native mass")
    ratio=d["raw_meff2"]/d["h2"]
    if not close_decomp(ratio,d["ratio"],max(abs(d["ratio"]),abs(ratio))):
        raise ValueError("Native m_eff²/H² mismatch")
    if not d["ratio"] < -d["tolerance"]:
        raise ValueError("C39 diagnostic did not observe an actual original veto")
    d["Vpp_over_H2"]=d["Vpp"]/d["h2"]
    d["matter_over_H2"]=d["matter_term"]/d["h2"]
    d["source_cancellation_condition"]=(
        (abs(d["Vpp"])+abs(d["matter_term"]))/abs(d["raw_meff2"])
        if d["raw_meff2"]!=0 else None)
    d["printed_veto_overshoot"]=-d["ratio"]-d["tolerance"]
    return d

def audit(stderr,receipt,source):
    src=json.loads(Path(source).read_text())
    r=json.loads(Path(receipt).read_text())
    if (src.get("schema")!="rims-c39-source-overlay-v1" or
        src.get("source_sha256_before_overlay")!=src.get("reconstruction_original_sha256") or
        src.get("veto_gate_preserved") is not True or
        src.get("changed_tolerance") is not False or
        src.get("changed_scientific_parameters") is not False):
        raise ValueError("Changed original RIMS native CLASS physics gate")
    if (r.get("case_id")!="rims_002" or
        r.get("case_sha256")!=CASE_SHA or r.get("freeze_sha256")!=FREEZE or
        r.get("compute_attempts")!=1 or
        r.get("normalization_or_final_background_certified") is not False or
        r.get("status")!="ORIGINAL_SHOOTING_FAILURE_REPRODUCED" or
        r.get("c35_failure_prefix_matches") is not True or
        r.get("c35_original_truncated_error_prefix_sha256")!=PRIOR_PREFIX_SHA):
        raise ValueError("Native first failed compute / historic c35 identity not proven")
    b=Path(stderr).read_bytes()
    lines=b.decode("utf-8").splitlines()
    candidates=[s for s in lines if s.startswith(PREFIX+" ")]
    if not candidates:raise ValueError("No native Vpp/matter diagnostic; no decomposition claim")
    parsed=[parse_line(s) for s in candidates]
    return {"schema":"rims-c39-native-raw-source-term-audit-v1",
            "original_prior_frozen_case":"rims_002","new_unique_parameter_cases":0,
            "underlying_first_native_compute":"solver_failed",
            "old_shooting_failure_reproduced":True,
            "source_change_sha256_before":src["source_sha256_before_overlay"],
            "source_change_sha256_after":src["source_sha256_after_overlay"],
            "native_stderr_sha256":hashlib.sha256(b).hexdigest(),
            "physical_trigger_count":len(parsed),
            "native_veto_records_all":parsed,
            "native_solver_viability_demonstrated":False,
            "numerical_convergence_demonstrated":False,
            "MCMC_or_likelihood":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stderr",type=Path,required=True)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--source-audit",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Refuse to overwrite prior C39 physical audit")
    v=audit(a.stderr,a.receipt,a.source_audit)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("C39_VETO_TERMS_SOURCE_LOCKED",v["physical_trigger_count"],
          "physical solver still failed")
if __name__=="__main__":main()
