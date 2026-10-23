"""Synthetic-only c32 FULL source-bracket tests; never a physical CLASS result."""
import copy,hashlib,json,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze as frozen
import c24_native_background as native
import c24_audit
from c32_bracketed_endpoint_audit import bracket_audit, STATUS

class MockClass:
    mode="valid"
    def set(self,**kwargs):self.kwargs=kwargs
    def compute(self):pass
    def get_background(self):
        z=[0.,1.,2.9995860999538064,3.0028107653487153,1100.,3300.]
        if self.mode=="coarse":
            z[3]=3.2
        if self.mode=="exact":
            z[3]=3.0
        mass=[.02]*len(z)
        if self.mode=="right_negative":
            mass[3]=-.03
        return {"z":z,"phi_scf":[4.44]*len(z),
                "rims_mratio":[1.]*len(z),
                "rims_stab":mass,"rims_meff2":list(mass),
                "H [1/Mpc]":[1.]*len(z)}
    def empty(self):pass
class MockModule:
    Class=MockClass
    __file__=__file__

def produce(tmp_path,mode="valid"):
    MockClass.mode=mode
    m=frozen.build_manifest()
    r=native.run_case(MockModule,m["cases"][0],m,tmp_path)
    return m,r,tmp_path/"rims_000"/"receipt.json"

def mutate_receipt(path,fn):
    d=json.loads(path.read_text());fn(d)
    path.write_text(json.dumps(d,sort_keys=True))
    return d

def test_c32_positive_bracket_sample_pass_with_strict_legacy_rejection(tmp_path):
    m,r,p=produce(tmp_path)
    old=c24_audit.audit(m,tmp_path)
    assert old["cases"][0]["status"]=="PHYSICAL_REJECT"
    assert old["cases"][0]["issues"]==["z_0to3_coverage_failed"]
    q=bracket_audit(m,tmp_path)
    assert q["c32_status"]==STATUS
    assert q["original_legacy_audit_status"]=="PHYSICAL_REJECT"
    assert q["z3_boundary_estimate"]["is_exact_native_mesh_sample"] is False
    assert q["z3_boundary_estimate"]["not_continuum_stability_proof"] is True
    assert q["other_80_cases_unattempted"] is True

def test_c32_right_mass_negative_is_a_real_veto(tmp_path):
    m,r,p=produce(tmp_path,"right_negative")
    assert r["run_status"]=="solver_completed"
    with pytest.raises(ValueError,match="unstable mass squared"):
        bracket_audit(m,tmp_path)

def test_c32_gap_too_wide_is_not_certified(tmp_path):
    m,r,p=produce(tmp_path,"coarse")
    with pytest.raises(ValueError,match="too coarse"):
        bracket_audit(m,tmp_path)

def test_c32_deleted_right_bracket_fail_closed(tmp_path):
    m,r,p=produce(tmp_path)
    mutate_receipt(p,lambda d:d.__setitem__("c32_native_z3_bracket",None))
    with pytest.raises(ValueError,match="Missing native full-mass"):
        bracket_audit(m,tmp_path)

def test_c32_mutated_bracket_mass_detected_by_receipt_hash(tmp_path):
    m,r,p=produce(tmp_path)
    mutate_receipt(p,lambda d:d["c32_native_z3_bracket"]["right"].__setitem__("rims_stab",.2))
    with pytest.raises(ValueError,match="Canonical raw native bracket"):
        bracket_audit(m,tmp_path)

def test_c32_rehashed_bracket_not_allowed_to_override_original_log(tmp_path):
    m,r,p=produce(tmp_path)
    def tamper(d):
        b=d["c32_native_z3_bracket"]
        b["right"]["rims_meff2"]=.4;b["right"]["rims_stab"]=.4
        d["c32_native_z3_bracket_sha256"]=hashlib.sha256(
            json.dumps(b,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    mutate_receipt(p,tamper)
    with pytest.raises(ValueError,match="Original native event"):
        bracket_audit(m,tmp_path)

def test_c32_source_row_index_changed_even_if_receipt_rehashed(tmp_path):
    m,r,p=produce(tmp_path)
    def tamper(d):
        b=d["c32_native_z3_bracket"];b["right"]["row_index"]=4
        d["c32_native_z3_bracket_sha256"]=hashlib.sha256(
            json.dumps(b,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    mutate_receipt(p,tamper)
    with pytest.raises(ValueError):
        bracket_audit(m,tmp_path)

def test_c32_archived_legacy_v6_cannot_be_promoted_as_v7(tmp_path):
    m,r,p=produce(tmp_path)
    mutate_receipt(p,lambda d:d.__setitem__("code_version","c30_native_background_v6"))
    with pytest.raises(ValueError,match="Legacy native provenance"):
        bracket_audit(m,tmp_path)

def test_c32_missing_history_fails_closed(tmp_path):
    m,r,p=produce(tmp_path)
    (tmp_path/"rims_000"/"c27_full_history_z_phi.json").unlink()
    with pytest.raises(FileNotFoundError):
        bracket_audit(m,tmp_path)

def test_c32_never_changes_fixed_81_input_grid(tmp_path):
    m,r,p=produce(tmp_path)
    assert m["freeze_hash"]=="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
    assert len(m["cases"])==81
    assert r["run_status"]=="solver_completed"
    assert r["native_compute_attempts"]==2
    q=bracket_audit(m,tmp_path)
    assert "PHYSICAL_VALID" not in q["c32_status"]

def test_c32_exact_native_z3_is_not_mislabelled_interpolation(tmp_path):
    m,r,p=produce(tmp_path,"exact")
    old=c24_audit.audit(m,tmp_path)
    assert old["cases"][0]["status"]=="PHYSICAL_VALID"
    q=bracket_audit(m,tmp_path)
    assert q["c32_status"]=="NATIVE_Z3_EXACT_MESH_SAMPLED_PASS"
    assert q["z3_boundary_estimate"]["is_exact_native_mesh_sample"] is True
    assert q["z3_boundary_estimate"]["method"]=="exact_native_mesh_sample"
    assert q["z3_boundary_estimate"]["not_continuum_stability_proof"] is True
