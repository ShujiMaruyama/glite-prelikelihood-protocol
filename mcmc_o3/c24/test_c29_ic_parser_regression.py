"""c29 regressions motivated by ACTUAL failed c28 physical Run #2 (39887833682).

The genuine native failure was "Class did not read input parameter(s): ic"
after 3 successful normalization backgrounds; the final background alone
included perturbation-only ic. These tests use FAKE CLASS, not physics.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze as frozen
import c24_native_background as runner
import c24_audit as auditor

def test_all_frozen_81_background_inputs_omit_unread_ic():
    m=frozen.build_manifest()
    for case in m["cases"]:
        pars=runner.base_args(case)
        assert pars["output"]==""
        assert "ic" not in pars
        assert "non_linear" not in pars
        assert "non linear" not in pars
    assert len(m["cases"])==81

class ParserLikeClass:
    attempts=[]
    def set(self,**parameters):
        self.parameters=parameters
        self.attempts.append(parameters.copy())
    def compute(self):
        if self.parameters.get("output") == "" and "ic" in self.parameters:
            raise RuntimeError("Class did not read input parameter(s): ic")
        if self.parameters.get("output") == "" and "non_linear" in self.parameters:
            raise RuntimeError("You requested non-linear computation but no perturbations")
    def get_background(self):
        ratio=[1.0020129165561753,1.0000006868179911,1.0000000002346996,1.0]
        phase=len(self.attempts)-1
        return {"z":[0.,1.,3.,1200.,3300.],
                "phi_scf":[4.44]*5,
                "rims_mratio":[ratio[min(phase,3)]]*5,
                "rims_stab":[1.]*5,"rims_meff2":[1.]*5,"H [1/Mpc]":[1.]*5}
    def empty(self):pass

class ParserLikeModule:
    Class=ParserLikeClass
    __file__=__file__

def test_three_background_normalizations_and_final_are_ic_free(tmp_path):
    ParserLikeClass.attempts=[]
    m=frozen.build_manifest()
    r=runner.run_case(ParserLikeModule,m["cases"][0],m,tmp_path)
    assert r["run_status"]=="solver_completed"
    assert r["normalization_iteration_success"] is True
    assert r["native_normalization_steps"]==3
    assert r["native_compute_attempts"]==4
    assert [p["rims_require_normalization"] for p in ParserLikeClass.attempts]==["no","no","no","yes"]
    assert all(p.get("output") == "" and "ic" not in p and "non_linear" not in p for p in ParserLikeClass.attempts)
    assert auditor.audit(m,tmp_path)["cases"][0]["status"]=="PHYSICAL_VALID"

def test_original_c28_extraneous_ic_still_causes_mock_parser_error():
    f=ParserLikeClass()
    f.set(output="",ic="ad")
    try:
        f.compute()
        assert False,"Fake CLASS parser should reject perturbation initial conditions"
    except RuntimeError as exc:
        assert "did not read input parameter(s): ic" in str(exc)

def test_actual_physical_run_id_not_claimed_as_success():
    # This test is an immutable claim boundary, not a runtime science result.
    original_c28_run={"id":39887833682,"stage":"final_background",
                     "native_calls":4,"successful_normalization":3,
                     "final_status":"SOLVER_FAILED"}
    assert original_c28_run["successful_normalization"]==3
    assert original_c28_run["final_status"]!="PHYSICAL_VALID"
