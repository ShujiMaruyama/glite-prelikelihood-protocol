"""c30 mock-only tests for the ACTUAL patched CLASS stability column rims_stab.

Patched V18_23_LOCAL_RIMS_PATCH.diff background_output_titles uses:
rims_stab = m_eff²/H² and rims_meff2 = m_eff², H [1/Mpc] = H.
No synthetic test here establishes a real RIMS physical solution.
"""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c23_freeze as frozen
import c24_native_background as native
import c24_audit as review

class ClassDouble:
    mode="valid"
    def set(self,**values):self.values=values
    def compute(self):pass
    def get_background(self):
        z=[0.,1.,3.,1100.,3300.]
        stab=[1.]*len(z)
        if self.mode=="negative":
            stab[2]=-0.01
        result={"z":z,"phi_scf":[4.44]*len(z),"rims_mratio":[1.]*len(z),
                "rims_stab":stab,"rims_meff2":list(stab),
                "H [1/Mpc]":[1.]*len(z)}
        if self.mode=="missing_stab":result.pop("rims_stab")
        if self.mode=="inconsistent":result["rims_meff2"][2]=2.
        if self.mode=="nonfinite":result["rims_stab"][2]=float("nan")
        return result
    def empty(self):pass
class ClassDoubleModule:
    Class=ClassDouble
    __file__=__file__

def simulate(tmp_path,mode):
    ClassDouble.mode=mode
    manifest=frozen.build_manifest()
    receipt=native.run_case(ClassDoubleModule,manifest["cases"][0],manifest,tmp_path)
    audited=review.audit(manifest,tmp_path)["cases"][0]
    return manifest,receipt,audited

def test_real_patch_exact_names_have_full_native_semantics(tmp_path):
    m,r,a=simulate(tmp_path,"valid")
    assert r["run_status"]=="solver_completed"
    assert r["code_version"]=="c32_native_background_v7"
    assert r["c30_mass_ratio_column"]=="rims_stab"
    assert r["c30_max_mass_ratio_reconstruction_error"]==0.
    assert "rims_stab" in r["native_background_keys"]
    assert a["status"]=="PHYSICAL_VALID"
    assert r["native_compute_attempts"]==2

def test_old_guessed_stability_column_not_substituted(tmp_path):
    m,r,a=simulate(tmp_path,"missing_stab")
    assert r["run_status"]=="solver_error"
    assert "Missing exact patched RIMS CLASS column: rims_stab" in r["failure_message"]
    assert a["status"]=="SOLVER_FAILED"
    assert r["native_compute_attempts"]==2

def test_inconsistent_meff_squared_divided_by_H_squared_fails(tmp_path):
    m,r,a=simulate(tmp_path,"inconsistent")
    assert r["run_status"]=="solver_error"
    assert "inconsistent with m_eff^2 / H^2" in r["failure_message"]
    assert a["status"]=="SOLVER_FAILED"

def test_negative_stability_margin_retained_as_physical_reject(tmp_path):
    m,r,a=simulate(tmp_path,"negative")
    assert r["run_status"]=="solver_completed"
    assert a["status"]=="PHYSICAL_REJECT"
    assert "unstable_effective_mass" in a["issues"]

def test_nonfinite_stability_margin_is_not_silently_dropped(tmp_path):
    m,r,a=simulate(tmp_path,"nonfinite")
    assert r["run_status"]=="solver_error"
    assert "nonfinite" in r["failure_message"]
    assert a["status"]=="SOLVER_FAILED"

def test_original_81_design_is_unmodified():
    m=frozen.build_manifest()
    assert m["freeze_hash"]=="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
    assert len(m["cases"])==81
