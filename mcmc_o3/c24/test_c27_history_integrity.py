"""Synthetic-only c27 checks: full unfiltered history must match native source decision."""
import hashlib,json,sys,math
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c23_freeze import build_manifest
from c26_occupancy_gate import derive_initial_gate
from c27_history_integrity import make_history_payload,canonical_json_bytes,audit_history

def valid_case():
    m=build_manifest();c=m["cases"][0]
    z=[0.,1.,3.,1100.,2400.,3300.]
    phi=[4.5,4.49,4.48,4.46,4.45,c["phi_i"]]
    h=make_history_payload(c,m,z,phi);raw=canonical_json_bytes(h)
    receipt={"schema":"rims-c23-native-background-attempt-v1",
      "id":c["id"],"case_sha256":c["input_sha256"],
      "source_freeze_hash":m["freeze_hash"],"synthetic_fixture":False,
      "run_status":"solver_completed","native_z_total_rows":len(z),
      "c26_initial_shell":derive_initial_gate(c,z,phi),
      "c27_native_history_sha256":hashlib.sha256(raw).hexdigest()}
    return m,receipt,h,raw

def test_valid_history_and_gate():
    m,r,h,raw=valid_case()
    a=audit_history(m,r,h,raw)
    assert a["gate_pass"] and a["history_rows"]==6
    assert not a["independent_physical_solver"]

def test_insufficient_early_history_is_not_a_pass():
    m,r,h,raw=valid_case()
    h=make_history_payload(m["cases"][0],m,[0.,10.,99.],[4.,4.1,m["cases"][0]["phi_i"]])
    raw=canonical_json_bytes(h)
    r["native_z_total_rows"]=3
    r["c26_initial_shell"]=derive_initial_gate(m["cases"][0],h["z"],h["phi"])
    r["c27_native_history_sha256"]=hashlib.sha256(raw).hexdigest()
    a=audit_history(m,r,h,raw)
    assert a["c26_gate"]=="UNRESOLVED_EARLY_EPOCH" and not a["gate_pass"]

def test_wrong_initial_history_index():
    m,r,h,raw=valid_case();r["c26_initial_shell"]["initial_history_index"]=4
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_tampered_earliest_phi():
    m,r,h,raw=valid_case();r["c26_initial_shell"]["earliest_phi"]+=0.2
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_tampered_earliest_redshift():
    m,r,h,raw=valid_case();r["c26_initial_shell"]["earliest_z"]=2200.
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_deleted_earliest_history_row():
    m,r,h,raw=valid_case()
    h["z"].pop();h["phi"].pop()
    with pytest.raises(ValueError):audit_history(m,r,h,canonical_json_bytes(h))

def test_rehashed_shorter_history_with_old_count():
    m,r,h,raw=valid_case()
    h["z"].pop();h["phi"].pop();h["native_history_rows"]=5
    raw=canonical_json_bytes(h);r["c27_native_history_sha256"]=hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_swapped_source_case_hash():
    m,r,h,raw=valid_case()
    h["case_sha256"]="0"*64;raw=canonical_json_bytes(h)
    r["c27_native_history_sha256"]=hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_changed_c26_frozen_threshold():
    m,r,h,raw=valid_case()
    r["c26_initial_shell"]["absolute_s_tolerance"]=1.
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_failed_solver_not_promoted():
    m,r,h,raw=valid_case();r["run_status"]="solver_error"
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_noncanonical_history_even_with_matching_sha():
    m,r,h,raw=valid_case()
    raw=json.dumps(h).encode()+b"\n"
    r["c27_native_history_sha256"]=hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_nonfinite_history_rejected():
    m,r,h,raw=valid_case()
    h["phi"][3]=float("nan")
    with pytest.raises(ValueError):canonical_json_bytes(h)

def test_frozen_81_grid_mutation_rejected():
    m,r,h,raw=valid_case()
    assert len(m["cases"])==81
    m["cases"][0]["s_i"]=0.2
    with pytest.raises(ValueError):audit_history(m,r,h,raw)

def test_missing_history_hash():
    m,r,h,raw=valid_case();r.pop("c27_native_history_sha256")
    with pytest.raises(ValueError):audit_history(m,r,h,raw)
