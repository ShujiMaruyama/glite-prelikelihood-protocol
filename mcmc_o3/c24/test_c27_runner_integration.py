"""Real c27 runner-to-audit connection with an in-process FAKE CLASS object.
This tests file wiring only; it is not a physical RIMS V18.29 calculation.
"""
import json,sys,hashlib
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze as frozen
import c24_native_background as native
from c27_history_integrity import audit_history

class MockClass:
    def set(self,**kwargs):self.kwargs=kwargs
    def compute(self):pass
    def get_background(self):
        return {"z":[0.,1.,3.,100.,1100.,3300.],
                "phi_scf":[4.44]*6,
                "rims_mratio":[1.]*6,
                "rims_stab":[1.]*6,"rims_meff2":[1.]*6,"H [1/Mpc]":[1.]*6}
    def empty(self):pass

class MockModule:
    Class=MockClass
    __file__=__file__

def produce(tmp_path):
    manifest=frozen.build_manifest()
    receipt=native.run_case(MockModule,manifest["cases"][0],manifest,tmp_path)
    p=tmp_path/"rims_000"/"c27_full_history_z_phi.json"
    return manifest,receipt,p

def test_mock_native_runner_exports_full_history_and_passes_c27(tmp_path):
    m,r,p=produce(tmp_path)
    assert r["run_status"]=="solver_completed"
    assert r["native_compute_attempts"]==2
    assert p.exists()
    result=audit_history(m,r,json.loads(p.read_text()),p.read_bytes())
    assert result["gate_pass"] and result["history_rows"]==6
    assert result["recomputed_s_i"]==pytest.approx(0.1,abs=1e-14)
    assert not result["independent_physical_solver"]

def test_mock_native_runner_source_mutation_is_detected(tmp_path):
    m,r,p=produce(tmp_path)
    original=json.loads(p.read_text())
    original["phi"][-1]+=0.1
    # Even a valid regenerated raw JSON cannot match old saved receipt SHA.
    from c27_history_integrity import canonical_json_bytes
    raw=canonical_json_bytes(original)
    with pytest.raises(ValueError):
        audit_history(m,r,original,raw)
