import importlib.util, json, math, sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]/"github_files"/"mcmc_o3"
if not ROOT.exists(): ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import c41_precision_gate as g
import c41_compare_receipts as c

@pytest.fixture
def base():return {"rims_stability_tolerance":1e-10,"rims_enforce_stability":"yes",
    "rims_phi_ref":4.11730971054,"rims_require_normalization":"no",
    "output":"","H0":70.,"rims_alpha_U":.01,"scf_parameters":"foo"}

def test_predeclared_registry_valid(): assert g.check_registry()["experiment"]["run_mode_default"]=="static-only"
@pytest.mark.parametrize("mode,val", [("tight10-one",1e-11),("tight100-one",1e-12)])
def test_only_precision_changed(base,mode,val):
    b=g.precision_params(base,mode)
    assert b["tol_background_integration"]==val
    assert {k for k in b if k not in base or b[k]!=base.get(k)}=={"tol_background_integration"}
    assert all(b[k]==v for k,v in base.items())

def test_unknown_mode_rejected(base):
    with pytest.raises(ValueError):g.precision_params(base,"static-only")
    with pytest.raises(ValueError):g.precision_params(base,"all-81")

def test_rejects_stability_veto_change(base):
    base["rims_enforce_stability"]="no"
    with pytest.raises(ValueError):g.precision_params(base,"tight10-one")

def test_rejects_stability_tolerance_change(base):
    base["rims_stability_tolerance"]=1e-8
    with pytest.raises(ValueError):g.precision_params(base,"tight10-one")

def test_rejects_reuse_of_solver_key(base):
    base["tol_background_integration"]=1e-10
    with pytest.raises(ValueError):g.precision_params(base,"tight10-one")

def test_rejects_extra_perturbation_inputs(base):
    base["ic"]="ad"
    with pytest.raises(ValueError):g.precision_params(base,"tight10-one")

def test_registry_rejects_posthoc_success(tmp_path):
    j=g.check_registry();j["execution_receipts"]["integration_convergence_verified"]=True
    p=tmp_path/"registry.json";p.write_text(json.dumps(j))
    with pytest.raises(ValueError):g.check_registry(p)

def test_registry_rejects_retuning(tmp_path):
    j=g.check_registry();j["experiment"]["manual_modes"]["tight10-one"]["tol_background_integration"]=1e-8
    p=tmp_path/"registry.json";p.write_text(json.dumps(j))
    with pytest.raises(ValueError):g.check_registry(p)

def record(mode,ratio=-1.01e-10, a=3.9e-10):
    return {"run_mode":mode,"status":"SHOOTING_FAILED_WITH_VETO","tol_background_integration":g.EXPECTED_MODES[mode],
            "case":"rims_002","case_sha256":g.EXPECTED_CASE_SHA,"freeze_sha256":g.EXPECTED_FREEZE,
            "compute_calls_attempted":1,"original_veto_tolerance":1e-10,
            "retuned_shooting":False,"normalized_final_background_certified":False,
            "numerical_convergence_demonstrated":False,"source_evidence_status":"NATIVE_VETO_SOURCE_ARITHMETIC_CHECKED",
            "native_record_parse_error":None,"all_veto_records_count":1,
            "all_veto_records":[{"a":a,"s":.65,"ratio":ratio,"Vpp_over_H2":1e-130,
                                 "matter_over_H2":ratio,"tolerance":1e-10}]}

BASELINE={"ratio":-1.0049389722010728e-10,"matter_term":-1.929112031676594e16,
          "a":3.945904558535526e-10}

def test_comparison_does_not_claim_convergence():
    q=c.compare(BASELINE,[record("tight10-one"),record("tight100-one",a=3.90001e-10)])
    assert not q["integration_convergence_proven"]
    assert q["no_root_bracket_captured"]
    assert q["status"]=="SAME_NEGATIVE_SOURCE_SIGN_NOT_CONVERGED"

def test_mixed_modes_duplicate_rejected():
    with pytest.raises(ValueError):c.compare(BASELINE,[record("tight10-one"),record("tight10-one")])

def test_wrong_stability_threshold_in_record_rejected():
    bad=record("tight10-one");bad["original_veto_tolerance"]=1e-9
    with pytest.raises(ValueError):c.compare(BASELINE,[bad,record("tight100-one")])

def test_missing_record_is_fail_closed():
    bad=record("tight100-one");bad["all_veto_records"]=[];bad["all_veto_records_count"]=0
    with pytest.raises(ValueError,match="SOURCE_RECORD_UNAVAILABLE"):c.compare(BASELINE,[record("tight10-one"),bad])

def test_nonnegative_sign_is_not_promoted():
    bad=record("tight10-one",ratio=-1.01e-10)
    bad["all_veto_records"][0]["matter_over_H2"]=1.0
    with pytest.raises(ValueError):c.compare(BASELINE,[bad,record("tight100-one")])

def test_nonfinite_rejected():
    bad=record("tight100-one");bad["all_veto_records"][0]["a"]=float('nan')
    with pytest.raises(ValueError):c.compare(BASELINE,[record("tight10-one"),bad])

def test_compute_attempts_cannot_be_zero():
    bad=record("tight100-one");bad["compute_calls_attempted"]=0
    with pytest.raises(ValueError):c.compare(BASELINE,[record("tight10-one"),bad])

def test_c40_external_archive_integrity_only_when_supplied():
    """The immutable C40 ZIP is *external evidence*, not part of this Git checkout.

    Missing evidence is explicitly SKIPPED, never misreported as a passed
    archive-integrity audit. If independently supplied, verify the exact
    registered bytes rather than merely checking for an arbitrary ZIP.
    """
    import hashlib, zipfile
    p=Path(__file__).resolve().parents[1]/"evidence"/"RIMS_C40_EXACT_LOCAL_VETO_ENVELOPE_20261027.zip"
    if not p.is_file():
        pytest.skip("C40 original ZIP not supplied to GitHub checkout: external integrity audit NOT performed")
    assert p.stat().st_size == 74199
    assert hashlib.sha256(p.read_bytes()).hexdigest() == "6d17d50f2079a94a58ed27867ab43ec9fc1b0d1d3cd702fe158b94824459df6b"
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        assert "outputs/C40_ACTUAL_FIXED_SLICE_AUDIT.json" in z.namelist()


def test_c41_ledger_preserves_c39_evidence_boundary():
    """A passing static suite cannot claim that C40/C41 physical validation ran."""
    j=g.check_registry()
    assert j["lineage"]["c39_artifact_sha256"] == (
        "08318f04e7d1e7a0edfa7a69eefd1c2dcf0c19c152ef4640db7b6b33df83e160")
    assert j["lineage"]["frozen_case_id"] == "rims_002"
    assert j["experiment"]["run_mode_default"] == "static-only"
    assert j["experiment"]["original_veto_must_remain_enabled"] is True
    assert j["execution_receipts"]["integration_convergence_verified"] is False
    assert j["execution_receipts"]["two_new_native_computes_executed"] is False


def test_independent_raw_stderr_reparse(tmp_path):
    b=dict(a=3.945904558535526e-10,phi=4.44,s=.65,H=100.,Vpp=0.,
        rho_idm=1.,mass_curvature=-3.35e-7,matter_term=-1.005e-6,
        raw_meff2=-1.005e-6,h2=1e4,ratio=-1.005e-10,tolerance=1e-10)
    line=c.PREFIX+" "+" ".join(k+"="+format(v,'.17g') for k,v in b.items())
    f=tmp_path/"native_stderr.txt";f.write_text("other logs\n"+line+"\n")
    expected=c.parse_line(line)
    r={"native_stderr_sha256":g.sha256(f.read_bytes()),"all_veto_records":[expected]}
    assert c.independently_validate_stderr(r,f)==[expected]
    r["all_veto_records"][0]["ratio"]=-1.04e-10
    with pytest.raises(ValueError,match="mismatch"):
        c.independently_validate_stderr(r,f)

def test_independent_raw_stderr_tamper_detection(tmp_path):
    f=tmp_path/"stderr.txt";f.write_text("not a valid native record")
    with pytest.raises(ValueError,match="SHA256"):
        c.independently_validate_stderr({"native_stderr_sha256":"000"},f)
