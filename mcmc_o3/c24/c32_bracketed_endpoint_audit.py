#!/usr/bin/env python3
"""RIMS c32: source-bound z=3 bracket validation for one real CLASS background.

This is a native sampled-grid / bracketed-endpoint test. It NEVER certifies
continuum tachyon freedom, independent Einstein--Boltzmann parity or observation.
The c24 PHYSICAL_REJECT result remains intact; c32 is a SEPARATE outcome.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from c23_freeze import verify
from c24_audit import audit as legacy_audit
from c26_native_receipt_bridge import audit_native_receipt
from c27_history_integrity import audit_history

GAP_MAX=0.01
M2_MIN=-1.0e-10
RATIO_RTOL=5e-8
RATIO_ATOL=1e-10
STATUS="NATIVE_GRID_BRACKETED_SAMPLED_PASS"

def safe(x):
    return type(x) in (int,float) and math.isfinite(float(x))

def logistic(t):
    if t>=0:return 1./(1.+math.exp(-t))
    q=math.exp(t);return q/(1.+q)

def close(a,b,atol=1e-12,rtol=2e-10):
    return math.isclose(float(a),float(b),abs_tol=atol,rel_tol=rtol)

def bracket_audit(m,root,case_id="rims_000"):
    """Compute a new conditional status; never alter c24 legacy archive."""
    verify(m)
    root=Path(root)
    rows=[x for x in m["cases"] if x["id"]==case_id]
    if len(rows)!=1:raise ValueError("Unfrozen or duplicated case ID")
    case=rows[0]
    folder=root/case_id
    receipt=json.loads((folder/"receipt.json").read_text())
    raw=(folder/"c27_full_history_z_phi.json").read_bytes()
    history=json.loads(raw)
    old=legacy_audit(m,root)
    byid=[x for x in old["cases"] if x["id"]==case_id]
    if len(byid)!=1:raise ValueError("Legacy case absent")
    oldcase=byid[0]
    if oldcase["status"] not in ("PHYSICAL_REJECT","PHYSICAL_VALID"):
        raise ValueError("Legacy native provenance or solver failed: "+oldcase["status"])
    if oldcase["status"]=="PHYSICAL_REJECT" and oldcase["issues"]!=["z_0to3_coverage_failed"]:
        raise ValueError("Other physical veto MUST NOT be overridden: "+str(oldcase["issues"]))
    if old["statuses"].get("NO_RECEIPT")!=80:
        raise ValueError("Single-case protocol altered / other 80 not preserved")
    if receipt.get("code_version")!="c32_native_background_v7":
        raise ValueError("Wrong native runner version; old artifact is not a c32 physical PASS")
    source=audit_history(m,receipt,history,raw)
    if not source["gate_pass"]:raise ValueError("Full native history or initial occupancy failed")
    c26=audit_native_receipt(m,receipt)
    if not c26["gate_pass"]:raise ValueError("Independent initial occupancy failed")
    b=receipt.get("c32_native_z3_bracket")
    if not isinstance(b,dict) or b.get("schema")!="rims-c32-native-z3-bracket-v1":
        raise ValueError("Missing native full-mass z3 source bracket")
    if b.get("case_sha256")!=case["input_sha256"] or b.get("exact_native_z3_recorded") is not False:
        raise ValueError("Bracket identity or exact/native interpolation label changed")
    if b.get("source")!="raw_final_Class.get_background_before_z_filter":
        raise ValueError("Untrusted source for bracket")
    z_all=history["z"];phi_all=history["phi"]
    if len(z_all)!=receipt["native_z_total_rows"]:
        raise ValueError("History length mismatch")
    s2=case["alpha_U"];pt=case["phi_t"]
    for name in ("left","right"):
        e=b.get(name)
        if not isinstance(e,dict):raise ValueError("Missing native "+name+" row")
        idx=e.get("row_index")
        if type(idx) is not int or not 0<=idx<len(z_all):
            raise ValueError("Out of-range native row index")
        for field in ("z","phi","s","rims_mratio","rims_stab","rims_meff2","H_Mpc_inverse"):
            if not safe(e.get(field)):raise ValueError("Nonfinite native bracket field: "+field)
        if not close(e["z"],z_all[idx],atol=1e-12,rtol=0):
            raise ValueError("Native z bracket not source anchored")
        if not close(e["phi"],phi_all[idx],atol=1e-12,rtol=0):
            raise ValueError("Native phi bracket not source anchored")
        if not close(e["s"],logistic(2*s2*(e["phi"]-pt)),atol=1e-13,rtol=0):
            raise ValueError("Bracket occupancy mass map mismatch")
        if e["H_Mpc_inverse"]<=0:raise ValueError("Nonpositive H in native bracket")
        if not math.isclose(e["rims_stab"],e["rims_meff2"]/e["H_Mpc_inverse"]**2,
                            rel_tol=RATIO_RTOL,abs_tol=RATIO_ATOL):
            raise ValueError("Native bracket effective-mass/H² mismatch")
        if e["rims_stab"]<M2_MIN:
            raise ValueError("Native bracket contains unstable mass squared")
    lo=b["left"];hi=b["right"]
    z1=float(lo["z"]);z2=float(hi["z"])
    if not(z1<3<z2 and 0<z2-z1<=GAP_MAX):
        raise ValueError("Native z3 bracket missing or too coarse")
    if not close(b.get("gap"),z2-z1,atol=1e-12,rtol=0):
        raise ValueError("Native gap metadata altered")
    # These must be the nearest two source points, not cherry-picked points.
    import bisect
    pairs=sorted((zz,i) for i,zz in enumerate(z_all))
    zz=[x[0] for x in pairs];at=bisect.bisect_left(zz,3.)
    if at<=0 or at>=len(pairs):
        raise ValueError("Raw source history does not straddle z3")
    if (pairs[at-1][1]!=lo["row_index"] or pairs[at][1]!=hi["row_index"]):
        raise ValueError("Nonadjacent or cherry-picked native z3 bracket")
    sample=receipt.get("background")
    if not isinstance(sample,list) or len(sample)<2:
        raise ValueError("No native sampled grid")
    if not close(sample[-1]["z"],z1,atol=1e-12,rtol=0):
        raise ValueError("Lower bracket not last z<=3 sampled row")
    if not close(sample[-1]["m2_over_H2"],lo["rims_stab"],atol=1e-12,rtol=1e-10):
        raise ValueError("Lower bracket stability differs from source sampled row")
    if not close(sample[-1]["s"],lo["s"],atol=1e-12,rtol=1e-10):
        raise ValueError("Lower bracket occupancy differs from source sampled row")
    # Keep endpoint numbers separate: this is a LINEAR DIAGNOSTIC, NOT a CLASS z=3 solve.
    t=(3.-z1)/(z2-z1)
    m3=(1-t)*lo["rims_stab"]+t*hi["rims_stab"]
    phi3=(1-t)*lo["phi"]+t*hi["phi"]
    out={"schema":"rims-c32-source-bound-grid-bracket-v1",
         "source_case_id":case_id,"source_case_sha256":case["input_sha256"],
         "frozen_grid_sha256":m["freeze_hash"],
         "original_legacy_audit_status":oldcase["status"],
         "original_legacy_audit_issues":oldcase["issues"],
         "c26_initial_occupancy_gate":c26["gate"],
         "c27_full_history_integrity_gate":source["c26_gate"],
         "c32_status":STATUS,
         "native_z_bracket":[z1,z2],"native_gap":z2-z1,
         "native_m2_H2_bracket":[lo["rims_stab"],hi["rims_stab"]],
         "sampled_z0_to3_native_m2_H2_min":min(row["m2_over_H2"] for row in sample),
         "z3_linear_interpolation_diagnostic_only":{
             "m2_over_H2":m3,"phi":phi3,
             "s":logistic(2*s2*(phi3-pt)),
             "is_exact_class_z3":False,
             "not_continuum_stability_proof":True},
         "no_second_solver_or_observational_inference":True,
         "other_80_cases_unattempted":True,"production_posterior":False}
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--receipts",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--one",default="rims_000")
    a=p.parse_args()
    m=json.loads(a.manifest.read_text())
    d=bracket_audit(m,a.receipts,a.one)
    if a.out.exists():raise RuntimeError("Do not overwrite c32 audit")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(STATUS,"original_legacy_status",d["original_legacy_audit_status"])
if __name__=="__main__":main()
