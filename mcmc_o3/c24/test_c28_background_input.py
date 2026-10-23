"""c28 regression for real Run #2 configuration fault, synthetic only.

Source of fault: upstream CLASS input_read_parameters_nonlinear checks
ppt->has_perturbations even when non_linear is explicitly set to "none".
Therefore omit the key entirely for output="" background-only operations.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze
import c24_native_background as native
import c24_audit

def test_background_mode_never_passes_nonlinear_parameter():
    for case in c23_freeze.build_manifest()["cases"]:
        args=native.base_args(case)
        assert args["output"]==""
        assert "non_linear" not in args
        assert "non linear" not in args

def test_initialization_and_final_background_do_not_reinsert_nonlinear(tmp_path):
    class FakeClass:
        def set(self,**params):
            assert "non_linear" not in params
            assert "non linear" not in params
            assert params.get("output")==""
        def compute(self):pass
        def get_background(self):
            return {"z":[0.,1.,3.,1200.,3300.],
                    "phi_scf":[4.44]*5,
                    "rims_mratio":[1.]*5,
                    "rims_m2eff_over_H2":[1.]*5}
        def empty(self):pass
    class FakeModule:
        Class=FakeClass
        __file__=__file__
    m=c23_freeze.build_manifest()
    r=native.run_case(FakeModule,m["cases"][0],m,tmp_path)
    assert r["run_status"]=="solver_completed"
    assert r["native_compute_attempts"]==2
    assert r["code_version"]=="c29_native_background_v5"
    assert r["c26_initial_shell"]["gate"]=="EARLY_OCCUPANCY_PASS"
    audit=c24_audit.audit(m,tmp_path)
    assert audit["cases"][0]["status"]=="PHYSICAL_VALID"
    assert audit["statuses"]["NO_RECEIPT"]==80

def test_frozen_81_inputs_remain_unchanged():
    m=c23_freeze.build_manifest()
    assert m["freeze_hash"]=="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
    assert len(m["cases"])==81


def test_binary_hash_targets_class_implementation_module_not_python_wrapper():
    import hashlib
    class FakeClass:
        pass
    class Wrapper:
        Class=FakeClass
        __file__="/fake/irrelevant/python/wrapper/__init__.py"
    target=native.class_compiled_module_path(Wrapper)
    assert target.exists() and target.name==Path(__file__).name
    assert hashlib.sha256(target.read_bytes()).hexdigest()
