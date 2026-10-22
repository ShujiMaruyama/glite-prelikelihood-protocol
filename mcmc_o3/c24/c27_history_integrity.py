#!/usr/bin/env python3
"""c27 frozen-source audit of the full unfiltered native CLASS z/phi history.
Not a second Einstein--Boltzmann solver or observational inference.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from c23_freeze import verify
from c26_occupancy_gate import derive_initial_gate

HISTORY_SCHEMA="rims-c27-native-history-z-phi-v1"
GATE_SCHEMA="rims-c26-early-shell-occupancy-v1"

def canonical_json_bytes(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")

def make_history_payload(case,manifest,z_values,phi_values):
    z=[float(x) for x in z_values]
    phi=[float(x) for x in phi_values]
    if len(z)<2 or len(z)!=len(phi):
        raise ValueError("Missing/unequal native history z/phi rows")
    if not all(math.isfinite(v) for v in z+phi):
        raise ValueError("Nonfinite native z/phi row; never silently trim")
    return {"schema":HISTORY_SCHEMA,"source_freeze_hash":manifest["freeze_hash"],
        "case_id":case["id"],"case_sha256":case["input_sha256"],
        "native_history_rows":len(z),"z":z,"phi":phi,"synthetic_fixture":False}

def audit_history(manifest,native_receipt,history,history_raw_bytes):
    verify(manifest)
    case_id=native_receipt.get("id")
    cases=[c for c in manifest["cases"] if c["id"]==case_id]
    if len(cases)!=1:raise ValueError("Unknown frozen case")
    case=cases[0]
    expected_native={"schema":"rims-c23-native-background-attempt-v1",
        "id":case_id,"case_sha256":case["input_sha256"],
        "source_freeze_hash":manifest["freeze_hash"],
        "synthetic_fixture":False,"run_status":"solver_completed"}
    for k,v in expected_native.items():
        if native_receipt.get(k)!=v:
            raise ValueError("Invalid/unsuccessful native receipt: "+k)
    if not isinstance(history,dict):raise ValueError("No full native history")
    expected_history={"schema":HISTORY_SCHEMA,"case_id":case_id,
        "case_sha256":case["input_sha256"],
        "source_freeze_hash":manifest["freeze_hash"],"synthetic_fixture":False}
    for k,v in expected_history.items():
        if history.get(k)!=v:raise ValueError("History source mismatch: "+k)
    if not isinstance(native_receipt.get("c27_native_history_sha256"),str):
        raise ValueError("Missing saved native history SHA256")
    actual_hash=hashlib.sha256(history_raw_bytes).hexdigest()
    if actual_hash!=native_receipt["c27_native_history_sha256"]:
        raise ValueError("Native history SHA256 mismatch")
    if canonical_json_bytes(history)!=history_raw_bytes:
        raise ValueError("Native history is not canonical/byte-exact")
    z,phi=history.get("z"),history.get("phi")
    if not isinstance(z,list) or not isinstance(phi,list) or len(z)<2 or len(z)!=len(phi):
        raise ValueError("Invalid full native z/phi arrays")
    if history.get("native_history_rows")!=len(z) or native_receipt.get("native_z_total_rows")!=len(z):
        raise ValueError("Native history row count differs from original receipt")
    if not all(type(x) in (int,float) and math.isfinite(x) for x in z+phi):
        raise ValueError("Nonfinite/nonnumeric source history rows")
    gate=native_receipt.get("c26_initial_shell")
    if not isinstance(gate,dict) or gate.get("schema")!=GATE_SCHEMA:
        raise ValueError("Missing c26 source-linked occupancy result")
    reconstructed=derive_initial_gate(case,z,phi)
    if set(reconstructed)!=set(gate):
        raise ValueError("c26 registered decision keys were modified")
    for k,v in reconstructed.items():
        got=gate[k]
        if type(v) is float:
            if type(got) not in (float,int) or not math.isclose(got,v,abs_tol=1e-14,rel_tol=0):
                raise ValueError("Native earliest history decision modified: "+k)
        elif got!=v:
            raise ValueError("Native earliest history decision modified: "+k)
    return {"schema":"rims-c27-full-history-source-parity-v1",
        "case_id":case_id,"case_sha256":case["input_sha256"],
        "full_history_sha256":actual_hash,"history_rows":len(z),
        "recomputed_earliest_z":reconstructed["earliest_z"],
        "recomputed_earliest_phi":reconstructed["earliest_phi"],
        "recomputed_s_i":reconstructed["actual_s"],
        "c26_gate":reconstructed["gate"],
        "gate_pass":reconstructed["gate"]=="EARLY_OCCUPANCY_PASS",
        "independent_physical_solver":False,"posterior_or_observation":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--native-receipt",type=Path,required=True)
    p.add_argument("--native-history",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    m=json.loads(a.manifest.read_text())
    receipt=json.loads(a.native_receipt.read_text())
    raw=a.native_history.read_bytes()
    result=audit_history(m,receipt,json.loads(raw),raw)
    if a.out.exists():raise RuntimeError("Refusing to overwrite a c27 decision")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    if not result["gate_pass"]:raise SystemExit(2)
    print("c27 original full CLASS history identity PASS; no posterior claim")

if __name__=="__main__":main()
