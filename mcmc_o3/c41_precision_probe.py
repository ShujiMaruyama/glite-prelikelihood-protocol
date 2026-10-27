#!/usr/bin/env python3
"""One source-instrumented failed-shooting CLASS compute, controlled tolerance.
Only to be called from explicitly manual C41 GitHub workflow. Saves all
observations even when the CLASS failure differs from the C39 historical error.
"""
import argparse
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "c24"))
import c23_freeze as frozen
import c24_native_background as original
from c37_exact_shooting_probe import exact_params
from c41_precision_gate import EXPECTED_MODES, check_registry, precision_params, sha256, validate_native_record
from c39_audit_raw_stability_terms import parse_line, PREFIX


def run(manifest_path, class_source, base_patch, delta_patch, mode, out_path, stderr_path):
    check_registry()
    m=json.loads(Path(manifest_path).read_text());frozen.verify(m)
    case=next(c for c in m["cases"] if c["id"]=="rims_002")
    params=precision_params(exact_params(case),mode)
    out=Path(out_path);out.mkdir(parents=True,exist_ok=False)
    (out/"native_input.json").write_text(json.dumps(params,indent=2,sort_keys=True,allow_nan=False)+"\n")
    classy=original.verify_pinned_environment(class_source,base_patch,delta_patch,m)
    binary=original.class_compiled_module_path(classy)
    receipt={"schema":"RIMS_C41_TIGHTENED_TOLERANCE_ONE_NATIVE_COMPUTE_V1",
        "run_mode":mode,"tol_background_integration":EXPECTED_MODES[mode],
        "case":"rims_002","case_sha256":case["input_sha256"],
        "freeze_sha256":m["freeze_hash"],"original_veto_tolerance":1e-10,
        "native_input_sha256":sha256((out/"native_input.json").read_bytes()),
        "compiled_CLASS_sha256":sha256(binary.read_bytes()),
        "compute_calls_attempted":0,"MCMC":False,"retuned_shooting":False,
        "new_unique_parameter_cases":0,"normalized_final_background_certified":False,
        "numerical_convergence_demonstrated":False}
    obj=None;t0=time.monotonic()
    try:
        obj=classy.Class();obj.set(**params)
        receipt["compute_calls_attempted"]=1
        obj.compute()
        receipt["status"]="RETURNED_WITHOUT_VETO_NOT_A_NORMALIZED_BACKGROUND_CERTIFICATE"
    except BaseException as exc:
        full=str(exc).encode("utf-8",errors="backslashreplace")
        trace="".join(traceback.format_exception(exc)).encode("utf-8",errors="backslashreplace")
        (out/"native_exception.txt").write_bytes(full)
        (out/"python_traceback.txt").write_bytes(trace)
        receipt.update(error_type=type(exc).__name__, full_exception_sha256=sha256(full),
                       traceback_sha256=sha256(trace), full_exception_bytes=len(full))
        receipt["status"] = ("SHOOTING_FAILED_WITH_VETO" if
            receipt["compute_calls_attempted"]==1 and type(exc).__name__=="CosmoComputationError"
            and b"Shooting failed" in full and b"RIMS stability gate failed" in full
            else "UNEXPECTED_NATIVE_EXCEPTION")
    finally:
        if obj is not None:
            try: obj.empty()
            except Exception as exc:receipt["cleanup_exception"]=str(exc)
        receipt["elapsed_seconds"]=time.monotonic()-t0
        # The diagnostic C layer prints the source record to native stderr.
        b=Path(stderr_path).read_bytes() if Path(stderr_path).exists() else b""
        lines=b.decode("utf-8",errors="replace").splitlines()
        records=[];parse_error=None
        for line in lines:
            if line.startswith(PREFIX+" "):
                try:
                    parsed=parse_line(line)
                    validate_native_record(parsed)
                    records.append(parsed)
                except Exception as e:
                    parse_error=type(e).__name__+": "+str(e)
        receipt["native_stderr_sha256"]=sha256(b)
        receipt["all_veto_records"]=records
        receipt["all_veto_records_count"]=len(records)
        receipt["native_record_parse_error"]=parse_error
        receipt["source_evidence_status"]=("SOURCE_RECORD_UNAVAILABLE" if not records or parse_error
                                             else "NATIVE_VETO_SOURCE_ARITHMETIC_CHECKED")
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")
    # Fail-closed. Workflow artifact persists even for unexpected outcomes.
    if receipt["compute_calls_attempted"]!=1 or receipt["status"]!="SHOOTING_FAILED_WITH_VETO" or not records or parse_error:
        return 3
    return 0


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--class-source",required=True)
    p.add_argument("--base-patch",required=True)
    p.add_argument("--delta-patch",required=True)
    p.add_argument("--mode",choices=sorted(EXPECTED_MODES),required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--stderr",required=True)
    a=p.parse_args()
    exit_code=run(a.manifest,a.class_source,a.base_patch,a.delta_patch,a.mode,a.out,a.stderr)
    print("C41_NATIVE_RESULT_RECORDED exit_code",exit_code,"NOT_CONVERGENCE_CERTIFIED")
    raise SystemExit(exit_code)

if __name__=="__main__":main()
