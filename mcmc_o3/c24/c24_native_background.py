#!/usr/bin/env python3
"""Manual-only patched RIMS V18.29 CLASS background executor. No MCMC or likelihood."""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess,time
from pathlib import Path
import numpy as np
from c23_freeze import build_manifest,verify
MAXITER=16
TOL=3e-9

def field_key(bg,preferred,tokens):
    if preferred in bg:return preferred
    if preferred=="rims_m2eff_over_H2":
        for a in ("rims_meff2_over_H2","rims_m_eff2_over_H2","rims_m2eff_H2","rims_meff_over_H_squared"):
            if a in bg:return a
    hits=[k for k in bg if all(t.lower() in k.lower().replace(" ","").replace("_","") for t in tokens)]
    if len(hits)!=1:raise RuntimeError("Missing/ambiguous patched RIMS CLASS background field "+preferred+": "+str(hits))
    return hits[0]

def base_args(case):
    b=case["fixed_background"];frac=b["inert_fraction"];omdm=b["omega_dm"]
    return {"H0":b["H0"],"omega_b":b["omega_b"],"omega_cdm":omdm*frac,
        "omega_idm":omdm*(1-frac),"Omega_scf":case["omega_phi0"],
        "N_ur":b["N_ur"],"N_ncdm":0,"YHe":"BBN","tau_reio":b["tau_reio"],
        "gauge":"synchronous","ic":"ad","scf_parameters":case["scf_parameters"],
        "attractor_ic_scf":"no","scf_tuning_index":0,
        "recombination":"HYREC","reio_parametrization":"reio_camb",
        "idm_soundspeed":"no","rims_enabled":"yes",
        "rims_enforce_stability":"yes","rims_stability_tolerance":1e-10,
        "rims_normalization_tolerance":1e-8,
        "rims_subleading_adiabatic_ic":"yes","rims_regular_standard_ic":"yes",
        "rims_alpha_U":case["alpha_U"],"rims_phi_transition":case["phi_t"],"output":""}

# For CLASS upstream e858083..., explicitly supplying non_linear='none'
# STILL triggers a perturbation requirement in input_read_parameters_nonlinear.
# Pure background-only runs must OMIT that key entirely when output="".
# The actual r28 failure diagnosis is GitHub Actions run 39741330265.
def run_case(classy,case,manifest,out):
    folder=Path(out)/case["id"];folder.mkdir(parents=True,exist_ok=False)
    log=folder/"native_compute.log"
    binary=Path(classy.__file__).resolve(strict=True)
    receipt={"schema":"rims-c23-native-background-attempt-v1",
        "id":case["id"],"case_sha256":case["input_sha256"],
        "source_freeze_hash":manifest["freeze_hash"],
        "Class_upstream_commit":manifest["Class_upstream_commit"],
        "RIMS_patch_sha256":manifest["RIMS_patch_sha256"],
        "code_version":"c28_native_background_v4","MCMC":False,
        "synthetic_fixture":False,"run_status":"solver_error",
        "native_compute_attempts":0,"normalization_iteration_success":False,
        "binary_path":str(binary),"binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest()}
    t0=time.monotonic()
    def event(f,label,fields):
        f.write(json.dumps({"event":label,"mono_seconds":time.monotonic()-t0,**fields},sort_keys=True)+"\n");f.flush()
    def calculate(f,params,kind):
        # Setup and extraction failures are NOT failed native compute() calls.
        # Every native compute() START has one SUCCESS or EXCEPTION event.
        try:
            obj=classy.Class()
        except BaseException as ex:
            event(f,"native_setup_exception",{"kind":kind,"stage":"Class_constructor",
                  "error_type":type(ex).__name__,"error":str(ex)[:400]})
            raise
        try:
            try:
                obj.set(**params)
            except BaseException as ex:
                event(f,"native_setup_exception",{"kind":kind,"stage":"Class.set",
                      "error_type":type(ex).__name__,"error":str(ex)[:400]})
                raise
            receipt["native_compute_attempts"]+=1
            idx=receipt["native_compute_attempts"]
            event(f,"native_compute_start",{"index":idx,"kind":kind})
            try:
                obj.compute()
            except BaseException as ex:
                event(f,"native_compute_exception",{"index":idx,"kind":kind,
                      "error_type":type(ex).__name__,"error":str(ex)[:400]})
                raise
            event(f,"native_compute_end",{"index":idx,"kind":kind,"success":True})
            try:
                result=obj.get_background()
                return {k:np.asarray(v) for k,v in result.items()}
            except BaseException as ex:
                event(f,"native_extract_exception",{"index":idx,"kind":kind,
                      "error_type":type(ex).__name__,"error":str(ex)[:400]})
                raise
        finally:
            try:obj.empty()
            except Exception:pass
    with log.open("x") as f:
        try:
            args=base_args(case);pref=4.11730971054
            for step in range(MAXITER):
                q=dict(args);q["rims_phi_ref"]=pref;q["rims_require_normalization"]="no";q.pop("ic",None)
                bg=calculate(f,q,"normalization_background")
                z=np.asarray(bg[field_key(bg,"z",("z",))],float)
                if not np.all(np.isfinite(z)):raise RuntimeError("nonfinite native normalization redshift values")
                j=int(np.argmin(np.abs(z)))
                phi=float(np.asarray(bg[field_key(bg,"phi_scf",("phi","scf"))],float)[j])
                mr=float(np.asarray(bg[field_key(bg,"rims_mratio",("rims","mratio"))],float)[j])
                if not(math.isfinite(phi) and math.isfinite(mr)):raise RuntimeError("nonfinite normalization endpoint")
                event(f,"norm_step",{"step":step,"mass_ratio":mr,"phi_ref":pref})
                if abs(mr-1)<=TOL:break
                pref=phi
            else:raise RuntimeError("native RIMS normalization did not converge within 16 steps")
            receipt["normalization_iteration_success"]=True
            q=dict(args);q["rims_phi_ref"]=pref;q["rims_require_normalization"]="yes"
            bg=calculate(f,q,"final_background")
            z=np.asarray(bg[field_key(bg,"z",("z",))],float)
            phi=np.asarray(bg[field_key(bg,"phi_scf",("phi","scf"))],float)
            mr=np.asarray(bg[field_key(bg,"rims_mratio",("rims","mratio"))],float)
            m2=np.asarray(bg[field_key(bg,"rims_m2eff_over_H2",("rims","m2","h2"))],float)
            if z.ndim!=1 or not(z.shape==phi.shape==mr.shape==m2.shape):raise RuntimeError("CLASS background array shape mismatch")
            # c27: freeze the full, UNFILTERED final native CLASS z/phi vectors.
            # This raw history is independently compared with the c26
            # earliest-epoch statement; neither data file is a second solver.
            from c27_history_integrity import make_history_payload, canonical_json_bytes
            original_history=make_history_payload(case,manifest,z,phi)
            original_bytes=canonical_json_bytes(original_history)
            original_path=folder/"c27_full_history_z_phi.json"
            with original_path.open("xb") as source_file:
                source_file.write(original_bytes)
            receipt["c27_native_history_sha256"]=hashlib.sha256(original_bytes).hexdigest()
            event(f,"c27_full_native_history_export",{
                "sha256":receipt["c27_native_history_sha256"],
                "source_case_sha256":case["input_sha256"],
                "all_unfiltered_native_rows":len(z)})
            # c26: independently report whether CLASS actually reached the
            # initial shell occupancy specified in the frozen design.
            # This is an ADDITIONAL science gate, not a substitute for c25
            # numerical receipt, nor a production-likelihood validation.
            try:
                from c26_occupancy_gate import derive_initial_gate
                receipt["c26_initial_shell"] = derive_initial_gate(case,z,phi)
                event(f,"c26_initial_occupancy_gate",{
                    "gate":receipt["c26_initial_shell"]["gate"],
                    "initial_z":receipt["c26_initial_shell"]["earliest_z"],
                    "source_case_sha256":case["input_sha256"]})
            except Exception as exc:
                receipt["c26_initial_shell"] = {"schema":"rims-c26-early-shell-occupancy-v1",
                    "gate":"INITIAL_GATE_DATA_ERROR","error_type":type(exc).__name__,
                    "case_id":case["id"],"case_sha256":case["input_sha256"]}
                event(f,"c26_initial_occupancy_gate",{"gate":"INITIAL_GATE_DATA_ERROR",
                    "source_case_sha256":case["input_sha256"]})

            if not np.all(np.isfinite(z)):raise RuntimeError("nonfinite redshift coordinates, cannot safely filter z=0..3")
            inside=(z>=0)&(z<=3)
            receipt["native_z_total_rows"]=int(len(z))
            receipt["native_z_in_domain_rows"]=int(np.count_nonzero(inside))
            receipt["input_native_nonfinite_count"]=int(np.count_nonzero(~(np.isfinite(phi[inside])&np.isfinite(mr[inside])&np.isfinite(m2[inside]))))
            if receipt["input_native_nonfinite_count"]:raise RuntimeError("nonfinite physical CLASS background within z=0..3, refusing silent row exclusion")
            if receipt["native_z_in_domain_rows"]<2:raise RuntimeError("insufficient z=0..3 native rows")
            z=z[inside];phi=phi[inside];mr=mr[inside];m2=m2[inside]
            order=np.argsort(z);z=z[order];phi=phi[order];mr=mr[order];m2=m2[order]
            s=1/(1+np.exp(np.clip(-2*case["alpha_U"]*(phi-case["phi_t"]),-700,700)))
            norm_err=float(mr[int(np.argmin(np.abs(z)))])-1
            receipt["background"]=[{"z":float(zz),"s":float(ss),"m2_over_H2":float(mm),"norm_err":norm_err} for zz,ss,mm in zip(z,s,m2)]
            receipt["native_min_m2_over_H2"]=float(np.min(m2))
            receipt["native_z_range"]=[float(z[0]),float(z[-1])]
            receipt["native_normalization_steps"]=int(step+1)
            receipt["final_background_arrays_count"]=int(len(z))
            receipt["phi_ref"]=float(pref)
            receipt["run_status"]="solver_completed"
        except BaseException as ex:
            receipt["failure_class"]=type(ex).__name__
            receipt["failure_message"]=str(ex)[:1000]
            event(f,"failure",{"type":type(ex).__name__,"message":str(ex)[:500]})
        finally:receipt["wall_seconds"]=time.monotonic()-t0
    receipt["log_sha256"]=hashlib.sha256(log.read_bytes()).hexdigest()
    (folder/"receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return receipt

def verify_pinned_environment(src,base_patch,delta_patch,m):
    src=Path(src).resolve(strict=True)
    for f,expected in zip((base_patch,delta_patch),m["RIMS_patch_sha256"]):
        if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=expected:raise RuntimeError("RIMS patch SHA mismatch")
    head=subprocess.check_output(["git","-C",str(src),"rev-parse","HEAD"],text=True).strip()
    if head!=m["Class_upstream_commit"]:raise RuntimeError("wrong CLASS upstream commit")
    subprocess.run(["git","-C",str(src),"diff","--check"],check=True)
    if not subprocess.check_output(["git","-C",str(src),"diff","--name-only"],text=True).strip():
        raise RuntimeError("patched RIMS source diff absent")
    import classy
    binary=Path(classy.__file__).resolve(strict=True)
    if src not in binary.parents:raise RuntimeError("imported CLASS binary outside pinned patched source: "+str(binary))
    return classy

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--class-source",type=Path,required=True)
    p.add_argument("--base-patch",type=Path,required=True);p.add_argument("--delta-patch",type=Path,required=True)
    selection=p.add_mutually_exclusive_group(required=True)
    selection.add_argument("--one");selection.add_argument("--all-81",action="store_true")
    a=p.parse_args();m=json.loads(a.manifest.read_text());verify(m)
    cases=m["cases"] if a.all_81 else [x for x in m["cases"] if x["id"]==a.one]
    if not cases:raise RuntimeError("unknown frozen ID; refuse to run")
    classy=verify_pinned_environment(a.class_source,a.base_patch,a.delta_patch,m)
    results=[]
    for case in cases:
        r=run_case(classy,case,m,a.output);results.append(r)
        print(r["id"],r["run_status"],r.get("failure_message",""),flush=True)
    if any(r["run_status"]!="solver_completed" for r in results):raise SystemExit(2)
if __name__=="__main__":main()
