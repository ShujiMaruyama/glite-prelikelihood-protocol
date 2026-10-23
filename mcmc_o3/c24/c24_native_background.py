#!/usr/bin/env python3
"""Manual-only patched RIMS V18.29 CLASS background executor. No MCMC or likelihood."""
from __future__ import annotations
import argparse,hashlib,importlib,importlib.machinery,json,math,subprocess,sys,time
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
        "gauge":"synchronous","scf_parameters":case["scf_parameters"],
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
def class_compiled_module_path(classy):
    # CLASS' package __init__.py is a Python wrapper, not the native solver.
    # The actual Cython extension is the module defining Class.
    modname=classy.Class.__module__
    module=sys.modules.get(modname)
    if module is None:
        module=importlib.import_module(modname)
    file=getattr(module,"__file__",None)
    if not file:raise RuntimeError("Class implementation module has no physical source path")
    return Path(file).resolve(strict=True)

def run_case(classy,case,manifest,out):
    folder=Path(out)/case["id"];folder.mkdir(parents=True,exist_ok=False)
    log=folder/"native_compute.log"
    binary=class_compiled_module_path(classy)
    receipt={"schema":"rims-c23-native-background-attempt-v1",
        "id":case["id"],"case_sha256":case["input_sha256"],
        "source_freeze_hash":manifest["freeze_hash"],
        "Class_upstream_commit":manifest["Class_upstream_commit"],
        "RIMS_patch_sha256":manifest["RIMS_patch_sha256"],
        "code_version":"c32_native_background_v7","MCMC":False,
        "synthetic_fixture":False,"run_status":"solver_error",
        "native_compute_attempts":0,"normalization_iteration_success":False,
        "binary_path":str(binary),"binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest()}
    t0=time.monotonic()
    def event(f,label,fields):
        f.write(json.dumps({"event":label,"mono_seconds":time.monotonic()-t0,**fields},sort_keys=True)+"\n");f.flush()
    def calculate(f,params,kind):
        # A background-only CLASS call must never pass perturbation initial
        # conditions. This is the diagnosed c28 Run #2 failure (ic unread).
        if params.get("output") == "" and ("ic" in params or "non_linear" in params or "non linear" in params):
            raise ValueError("Perturbation-only inputs prohibited for output='' background smoke")

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
                q=dict(args);q["rims_phi_ref"]=pref;q["rims_require_normalization"]="no"
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
            # c30: these are EXACT patched background_output_titles names,
            # not guesses or alternative physics quantities.
            receipt["native_background_keys"]=sorted(str(k) for k in bg)
            event(f,"c30_native_output_schema",{"keys":receipt["native_background_keys"]})
            for required in ("z","phi_scf","rims_mratio","rims_stab","rims_meff2","H [1/Mpc]"):
                if required not in bg:
                    raise RuntimeError("Missing exact patched RIMS CLASS column: "+required)
            z=np.asarray(bg["z"],float)
            phi=np.asarray(bg["phi_scf"],float)
            mr=np.asarray(bg["rims_mratio"],float)
            m2=np.asarray(bg["rims_stab"],float)
            meff2=np.asarray(bg["rims_meff2"],float)
            hubble=np.asarray(bg["H [1/Mpc]"],float)
            receipt["c30_mass_ratio_column"]="rims_stab"
            if z.ndim!=1 or not(z.shape==phi.shape==mr.shape==m2.shape==meff2.shape==hubble.shape):
                raise RuntimeError("Patched CLASS full background array shape mismatch")
            if not np.all(np.isfinite(z)):
                raise RuntimeError("nonfinite CLASS native redshift coordinate; cannot identify z3 source bracket")

            # Preserve the two original, adjacent FULL CLASS samples around
            # z=3. No resampling and no claim of an exact z=3 CLASS sample.
            # The c27 full-history hash independently binds z and phi rows.
            original_sorted=np.argsort(z)
            zs=z[original_sorted]
            ix=int(np.searchsorted(zs,3.0,side="left"))
            if ix>0 and ix<len(zs):
                original_lo=int(original_sorted[ix-1])
                original_hi=int(original_sorted[ix])
                if not (z[original_lo]<3<=z[original_hi]):
                    raise RuntimeError("Native z=3 bracket source ordering invalid")
                def source_native_row(index):
                    return {"row_index":index,"z":float(z[index]),
                            "phi":float(phi[index]),
                            "s":float(1/(1+np.exp(np.clip(
                                -2*case["alpha_U"]*(phi[index]-case["phi_t"]),-700,700)))),
                            "rims_mratio":float(mr[index]),
                            "rims_stab":float(m2[index]),
                            "rims_meff2":float(meff2[index]),
                            "H_Mpc_inverse":float(hubble[index])}
                receipt["c32_native_z3_bracket"]={
                    "schema":"rims-c32-native-z3-bracket-v1",
                    "source":"raw_final_Class.get_background_before_z_filter",
                    "case_sha256":case["input_sha256"],
                    "left":source_native_row(original_lo),
                    "right":source_native_row(original_hi),
                    "gap":float(z[original_hi]-z[original_lo]),
                    "exact_native_z3_recorded":bool(z[original_hi]==3.0)
                }
                bracket_data=json.dumps(receipt["c32_native_z3_bracket"],
                                        sort_keys=True,separators=(",",":"),allow_nan=False)
                receipt["c32_native_z3_bracket_sha256"]=hashlib.sha256(
                    bracket_data.encode("utf-8")).hexdigest()
                event(f,"c32_native_z3_bracket",{
                    "left_row_index":original_lo,"right_row_index":original_hi,
                    "gap":receipt["c32_native_z3_bracket"]["gap"],
                    "native_right_stability":float(m2[original_hi]),
                    "source_bracket_sha256":receipt["c32_native_z3_bracket_sha256"]})
            else:
                receipt["c32_native_z3_bracket"]=None
                event(f,"c32_native_z3_bracket_missing",{"z_max":float(np.max(z)),
                      "z_min":float(np.min(z))})

            # Preserve c24's fail-closed, in-domain nonfinite row count even
            # if the full-history consistency check fails before z-window export.
            if not np.all(np.isfinite(z)):
                raise RuntimeError("nonfinite CLASS redshift coordinate in full native history")
            inside_precheck=(z>=0)&(z<=3)
            finite_native=(np.isfinite(phi)&np.isfinite(mr)&np.isfinite(m2)&
                           np.isfinite(meff2)&np.isfinite(hubble))
            receipt["input_native_nonfinite_count"]=int(np.count_nonzero(
                inside_precheck&~finite_native))
            receipt["c30_native_full_nonfinite_rows"]=int(np.count_nonzero(~finite_native))
            if receipt["c30_native_full_nonfinite_rows"] or np.any(hubble<=0):
                raise RuntimeError("RIMS mass/H or matter columns contain nonfinite values or H<=0")
            independent_ratio=meff2/(hubble*hubble)
            abs_delta=np.abs(independent_ratio-m2)
            receipt["c30_max_mass_ratio_reconstruction_error"]=float(np.max(abs_delta))
            if not np.allclose(m2,independent_ratio,rtol=5e-8,atol=1e-10):
                raise RuntimeError("RIMS stability ratio inconsistent with m_eff^2 / H^2: maximum absolute difference "+
                                   str(receipt["c30_max_mass_ratio_reconstruction_error"]))
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
    binary=class_compiled_module_path(classy)
    if not any(str(binary).endswith(x) for x in importlib.machinery.EXTENSION_SUFFIXES):
        raise RuntimeError("Class is not backed by native compiled extension: "+str(binary))
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
