"""c25 synthetic receipt edge-cases; no physical RIMS CLASS result is asserted."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import c23_freeze as frozen
import c24_native_background as native
import c24_audit as audit

class GuardClass:
    mode="ok"
    def __init__(self):
        if self.mode=="constructor":raise RuntimeError("synthetic constructor failure")
    def set(self, **kwargs):
        if self.mode=="set":raise RuntimeError("synthetic CLASS.set failure")
    def compute(self):
        if self.mode=="compute":raise RuntimeError("synthetic CLASS.compute failure")
    def get_background(self):
        if self.mode=="extract":raise RuntimeError("synthetic get_background failure")
        return {"z":[0.,1.,2.,3.],
                "phi_scf":[4.44,4.43,4.42,4.41],
                "rims_mratio":[1.,1.,1.,1.],
                "rims_m2eff_over_H2":[1.,1.,1.,1.]}
    def empty(self):pass

class GuardModule:
    Class=GuardClass
    __file__=__file__

def exercise(tmp_path,mode):
    GuardClass.mode=mode
    manifest=frozen.build_manifest()
    result=native.run_case(GuardModule,manifest["cases"][0],manifest,tmp_path)
    reviewed=audit.audit(manifest,tmp_path)["cases"][0]
    events=[json.loads(s) for s in (tmp_path/"rims_000"/"native_compute.log").read_text().splitlines()]
    return result,reviewed,events

def test_constructor_exception_preserved_as_solver_failure(tmp_path):
    r,a,e=exercise(tmp_path,"constructor")
    assert r["native_compute_attempts"]==0
    assert a["status"]=="SOLVER_FAILED"
    assert any(x.get("stage")=="Class_constructor" for x in e)

def test_class_set_failure_not_falsely_recorded_as_compute(tmp_path):
    r,a,e=exercise(tmp_path,"set")
    assert r["native_compute_attempts"]==0
    assert a["status"]=="SOLVER_FAILED"
    assert any(x.get("stage")=="Class.set" for x in e)
    assert not any(x["event"]=="native_compute_start" for x in e)

def test_native_compute_failure_exactly_one_terminal_event(tmp_path):
    r,a,e=exercise(tmp_path,"compute")
    assert r["native_compute_attempts"]==1
    assert a["status"]=="SOLVER_FAILED"
    assert sum(x["event"]=="native_compute_start" for x in e)==1
    assert sum(x["event"]=="native_compute_exception" for x in e)==1
    assert not any(x["event"]=="native_compute_end" for x in e)

def test_postcompute_background_extraction_failure_separate(tmp_path):
    r,a,e=exercise(tmp_path,"extract")
    assert r["native_compute_attempts"]==1
    assert a["status"]=="SOLVER_FAILED"
    assert sum(x["event"]=="native_compute_end" for x in e)==1
    assert sum(x["event"]=="native_extract_exception" for x in e)==1
    assert not any(x["event"]=="native_compute_exception" for x in e)

def test_logged_setup_fail_event_cannot_be_removed_undetected(tmp_path):
    r,a,e=exercise(tmp_path,"set")
    log=tmp_path/"rims_000"/"native_compute.log"
    log.write_text("".join(json.dumps(x)+"\n" for x in e if x["event"]!="native_setup_exception"))
    receipt=tmp_path/"rims_000"/"receipt.json"
    from hashlib import sha256
    obj=json.loads(receipt.read_text());obj["log_sha256"]=sha256(log.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(obj))
    audited=audit.audit(frozen.build_manifest(),tmp_path)["cases"][0]
    assert audited["status"]=="PROVENANCE_GATE_FAIL"
    assert "zero_native_calls_without_recorded_setup_failure" in audited["issues"]

def test_complete_synthetic_background_still_valid_not_81(tmp_path):
    r,a,e=exercise(tmp_path,"ok")
    full=audit.audit(frozen.build_manifest(),tmp_path)
    assert a["status"]=="PHYSICAL_VALID"
    assert full["all_81_documented"] is False
    assert full["all_81_physically_valid_under_declared_background_gates"] is False


def _rebuild_receipt_hash(tmp_path,events):
    from hashlib import sha256
    log=tmp_path/"rims_000"/"native_compute.log"
    log.write_text(chr(10).join(json.dumps(x,sort_keys=True) for x in events)+chr(10))
    receipt=tmp_path/"rims_000"/"receipt.json"
    payload=json.loads(receipt.read_text())
    payload["log_sha256"]=sha256(log.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(payload))

def test_falsified_compute_end_success_flag_is_detected(tmp_path):
    r,a,e=exercise(tmp_path,"ok")
    for x in e:
        if x["event"]=="native_compute_end":
            x["success"]=False
            break
    _rebuild_receipt_hash(tmp_path,e)
    reviewed=audit.audit(frozen.build_manifest(),tmp_path)["cases"][0]
    assert reviewed["status"]=="PROVENANCE_GATE_FAIL"
    assert "native_compute_end_without_success_flag" in reviewed["issues"]

def test_duplicate_background_extract_exception_is_detected(tmp_path):
    r,a,e=exercise(tmp_path,"extract")
    original=next(x for x in e if x["event"]=="native_extract_exception")
    e.append(dict(original))
    _rebuild_receipt_hash(tmp_path,e)
    reviewed=audit.audit(frozen.build_manifest(),tmp_path)["cases"][0]
    assert reviewed["status"]=="PROVENANCE_GATE_FAIL"
    assert "duplicate_background_extract_exception" in reviewed["issues"]


def test_ideal_design_ceiling_is_computed_only_for_physical_valid(tmp_path):
    import math
    r,a,e=exercise(tmp_path,"ok")
    assert a["status"]=="PHYSICAL_VALID"
    cap=a["idealized_three_node_expected_5sigma_50pct_power_relative_F_error_ceiling"]
    normalized=a["fractional_W_sagitta"]
    assert cap>0 and math.isfinite(cap)
    assert math.isclose(cap,2*normalized/(5*math.sqrt(1.5)),rel_tol=1e-12)
    assert a["idealized_design_only"] is True

def test_ideal_design_ceiling_not_released_for_failed_native_case(tmp_path):
    r,a,e=exercise(tmp_path,"extract")
    assert a["status"]=="SOLVER_FAILED"
    assert "idealized_three_node_expected_5sigma_50pct_power_relative_F_error_ceiling" not in a
