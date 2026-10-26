"""C39 synthetic source overlay and raw native mass-decomposition guards.

These are regression/fixture tests, NOT real CLASS solves.
"""
import hashlib,json,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c39_instrument_stability_terms import ANCHOR,OVERLAY,overlay,install
from c39_audit_raw_stability_terms import parse_line,audit,PREFIX

def source_fixture():return "/* pinned native source */\n"+ANCHOR+"\n} /* fn */\n"
def fmtline(**kw):
    d=dict(a=3.945905e-10,phi=4.1,s=.65,H=100,Vpp=0.0,
           rho_idm=1.0,mass_curvature=-3.3497966666666667e-7,
           matter_term=-1.004939e-6,raw_meff2=-1.004939e-6,
           h2=1e4,ratio=-1.004939e-10,tolerance=1e-10)
    d.update(kw)
    return PREFIX+" "+" ".join(k+"="+format(v,'.17g') for k,v in d.items())

def test_overlay_changes_only_original_rejection_prelog():
    orig=source_fixture()
    mod=overlay(orig)
    assert mod.replace(OVERLAY,"",1)==orig
    assert mod.count(ANCHOR)==1 and mod.count(PREFIX)==1
    assert "class_test" in mod and "rims_stability_tolerance" in mod

def test_overlay_rejects_absent_original_veto():
    with pytest.raises(ValueError,match="absent/ambiguous"):overlay("no native gate")
def test_overlay_rejects_ambiguous_or_double_patch():
    with pytest.raises(ValueError,match="absent/ambiguous"):overlay(source_fixture()+ANCHOR)
    with pytest.raises(ValueError):overlay(overlay(source_fixture()))
def test_install_emits_pre_post_source_hash_and_roundtrip(tmp_path):
    f=tmp_path/"background.c";f.write_text(source_fixture())
    dest=tmp_path/"source_audit.json"
    r=install(f,dest)
    assert r["source_sha256_before_overlay"]==r["reconstruction_original_sha256"]
    assert hashlib.sha256(f.read_bytes()).hexdigest()==r["source_sha256_after_overlay"]
    with pytest.raises(FileExistsError):install(f,dest)
def test_real_guard_fixture_decomposition_is_numerically_consistent():
    d=parse_line(fmtline())
    assert d["ratio"]<-d["tolerance"]
    assert d["printed_veto_overshoot"]==pytest.approx(4.939e-13,rel=1e-8)
def test_mass_curvature_contribution_mismatch_is_rejected():
    with pytest.raises(ValueError,match="Matter term mismatch"):
        parse_line(fmtline(matter_term=3.0))
def test_vpp_plus_matter_sum_mismatch_rejected():
    with pytest.raises(ValueError,match="source sum"):
        parse_line(fmtline(raw_meff2=-0.000002,ratio=-2e-10))
def test_positive_total_mass_cannot_masquerade_as_original_veto():
    with pytest.raises(ValueError,match="did not observe"):
        parse_line(fmtline(Vpp=2.0e-6,raw_meff2=9.95061e-7,ratio=9.95061e-11))
def test_malicious_nan_and_wrong_tolerance_fail_closed():
    with pytest.raises(ValueError,match="Nonfinite"):parse_line(fmtline(s=float("nan")))
    with pytest.raises(ValueError,match="retuned"):parse_line(fmtline(tolerance=1e-8))
def test_missing_real_native_stderr_record_not_promoted(tmp_path):
    a={"schema":"rims-c39-source-overlay-v1",
        "source_sha256_before_overlay":"aa","reconstruction_original_sha256":"aa",
        "source_sha256_after_overlay":"bb","veto_gate_preserved":True,
        "changed_tolerance":False,"changed_scientific_parameters":False}
    b={"case_id":"rims_002","case_sha256":"9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284",
       "freeze_sha256":"0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0",
       "compute_attempts":1,"normalization_or_final_background_certified":False,
       "status":"ORIGINAL_SHOOTING_FAILURE_REPRODUCED",
       "c35_failure_prefix_matches":True,
       "c35_original_truncated_error_prefix_sha256":"eb8b7a6e5e52cec209141a7c359c5e6947b5479bb076df592558853b41b4beaf"}
    (tmp_path/"audit.json").write_text(json.dumps(a));(tmp_path/"receipt.json").write_text(json.dumps(b))
    err=tmp_path/"stderr.txt";err.write_text("unrelated solver error\n")
    with pytest.raises(ValueError,match="No native Vpp/matter"):
        audit(err,tmp_path/"receipt.json",tmp_path/"audit.json")
    err.write_text(fmtline()+"\n")
    v=audit(err,tmp_path/"receipt.json",tmp_path/"audit.json")
    assert v["physical_trigger_count"]==1
    assert not v["native_solver_viability_demonstrated"]
