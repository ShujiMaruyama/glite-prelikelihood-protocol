#!/usr/bin/env python3
"""C44 one original frozen case, one CLASS.compute, C43 telemetry. No viability claim."""
import argparse,hashlib,json,os,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"c24"))
import c23_freeze as freeze
import c24_native_background as native
from c37_exact_shooting_probe import exact_params
from c43_phase_audit import parse
CASE_SHA="9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284"
FREEZE_SHA="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
def sha(b):return hashlib.sha256(b).hexdigest()
def original_input(m):
    freeze.verify(m)
    assert m["freeze_hash"]==FREEZE_SHA and len(m["cases"])==81
    c=next(x for x in m["cases"] if x["id"]=="rims_002")
    assert c["input_sha256"]==CASE_SHA
    p=exact_params(c)
    assert p["rims_stability_tolerance"]==1e-10
    assert p["rims_enforce_stability"]=="yes"
    assert "tol_background_integration" not in p
    assert p["output"]=="" and not any(k in p for k in ("ic","non_linear","non linear"))
    return p
def run(a):
    if os.environ.get("RIMS_C43_NDF_TRACE")!="1":raise ValueError("trace must be enabled")
    m=json.loads(Path(a.manifest).read_text())
    p=original_input(m)
    lock=json.loads(Path(a.source_receipt).read_text())
    assert lock["original_source_blob_sha1"]=="0d293723510171ae9a732c80da32adb9ee52701f"
    assert lock["native_CLASS_executed"] is False
    assert "RIMS_C43_NDF_TRACE_V1" in (Path(a.class_source)/"tools/evolver_ndf15.c").read_text()
    classy=native.verify_pinned_environment(a.class_source,a.base_patch,a.delta_patch,m)
    binary=native.class_compiled_module_path(classy)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    text=json.dumps(p,sort_keys=True,indent=2,allow_nan=False)+"\n"
    (out/"original_input.json").write_text(text)
    receipt={"schema":"RIMS_C44_ONE_NATIVE_PHASE_TRACE_V1","case":"rims_002",
             "case_sha256":CASE_SHA,"freeze_sha256":FREEZE_SHA,
             "input_sha256":sha(text.encode()),"binary_sha256":sha(binary.read_bytes()),
             "ndf15_overlay_sha256":lock["source_after_sha256"],
             "compute_attempts":0,"retuned_shooting":False,"MCMC":False,
             "accepted_physical_g_measured":False,"numerical_convergence_proven":False,
             "normalization_proven":False,"physical_stability_proven":False}
    obj=None;start=time.monotonic()
    try:
        obj=classy.Class();obj.set(**p);receipt["compute_attempts"]=1
        obj.compute();receipt["native_status"]="UNEXPECTED_COMPUTE_RETURNED"
    except BaseException as ex:
        err=str(ex).encode("utf-8",errors="backslashreplace")
        tb="".join(traceback.format_exception(ex)).encode("utf-8",errors="backslashreplace")
        (out/"native_exception.txt").write_bytes(err)
        (out/"traceback.txt").write_bytes(tb)
        receipt.update(error_type=type(ex).__name__,error_sha256=sha(err),traceback_sha256=sha(tb))
        receipt["native_status"]=("ORIGINAL_SHOOTING_VETO"
          if receipt["compute_attempts"]==1 and type(ex).__name__=="CosmoComputationError"
          and b"Shooting failed" in err and b"RIMS stability gate failed" in err
          else "UNEXPECTED_NATIVE_EXCEPTION")
    finally:
        if obj is not None:
            try:obj.empty()
            except Exception as ex:receipt["cleanup_error"]=type(ex).__name__
        receipt["elapsed_seconds"]=time.monotonic()-start
        raw=Path(a.stderr).read_bytes() if Path(a.stderr).is_file() else b""
        receipt["stderr_sha256"]=sha(raw)
        try:
            audited=parse(raw.decode("utf-8",errors="strict"))
            audited["stderr_sha256"]=sha(raw)
            (out/"phase_audit.json").write_text(json.dumps(audited,indent=2,allow_nan=False)+"\n")
            receipt["phase_status"]=audited["status"]
            receipt["committed_steps"]=audited["committed_step_count_in_final_evolver"]
            receipt["last_committed_a"]=audited["last_committed_a"]
        except BaseException as ex:
            receipt["phase_status"]="INCOMPLETE_FAIL_CLOSED"
            receipt["phase_error"]=str(ex)[:1000]
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return 0 if (receipt["compute_attempts"]==1 and receipt["native_status"]=="ORIGINAL_SHOOTING_VETO"
                 and receipt["phase_status"]=="FAILED_NEWTON_TRIAL_CONFIRMED") else 3
def main():
    ap=argparse.ArgumentParser()
    for key in ("manifest","class-source","base-patch","delta-patch","source-receipt","stderr","out"):
        ap.add_argument("--"+key,required=True)
    return run(ap.parse_args())
if __name__=="__main__":raise SystemExit(main())
