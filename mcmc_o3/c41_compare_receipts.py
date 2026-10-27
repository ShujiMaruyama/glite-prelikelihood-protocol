#!/usr/bin/env python3
"""Independent cross-run comparison; sign sensitivity only, NOT root convergence."""
import argparse, hashlib, json, math
from pathlib import Path
from c41_precision_gate import EXPECTED_MODES,EXPECTED_CASE_SHA,EXPECTED_FREEZE,check_registry,sha256
# Independent re-parser of the historical C39 stderr record format.
PREFIX="RIMS_C39_TERMS_V1"
FIELDS=("a","phi","s","H","Vpp","rho_idm","mass_curvature","matter_term", "raw_meff2","h2","ratio","tolerance")
def parse_line(line):
    if not line.startswith(PREFIX+" "): raise ValueError("C39 marker missing")
    parts=line[len(PREFIX)+1:].split()
    if len(parts)!=len(FIELDS):raise ValueError("Wrong C39 record length")
    d={}
    for field,segment in zip(FIELDS,parts):
        key,eq,val=segment.partition("=")
        if eq!="=" or key!=field: raise ValueError("C39 field name/order mismatch")
        x=float(val)
        if not math.isfinite(x):raise ValueError("Nonfinite original source value")
        d[field]=x
    if not (0<d["a"]<1 and 0<d["s"]<1 and d["H"]>0 and d["h2"]>0
            and d["rho_idm"]>=0 and d["tolerance"]==1e-10):
        raise ValueError("Invalid original veto inputs")
    close=lambda a,b,scale: abs(a-b)<=5e-13*max(abs(scale),1e-300)
    if not close(d["h2"],d["H"]**2,d["h2"]):raise ValueError("C39 H² mismatch")
    t=3*d["rho_idm"]*d["mass_curvature"]
    if not close(t,d["matter_term"],t):raise ValueError("C39 matter-term mismatch")
    v=d["Vpp"]+d["matter_term"]
    if not close(v,d["raw_meff2"],max(abs(d["Vpp"]),abs(d["matter_term"]),abs(d["raw_meff2"]))):
        raise ValueError("C39 m_eff² decomposition mismatch")
    ratio=d["raw_meff2"]/d["h2"]
    if not close(ratio,d["ratio"],max(abs(d["ratio"]),abs(ratio))):
        raise ValueError("C39 mass/H² inconsistency")
    if not d["ratio"] < -d["tolerance"]:raise ValueError("No original native veto")
    d["Vpp_over_H2"]=d["Vpp"]/d["h2"]
    d["matter_over_H2"]=d["matter_term"]/d["h2"]
    d["source_cancellation_condition"]=(abs(d["Vpp"])+abs(d["matter_term"]))/abs(d["raw_meff2"]) if d["raw_meff2"]!=0 else None
    d["printed_veto_overshoot"]=-d["ratio"]-d["tolerance"]
    return d

BASELINE_SHA="08318f04e7d1e7a0edfa7a69eefd1c2dcf0c19c152ef4640db7b6b33df83e160"

def compare(baseline_record, receipts):
    check_registry()
    if len(receipts)!=2:raise ValueError("Exactly two separately authorized numerical settings required")
    if {r.get("run_mode") for r in receipts} != set(EXPECTED_MODES):
        raise ValueError("Missing/duplicate/unregistered precision settings")
    for r in receipts:
        mode=r["run_mode"]
        if (r.get("tol_background_integration") != EXPECTED_MODES[mode]
            or r.get("case")!="rims_002" or r.get("case_sha256")!=EXPECTED_CASE_SHA
            or r.get("freeze_sha256")!=EXPECTED_FREEZE or r.get("compute_calls_attempted")!=1
            or r.get("original_veto_tolerance") != 1e-10
            or r.get("retuned_shooting") is not False
            or r.get("status") != "SHOOTING_FAILED_WITH_VETO"
            or r.get("normalized_final_background_certified") is not False
            or r.get("numerical_convergence_demonstrated") is not False):
            raise ValueError("Provenance / physical input changed")
    records=[]
    for r in receipts:
        if (r.get("source_evidence_status")!="NATIVE_VETO_SOURCE_ARITHMETIC_CHECKED"
            or r.get("native_record_parse_error") is not None
            or r.get("all_veto_records_count") != len(r.get("all_veto_records",[]))
            or not r.get("all_veto_records")):
            raise ValueError("SOURCE_RECORD_UNAVAILABLE")
        for d in r["all_veto_records"]:
            if not all(math.isfinite(d.get(k,float("nan"))) for k in ("a","s","ratio","Vpp_over_H2","matter_over_H2")):
                raise ValueError("Nonfinite native source record")
            if not (0<d["a"]<1 and 0<d["s"]<1 and d["ratio"] < -1e-10
                    and d["matter_over_H2"]<0 and d["tolerance"]==1e-10):
                raise ValueError("Native physical veto/sign consistency failed")
        records.append(r["all_veto_records"])
    if baseline_record["ratio"] >= -1e-10 or baseline_record["matter_term"]>=0:
        raise ValueError("C39 original reference was not a negative coupling term veto")
    # first *reported* failure, not a continuous accepted-step root bracket
    src=next(x for x in receipts if x["run_mode"]=="tight10-one")["all_veto_records"][0]
    dst=next(x for x in receipts if x["run_mode"]=="tight100-one")["all_veto_records"][0]
    return {"schema":"RIMS_C41_SOURCE_SIGN_SENSITIVITY_ONLY_V1",
            "status":"SAME_NEGATIVE_SOURCE_SIGN_NOT_CONVERGED",
            "no_root_bracket_captured":True,
            "integration_convergence_proven":False,
            "background_viability_proven":False,
            "source_comparisons":{
                "baseline_c39_a":baseline_record["a"],
                "tight10_first_veto_a":src["a"],
                "tight100_first_veto_a":dst["a"],
                "tight10_first_veto_ratio":src["ratio"],
                "tight100_first_veto_ratio":dst["ratio"],
                "abs_delta_first_veto_lna":abs(math.log(src["a"])-math.log(dst["a"])),
                "abs_delta_first_veto_ratio":abs(src["ratio"]-dst["ratio"]),
                "interpretation":"FIRST TRIGGERED NUMERICAL EVALUATIONS, not accepted-step root samples"},
            "claim_boundary":"A sign check on two independent precision calls is not a numerical convergence or physical-instability theorem."}

def independently_validate_stderr(receipt, stderr_path):
    raw=Path(stderr_path).read_bytes()
    if sha256(raw)!=receipt.get("native_stderr_sha256"):
        raise ValueError("Raw native stderr SHA256 mismatch")
    lines=raw.decode("utf-8",errors="strict").splitlines()
    native=[parse_line(line) for line in lines if line.startswith(PREFIX+" ")]
    if not native or native != receipt.get("all_veto_records"):
        raise ValueError("Independent raw diagnostic/receipt mismatch")
    return native


def main():
    p=argparse.ArgumentParser();p.add_argument("--c39",required=True)
    p.add_argument("--tight10",required=True);p.add_argument("--tight100",required=True)
    p.add_argument("--tight10-stderr",required=True);p.add_argument("--tight100-stderr",required=True)
    p.add_argument("--out",required=True);a=p.parse_args()
    b=json.loads(Path(a.c39).read_text())["veto_records_ALL"][0]
    rs=[json.loads(Path(q).read_text()) for q in (a.tight10,a.tight100)]
    independently_validate_stderr(rs[0],a.tight10_stderr)
    independently_validate_stderr(rs[1],a.tight100_stderr)
    obj=compare(b,rs)
    out=Path(a.out)
    if out.exists():raise FileExistsError("Do not overwrite audit output")
    out.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(obj["status"],"C41 convergence NOT established")
if __name__=="__main__":main()
