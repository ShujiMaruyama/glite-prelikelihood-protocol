#!/usr/bin/env python3
"""Read-only-frozen-input, single native CLASS shooting-error diagnostic (not MCMC)."""
import argparse,hashlib,json,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
import c23_freeze as frozen
import c24_native_background as original
CASE="rims_002"
ORIGINAL_SHA="9bc753d2dd2843160e43ca9c37e4480d78513ef372ee9618831cc4447da6a284"
PREF=4.11730971054
def exact_params(case):
    if case["id"]!=CASE or case["input_sha256"]!=ORIGINAL_SHA:raise ValueError("Only original frozen rims_002")
    d=original.base_args(case)
    if d["output"]!="" or "ic" in d or "non_linear" in d:raise ValueError("Inputs changed")
    d.update(rims_phi_ref=PREF,rims_require_normalization="no")
    return d
def single_probe(classy,case,manifest,out,binary):
    frozen.verify(manifest)
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    params=exact_params(case)
    inp=json.dumps(params,sort_keys=True,allow_nan=False).encode()
    (out/"original_input.json").write_bytes(inp)
    receipt={"schema":"rims-c37-full-shooting-diagnostic-v1","case_id":CASE,
        "case_sha256":ORIGINAL_SHA,"freeze_sha256":manifest["freeze_hash"],
        "original_failed_run_id":40269433141,"compute_attempts":0,
        "input_sha256":hashlib.sha256(inp).hexdigest(),
        "compiled_CLASS_sha256":hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
        "normalization_or_final_background_certified":False,
        "retuned_parameters":False,"MCMC":False}
    t=time.monotonic();obj=None
    try:
        obj=classy.Class();obj.set(**params)
        receipt["compute_attempts"]=1
        obj.compute()
        receipt["status"]="FIRST_COMPUTE_RETURNED_NOT_A_NORMALIZED_BACKGROUND"
    except BaseException as exc:
        message=str(exc).encode("utf-8",errors="backslashreplace")
        frames="".join(traceback.format_exception(exc)).encode("utf-8",errors="backslashreplace")
        (out/"full_CLASS_exception.txt").write_bytes(message)
        (out/"full_python_traceback.txt").write_bytes(frames)
        # c35's original receipt kept only the first 1,000 characters.
        # Compare that immutable prefix separately; never call a different
        # native shooting cause byte-identical merely because its class matches.
        legacy_prefix=str(exc)[:1000].encode("utf-8",errors="backslashreplace")
        receipt["c35_original_truncated_error_prefix_sha256"]="eb8b7a6e5e52cec209141a7c359c5e6947b5479bb076df592558853b41b4beaf"
        receipt["c35_failure_prefix_matches"]=(
            hashlib.sha256(legacy_prefix).hexdigest()==receipt["c35_original_truncated_error_prefix_sha256"])
        receipt["error_type"]=type(exc).__name__
        receipt["full_error_bytes"]=len(message)
        receipt["error_sha256"]=hashlib.sha256(message).hexdigest()
        receipt["traceback_sha256"]=hashlib.sha256(frames).hexdigest()
        receipt["status"]=("ORIGINAL_SHOOTING_FAILURE_REPRODUCED" if
            receipt["compute_attempts"]==1 and type(exc).__name__=="CosmoComputationError"
            and b"Shooting failed" in message else "OTHER_ERROR")
    finally:
        if obj is not None:
            try:obj.empty()
            except Exception as exc:receipt["cleanup_error"]=str(exc)
        receipt["seconds"]=time.monotonic()-t
        (out/"receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return receipt
def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--class-source",type=Path,required=True)
    p.add_argument("--base-patch",type=Path,required=True);p.add_argument("--delta-patch",type=Path,required=True)
    p.add_argument("--one",choices=[CASE],required=True)
    a=p.parse_args();m=json.loads(a.manifest.read_text());frozen.verify(m)
    c=next(x for x in m["cases"] if x["id"]==a.one)
    classy=original.verify_pinned_environment(a.class_source,a.base_patch,a.delta_patch,m)
    r=single_probe(classy,c,m,a.output,original.class_compiled_module_path(classy))
    print("C37 first CLASS compute:",r["status"],"full_exception_bytes",r.get("full_error_bytes",0))
    if r["status"]!="ORIGINAL_SHOOTING_FAILURE_REPRODUCED":raise SystemExit(3)
if __name__=="__main__":main()
