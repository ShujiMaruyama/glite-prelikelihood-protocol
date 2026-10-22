#!/usr/bin/env python3
"""Failure-preserving audit of pinned RIMS CLASS background attempts. Not cryptographic attestation."""
import argparse,collections,hashlib,json,math
from pathlib import Path
from c23_freeze import build_manifest,verify

def sha_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finite(x):return isinstance(x,(int,float)) and math.isfinite(float(x))

def audit_case(case,m,folder):
    p=folder/"receipt.json";log=folder/"native_compute.log"
    if not p.is_file():return {"id":case["id"],"status":"NO_RECEIPT","issues":["no receipt"]}
    issues=[]
    try:r=json.loads(p.read_text())
    except Exception:return {"id":case["id"],"status":"PROVENANCE_GATE_FAIL","issues":["invalid receipt JSON"]}
    frozen={"id":case["id"],"case_sha256":case["input_sha256"],
        "source_freeze_hash":m["freeze_hash"],"Class_upstream_commit":m["Class_upstream_commit"],
        "RIMS_patch_sha256":m["RIMS_patch_sha256"],"schema":"rims-c23-native-background-attempt-v1",
        "MCMC":False,"synthetic_fixture":False,"code_version":"c28_native_background_v4"}
    for k,v in frozen.items():
        if r.get(k)!=v:issues.append("bad_"+k)
    n=r.get("native_compute_attempts")
    if not isinstance(n,int) or n<0:issues.append("invalid_native_attempt_count")
    if not log.is_file():issues.append("missing_native_event_log")
    else:
        if sha_file(log)!=r.get("log_sha256"):issues.append("native_log_sha256_mismatch")
        events=[]
        for j,line in enumerate(log.read_text().splitlines()):
            try:
                event=json.loads(line)
                if not isinstance(event,dict) or "event" not in event:raise ValueError()
                events.append(event)
            except (ValueError,TypeError):issues.append("invalid_event_"+str(j))
        setups=[e for e in events if e.get("event")=="native_setup_exception"]
        extracts=[e for e in events if e.get("event")=="native_extract_exception"]
        if n==0 and r.get("run_status")=="solver_error" and not setups:
            issues.append("zero_native_calls_without_recorded_setup_failure")
        if n==0 and r.get("run_status")=="solver_completed":
            issues.append("zero_native_calls_in_successful_receipt")
        if setups and (r.get("run_status")!="solver_error" or
                       any(e.get("stage") not in ("Class_constructor","Class.set") for e in setups)):
            issues.append("invalid_setup_exception_event")
        if extracts and r.get("run_status")!="solver_error":
            issues.append("extraction_error_in_success_receipt")
        starts=[e for e in events if e.get("event")=="native_compute_start"]
        exits=[e for e in events if e.get("event") in ("native_compute_end","native_compute_exception")]
        if len(starts)!=n:issues.append("native_log_compute_count_mismatch")
        if [e.get("index") for e in starts]!=list(range(1,len(starts)+1)):issues.append("native_event_index_noncontiguous")
        start_by_index={e.get("index"):e for e in starts}
        done=set()
        for e in exits:
            index=e.get("index")
            if index not in start_by_index or index in done:issues.append("orphan_or_duplicate_native_exit")
            elif e.get("kind")!=start_by_index[index].get("kind"):issues.append("native_event_kind_changed")
            done.add(index)
        if done!=set(start_by_index):issues.append("unpaired_native_compute_start")
        if len(extracts)>1:
            issues.append("duplicate_background_extract_exception")
        for e in exits:
            if e.get("event")=="native_compute_end" and e.get("success") is not True:
                issues.append("native_compute_end_without_success_flag")
        for e in extracts:
            idx=e.get("index")
            if idx not in start_by_index or idx not in done or e.get("kind")!=start_by_index[idx].get("kind"):
                issues.append("extract_exception_without_successful_native_compute")
        if setups and len(setups)>1:
            issues.append("duplicate_setup_exception")
        if r.get("run_status")=="solver_completed":
            if any(e.get("event")=="native_compute_exception" for e in exits):issues.append("native_exception_in_successful_receipt")
            if sum(e.get("kind")=="final_background" for e in starts)!=1:issues.append("full_compute_not_once")
            if sum(e.get("kind")=="normalization_background" for e in starts)<1:issues.append("normalization_never_computed")
            if sum(e.get("kind")=="normalization_background" for e in starts)!=r.get("native_normalization_steps"):issues.append("normalization_step_count_mismatch")
    if not isinstance(r.get("binary_sha256"),str) or len(r["binary_sha256"])!=64:
        issues.append("unlocked_native_binary_hash")
    if not r.get("binary_path"):issues.append("missing_native_binary_path")
    if r.get("run_status") not in ("solver_completed","solver_error"):issues.append("invalid_run_status")
    if issues:return {"id":case["id"],"status":"PROVENANCE_GATE_FAIL","issues":sorted(set(issues))}
    if r["run_status"]=="solver_error":
        if not r.get("failure_class"):return {"id":case["id"],"status":"PROVENANCE_GATE_FAIL","issues":["failure_reason_missing"]}
        return {"id":case["id"],"status":"SOLVER_FAILED","issues":[],"failure":r.get("failure_message")}
    b=r.get("background");reject=[]
    if not isinstance(b,list) or len(b)<2:return {"id":case["id"],"status":"PHYSICAL_REJECT","issues":["missing_background"]}
    for i,row in enumerate(b):
        if not isinstance(row,dict) or not all(finite(row.get(k)) for k in ("z","s","m2_over_H2","norm_err")):
            reject.append("bad_native_sample_"+str(i))
    if reject:return {"id":case["id"],"status":"PHYSICAL_REJECT","issues":reject}
    z=[x["z"] for x in b];s=[x["s"] for x in b];m2=[x["m2_over_H2"] for x in b]
    if len(set(z))!=len(z):reject.append("duplicate_native_redshift")
    if min(z)>1e-6 or max(z)<3-1e-6:reject.append("z_0to3_coverage_failed")
    if any(x<0 or x>3 for x in z):reject.append("out_of_range_z")
    if any(not 0<x<1 for x in s):reject.append("mass_shell_occupancy_out_of_bounds")
    if max(abs(x["norm_err"]) for x in b)>=1e-8:reject.append("mass_normalization_failed")
    if min(m2)<-1e-10:reject.append("unstable_effective_mass")
    if r.get("input_native_nonfinite_count")!=0:reject.append("native_nonfinite_rows_recorded")
    if r.get("final_background_arrays_count")!=len(b):reject.append("raw_output_count_changed")
    if not finite(r.get("native_min_m2_over_H2")) or abs(r["native_min_m2_over_H2"]-min(m2))>1e-10:reject.append("mass_minimum_summary_changed")
    if r.get("normalization_iteration_success") is not True:reject.append("normalization_not_certified")
    if reject:return {"id":case["id"],"status":"PHYSICAL_REJECT","issues":reject}
    xi=max(math.sqrt(max(0.,x)) for x in m2)
    h=(math.sqrt(max(s))-math.sqrt(min(s)))/2
    uc=(math.sqrt(max(s))+math.sqrt(min(s)))/2
    return {"id":case["id"],"status":"PHYSICAL_VALID","issues":[],"max_Xi":xi,
        "visibility":("shielded" if xi<1 else "transitional" if xi<10 else "resolved_QS"),
        "s_span":[min(s),max(s)],"W_sagitta":case["alpha_U"]*h*h,
        "fractional_W_sagitta":h*h/(1-uc*uc),
        "idealized_three_node_expected_5sigma_50pct_power_relative_F_error_ceiling":2*h*h/((1-uc*uc)*5*math.sqrt(1.5)),
        "idealized_design_only":True,
        "native_compute_attempts":n,"binary_sha256":r["binary_sha256"]}
def audit(m,root):
    verify(m);root=Path(root)
    cases=[audit_case(c,m,root/c["id"]) for c in m["cases"]]
    counts=collections.Counter(c["status"] for c in cases)
    dirs={x.name for x in root.iterdir() if x.is_dir()} if root.exists() else set()
    unexpected=sorted(dirs-{c["id"] for c in m["cases"]})
    completed=(counts["NO_RECEIPT"]==0 and counts["PROVENANCE_GATE_FAIL"]==0 and not unexpected)
    native_bins={c["binary_sha256"] for c in cases if c["status"]=="PHYSICAL_VALID"}
    if len(native_bins)>1:completed=False
    return {"schema":"rims-c24-81-attempt-integrity-v1","source_freeze_hash":m["freeze_hash"],
      "native_provenance_level":"self-reported native execution receipts + GitHub runner log; not cryptographically independently attested",
      "statuses":dict(counts),"all_81_documented":completed,
      "all_81_physically_valid_under_declared_background_gates":bool(completed and counts["PHYSICAL_VALID"]==81),"binary_sha256_consistent_valid_cases":len(native_bins)<=1,
      "unexpected_directories":unexpected,"cases":cases,"physical_scan_pass":False,"MCMC":False,"automatic_follow_on":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--receipts",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--one")
    a=p.parse_args();d=audit(json.loads(a.manifest.read_text()),a.receipts)
    if a.out.exists():raise RuntimeError("audit exists; refusing overwrite")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"statuses":d["statuses"],"all_81_documented":d["all_81_documented"]}))
    if a.one:
        matching=[c for c in d["cases"] if c["id"]==a.one]
        if len(matching)!=1 or matching[0]["status"]!="PHYSICAL_VALID":raise SystemExit(2)
    elif not d["all_81_documented"]:raise SystemExit(2)
if __name__=="__main__":main()
