"""Mock-only tests: no native CLASS computation; never promote a solver result."""
import hashlib,json,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
import c23_freeze as frozen
import c37_exact_shooting_probe as p
class CosmoComputationError(Exception):pass
class FailClass:
    calls=0
    def set(self,**kw):self.kw=kw
    def compute(self):
        self.__class__.calls+=1
        raise CosmoComputationError("Shooting failed: "+"derivative_inner_failure|"*100)
    def empty(self):pass
class SuccessClass(FailClass):
    def compute(self):self.__class__.calls+=1
class OtherFailClass(FailClass):
    def compute(self):raise RuntimeError("A different numerical failure")
class Module:
    Class=FailClass

def manifest_and_case():
    m=frozen.build_manifest()
    return m,m["cases"][2]
def test_only_002_and_same_parameters():
    m,c=manifest_and_case()
    d=p.exact_params(c)
    assert d["rims_phi_ref"]==4.11730971054
    assert d["rims_require_normalization"]=="no"
    assert d["output"]=="" and "ic" not in d and "non_linear" not in d
    assert d["scf_parameters"]==c["scf_parameters"]
def test_reject_other_two_successful_cases():
    m,c=manifest_and_case()
    for x in m["cases"][:2]:
        with pytest.raises(ValueError):p.exact_params(x)
def test_full_exception_retained_without_1000_character_cap(tmp_path):
    m,c=manifest_and_case();FailClass.calls=0
    Module.Class=FailClass
    r=p.single_probe(Module,c,m,tmp_path/"probe",__file__)
    msg=(tmp_path/"probe"/"full_CLASS_exception.txt").read_bytes()
    assert r["status"]=="ORIGINAL_SHOOTING_FAILURE_REPRODUCED"
    assert r["compute_attempts"]==1 and FailClass.calls==1
    assert len(msg)>1000
    assert r["error_sha256"]==hashlib.sha256(msg).hexdigest()
    assert json.loads((tmp_path/"probe"/"receipt.json").read_text())==r
def test_existing_output_never_overwritten(tmp_path):
    m,c=manifest_and_case()
    Module.Class=FailClass
    (tmp_path/"probe").mkdir()
    with pytest.raises(FileExistsError):
        p.single_probe(Module,c,m,tmp_path/"probe",__file__)
def test_different_native_failure_not_mislabeled(tmp_path):
    m,c=manifest_and_case();Module.Class=OtherFailClass
    r=p.single_probe(Module,c,m,tmp_path/"probe",__file__)
    assert r["status"]=="OTHER_ERROR" and r["compute_attempts"]==1
def test_returned_first_compute_not_a_physical_solution(tmp_path):
    m,c=manifest_and_case();Module.Class=SuccessClass
    r=p.single_probe(Module,c,m,tmp_path/"probe",__file__)
    assert r["status"]=="FIRST_COMPUTE_RETURNED_NOT_A_NORMALIZED_BACKGROUND"
    assert r["normalization_or_final_background_certified"] is False
def test_frozen_manifest_injected_change_fail_closed(tmp_path):
    m,c=manifest_and_case()
    m["cases"][2]["s_i"]=.1
    Module.Class=FailClass
    with pytest.raises(ValueError):
        p.single_probe(Module,c,m,tmp_path/"probe",__file__)
