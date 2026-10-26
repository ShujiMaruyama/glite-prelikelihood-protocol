#!/usr/bin/env python3
"""c35 strictly fixed two-case native RIMS comparison, manual-only.

Only frozen rims_001 and rims_002 are run; authentic c32 rims_000 is
preserved and must NEVER be resubmitted here. An invalid physical solution is
recorded rather than selecting or substituting a case. No CLASS dependency
for --plan-only; never MCMC, 81-case scan, or unattended follow-on.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
from c23_freeze import verify

CASES=("rims_001","rims_002")
FROZEN="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"
REAL_C32_BASELINE_SHA="5263f9489ada68adcc76c6d5e756ea95b3dfff40dec2448d2f87cea0efbe85dd"

def sign(s):
    if abs(s-1/3)<1e-12:return "ZERO"
    return "POSITIVE" if s<1/3 else "NEGATIVE"

def plan(manifest):
    verify(manifest)
    if manifest["freeze_hash"]!=FROZEN:raise ValueError("Frozen 81-grid altered")
    chosen=[manifest["cases"][i] for i in (0,1,2)]
    if tuple(c["id"] for c in chosen)!=("rims_000",)+CASES:
        raise ValueError("Frozen contrast cases changed")
    for key in ("potential","alpha_U","omega_phi0","fixed_background"):
        if chosen[0][key]!=chosen[1][key] or chosen[0][key]!=chosen[2][key]:
            raise ValueError("Not a controlled s_i-only physical contrast: "+key)
    if [sign(c["s_i"]) for c in chosen]!=["POSITIVE","ZERO","NEGATIVE"]:
        raise ValueError("Predeclared mass-curvature sign contrast corrupted")
    return {"schema":"rims-c35-predeclared-three-occupancy-contrast-v1",
        "frozen_81_sha256":FROZEN,
        "historic_reference":{"case_id":"rims_000",
            "original_real_c32_zip_sha256":REAL_C32_BASELINE_SHA,
            "must_not_reexecute":True},
        "new_exact_cases":list(CASES),
        "frozen_case_sha256":{c["id"]:c["input_sha256"] for c in chosen},
        "expected_start_mass_curvature_sign":{
            c["id"]:sign(c["s_i"]) for c in chosen},
        "analytic_initial_beta":{c["id"]:c["alpha_U"]*(1-c["s_i"]) for c in chosen},
        "conditional_massless_dark_dark_Gamma_proxy":{
            c["id"]:2*(c["alpha_U"]*(1-c["s_i"]))**2 for c in chosen},
        "real_survey_prediction":False,
        "new_native_cases_executed":0,"MCMC":False,"automatic_follow_on":False}

def run(manifest,root,runner,source,base,delta,timeout):
    design=plan(manifest)
    root=Path(root)
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("Refusing overwrite/restart; protect previous native case receipts")
    root.mkdir(parents=True,exist_ok=True)
    if not 1<=timeout<=900:raise ValueError("Per-case timeout must be 1..900 seconds")
    records=[]
    for case_id in CASES:
        case_folder=root/"native"/case_id
        if case_folder.exists():raise FileExistsError("Existing case cannot be overwritten")
        cmd=[sys.executable,str(runner),"--manifest",str(source["manifest"]),
             "--output",str(root/"native"),"--class-source",str(source["class"]),
             "--base-patch",str(base),"--delta-patch",str(delta),"--one",case_id]
        timed_out=False
        try:
            response=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,check=False)
            rc=response.returncode;out=response.stdout;err=response.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out=True;rc=124
            out=exc.stdout.decode(errors="replace") if isinstance(exc.stdout,bytes) else (exc.stdout or "")
            err=exc.stderr.decode(errors="replace") if isinstance(exc.stderr,bytes) else (exc.stderr or "")
        (root/(case_id+".runner.stdout.txt")).write_text(out)
        (root/(case_id+".runner.stderr.txt")).write_text(err)
        rec=case_folder/"receipt.json"
        receipt=None
        if rec.exists():
            try:receipt=json.loads(rec.read_text())
            except (OSError,ValueError):pass
        records.append({"case_id":case_id,"expected_sha256":design["frozen_case_sha256"][case_id],
            "subprocess_returncode":rc,"timed_out":timed_out,
            "receipt_exists":receipt is not None,
            "native_run_status":receipt.get("run_status") if isinstance(receipt,dict) else None,
            "no_science_promotion":True})
        # A failed solver is a legitimate recorded attempted trajectory.
        # Always attempt the OTHER predeclared case; never substitute cases.
    result={"schema":"rims-c35-two-case-attempt-ledger-v1",
        "plan":design,"records":records,
        "complete_attempt_recording":all(x["receipt_exists"] for x in records),
        "all_solver_completed":all(x["native_run_status"]=="solver_completed" for x in records),
        "physical_gate_is_automatic_pass":False,
        "do_not_use_as_production_posterior":True}
    (root/"c35_attempt_ledger.json").write_text(
        json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--runner",type=Path)
    p.add_argument("--class-source",type=Path)
    p.add_argument("--base-patch",type=Path)
    p.add_argument("--delta-patch",type=Path)
    p.add_argument("--timeout-seconds",type=int,default=600)
    args=p.parse_args()
    frozen=json.loads(args.manifest.read_text())
    if args.plan_only:
        if args.output.exists():raise FileExistsError("Plan exists")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(plan(frozen),indent=2,sort_keys=True)+"\n")
        print("ONLY analytic plan; native physical attempts=0")
        return
    if any(x is None for x in (args.runner,args.class_source,args.base_patch,args.delta_patch)):
        p.error("physical two-case mode requires runner, CLASS source and 2 locked patch paths")
    result=run(frozen,args.output,args.runner,{"manifest":args.manifest,"class":args.class_source},
               args.base_patch,args.delta_patch,args.timeout_seconds)
    print("c35 ATTEMPTED",[(x["case_id"],x["native_run_status"]) for x in result["records"]])
    if not result["complete_attempt_recording"]:
        raise SystemExit("Incomplete execution receipts; do NOT claim contrast evaluated")

if __name__=="__main__":main()
