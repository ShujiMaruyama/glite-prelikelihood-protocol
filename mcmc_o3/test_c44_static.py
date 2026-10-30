"""C44 original frozen input gates; external native CLASS is not executed."""
import sys,types
from pathlib import Path
import pytest
for name in ("c23_freeze","c24_native_background","c37_exact_shooting_probe"):
    if name not in sys.modules:sys.modules[name]=types.ModuleType(name)
sys.modules["c23_freeze"].verify=lambda x:None
sys.modules["c37_exact_shooting_probe"].exact_params=lambda x:{}
sys.path.insert(0,str(Path(__file__).parent))
import c44_native_phase_probe as c44

@pytest.fixture
def state(monkeypatch):
    monkeypatch.setattr(c44.freeze,"verify",lambda m:None)
    c={"id":"rims_002","input_sha256":c44.CASE_SHA}
    m={"freeze_hash":c44.FREEZE_SHA,"cases":[c]+[{"id":f"x{i}"} for i in range(80)]}
    p={"rims_stability_tolerance":1e-10,"rims_enforce_stability":"yes","output":"","H0":70.}
    monkeypatch.setattr(c44,"exact_params",lambda x:dict(p))
    return m,p

def test_single_frozen_input(state):
    m,p=state
    assert c44.original_input(m)==p

def test_changed_manifest_rejected(state):
    m,p=state;m["freeze_hash"]="changed"
    with pytest.raises(AssertionError):c44.original_input(m)

def test_changed_case_rejected(state):
    m,p=state;m["cases"][0]["input_sha256"]="wrong"
    with pytest.raises(AssertionError):c44.original_input(m)

@pytest.mark.parametrize("key,value",[
 ("rims_stability_tolerance",1e-8),
 ("rims_enforce_stability","no"),
 ("tol_background_integration",1e-12),
 ("ic","ad"),
 ("output","tCl"),
])
def test_forbidden_input_mutation(state,monkeypatch,key,value):
    m,p=state;p[key]=value
    monkeypatch.setattr(c44,"exact_params",lambda x:p)
    with pytest.raises(AssertionError):c44.original_input(m)

def test_no_native_without_opt_in(monkeypatch):
    monkeypatch.delenv("RIMS_C43_NDF_TRACE",raising=False)
    with pytest.raises(ValueError,match="trace must be enabled"):c44.run(None)
