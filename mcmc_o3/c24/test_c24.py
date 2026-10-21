"""Synthetic-only regression tests. A PASS never demonstrates physical CLASS correctness."""
import json,sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze as f
import c24_native_background as n
import c24_audit as a

class FakeClass:
    mode="good"
    def set(self,**kwargs):self.kw=kwargs
    def compute(self):
        if self.mode=="exception":raise RuntimeError("synthetic native compute failure")
    def get_background(self):
        z=np.array([0.,1.,2.,3.]);phi=np.array([4.44,4.43,4.42,4.41]);m2=np.ones(4)
        if self.mode=="nan_m2":m2[1]=np.nan
        if self.mode=="unstable":m2[2]=-1e-5
        if self.mode=="short_z":z[-1]=2.9
        if self.mode=="nan_z":z[-1]=np.nan
        return {"z":z,"phi_scf":phi,"rims_mratio":np.ones(4),"rims_m2eff_over_H2":m2}
    def empty(self):pass
class FakeModule:
    Class=FakeClass
    __file__=str(Path(__file__).resolve())

def run(tmp_path,mode="good"):
    FakeClass.mode=mode
    m=f.build_manifest();r=n.run_case(FakeModule,m["cases"][0],m,tmp_path)
    d=a.audit(m,tmp_path);return r,d

def test_frozen_hash_and_81_unique():
    m=f.build_manifest()
    assert m["freeze_hash"]==f.FROZEN_HASH
    assert len(m["cases"])==81
    assert len({c["input_sha256"] for c in m["cases"]})==81
def test_source_mutation_rejected():
    m=f.build_manifest();m["cases"][0]["alpha_U"]=0.2
    with pytest.raises(ValueError):f.verify(m)
def test_good_case(tmp_path):
    r,d=run(tmp_path)
    assert r["native_compute_attempts"]==2
    assert d["cases"][0]["status"]=="PHYSICAL_VALID"
    assert not d["all_81_documented"]
def test_nonfinite_m2_fails_closed(tmp_path):
    r,d=run(tmp_path,"nan_m2")
    assert r["run_status"]=="solver_error"
    assert r["input_native_nonfinite_count"]==1
    assert d["cases"][0]["status"]=="SOLVER_FAILED"
def test_nonfinite_z_fails_closed(tmp_path):
    r,d=run(tmp_path,"nan_z")
    assert r["run_status"]=="solver_error"
    assert "nonfinite" in r["failure_message"]
def test_failed_native_compute_preserved(tmp_path):
    r,d=run(tmp_path,"exception")
    assert d["cases"][0]["status"]=="SOLVER_FAILED"
def test_effective_mass_veto(tmp_path):
    r,d=run(tmp_path,"unstable")
    assert r["run_status"]=="solver_completed"
    assert d["cases"][0]["status"]=="PHYSICAL_REJECT"
def test_z_coverage_veto(tmp_path):
    r,d=run(tmp_path,"short_z")
    assert "z_0to3_coverage_failed" in d["cases"][0]["issues"]
def test_event_log_tamper_detected(tmp_path):
    r,d=run(tmp_path);p=tmp_path/r["id"]/"native_compute.log"
    p.write_text(p.read_text()+"\n")
    assert d["cases"][0]["status"]=="PHYSICAL_VALID"
    assert a.audit(f.build_manifest(),tmp_path)["cases"][0]["status"]=="PROVENANCE_GATE_FAIL"
def test_missing_binary_sha_detected(tmp_path):
    r,d=run(tmp_path);p=tmp_path/r["id"]/"receipt.json"
    r.pop("binary_sha256");p.write_text(json.dumps(r))
    assert "unlocked_native_binary_hash" in a.audit(f.build_manifest(),tmp_path)["cases"][0]["issues"]
def test_missing_80_not_valid_81(tmp_path):
    r,d=run(tmp_path)
    assert d["statuses"]["NO_RECEIPT"]==80
    assert d["all_81_documented"] is False
