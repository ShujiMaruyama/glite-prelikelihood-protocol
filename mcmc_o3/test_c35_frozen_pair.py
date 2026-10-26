"""c35 nonphysical offline gate: selection, analytic signs, no reruns."""
import copy,json,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
import c35_frozen_pair_run as run
from c23_freeze import build_manifest

@pytest.fixture
def frozen():return build_manifest()

def test_locked_source_81_and_cases(frozen):
    d=run.plan(frozen)
    assert d["frozen_81_sha256"]==run.FROZEN
    assert d["new_exact_cases"]==["rims_001","rims_002"]
    assert d["historic_reference"]["must_not_reexecute"] is True

def test_only_initial_occupancy_changes_in_frozen_triplet(frozen):
    c=frozen["cases"][:3]
    for k in ("potential","alpha_U","omega_phi0","fixed_background"):
        assert len({json.dumps(x[k],sort_keys=True) for x in c})==1
    assert [x["s_i"] for x in c]==pytest.approx([.1,1/3,.65])

def test_exact_predeclared_three_mass_curvature_signs(frozen):
    d=run.plan(frozen)
    assert list(d["expected_start_mass_curvature_sign"].values())==[
        "POSITIVE","ZERO","NEGATIVE"]

def test_exact_conditional_beta_and_amplitude_values(frozen):
    d=run.plan(frozen)
    assert list(d["analytic_initial_beta"].values())==pytest.approx([.009,1/150,.0035])
    assert list(d["conditional_massless_dark_dark_Gamma_proxy"].values())==pytest.approx(
        [0.000162,2*(1/150)**2,0.0000245])

def test_sign_is_mass_curvature_not_total_effective_mass():
    assert run.sign(.1)=="POSITIVE"
    assert run.sign(1/3)=="ZERO"
    assert run.sign(.65)=="NEGATIVE"

def test_reject_wrong_frozen_grid_even_if_top_metadata_changed(frozen):
    x=copy.deepcopy(frozen);x["cases"][1]["s_i"]+=.0001
    with pytest.raises(ValueError):run.plan(x)

def test_reject_cross_case_background_change(frozen):
    x=copy.deepcopy(frozen);x["cases"][2]["fixed_background"]["H0"]=99
    with pytest.raises(ValueError):run.plan(x)

def test_existing_results_never_overwritten(tmp_path,frozen):
    d=tmp_path/"native"
    d.mkdir();(d/"rims_001").mkdir()
    with pytest.raises(FileExistsError):
        run.run(frozen,d,Path("dummy.py"),
             {"manifest":Path("C23_FROZEN_81.json"),"class":Path("class_public")},
             Path("p1"),Path("p2"),10)

def test_timeout_must_be_finite_safe_range(tmp_path,frozen):
    with pytest.raises(ValueError):
        run.run(frozen,tmp_path/"new",Path("dummy.py"),
             {"manifest":Path("C23_FROZEN_81.json"),"class":Path("class_public")},
             Path("p1"),Path("p2"),0)

def test_strict_no_automatic_physics_in_plan(frozen):
    d=run.plan(frozen)
    assert d["new_native_cases_executed"]==0
    assert not d["MCMC"] and not d["automatic_follow_on"]
    assert not d["real_survey_prediction"]
