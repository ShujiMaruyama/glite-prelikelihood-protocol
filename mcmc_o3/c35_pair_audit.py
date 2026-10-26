#!/usr/bin/env python3
"""c35 read-only case-by-case gate across precisely rims_001 and rims_002.

A green GitHub job means two attempts and evidence checks completed, NOT that
every RIMS background or independent perturbation stability has passed.
"""
import argparse,json,math,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"c24"))
from c23_freeze import verify
from c24_audit import audit as legacy_audit
from c26_native_receipt_bridge import audit_native_receipt
from c27_history_integrity import audit_history
from c32_bracketed_endpoint_audit import bracket_audit
from c35_frozen_pair_run import plan,CASES

def audit_pair(manifest,root):
    design=plan(manifest)
    root=Path(root)
    reported=json.loads((root/"c35_attempt_ledger.json").read_text())
    records=reported.get("records",[])
    if [x.get("case_id") for x in records]!=list(CASES):
        raise ValueError("Predeclared physical contrast altered or dropped case")
    phys_root=root/"native"
    observed_dirs={p.name for p in phys_root.iterdir() if p.is_dir()} if phys_root.exists() else set()
    if observed_dirs!=set(CASES):
        raise ValueError("Missing/unexpected physical case directory: "+str(observed_dirs))
    orig=legacy_audit(manifest,phys_root)
    if orig["statuses"].get("NO_RECEIPT")!=79:
        raise ValueError("Fixed predeclared 81 ledger violated; expected 79 NO_RECEIPT")
    results=[];valid_provenance=True
    for cid in CASES:
        c=next(c for c in manifest["cases"] if c["id"]==cid)
        old=next(row for row in orig["cases"] if row["id"]==cid)
        rp=phys_root/cid/"receipt.json"
        r=json.loads(rp.read_text())
        if r.get("case_sha256")!=c["input_sha256"] or r.get("id")!=cid:
            raise ValueError("Wrong original source case")
        if old["status"]=="PROVENANCE_GATE_FAIL":
            valid_provenance=False
        one={"case_id":cid,"source_sha256":c["input_sha256"],
             "initial_occupation":c["s_i"],
             "predeclared_mass_curvature_sign":design["expected_start_mass_curvature_sign"][cid],
             "original_conservative_status":old["status"],
             "original_conservative_issues":old["issues"],
             "actual_native_compute_attempts":r.get("native_compute_attempts"),
             "source_is_synthetic_fixture":r.get("synthetic_fixture"),
             "c32_sampled_bracket_status":None,
             "c26_initial_gate":None,"c27_raw_history_gate":None,
             "full_perturbation_or_observation_claim":False}
        if old["status"] in ("PHYSICAL_REJECT","PHYSICAL_VALID"):
            c26=audit_native_receipt(manifest,r)
            one["c26_initial_gate"]=c26["gate"]
            history_path=phys_root/cid/"c27_full_history_z_phi.json"
            raw=history_path.read_bytes()
            c27=audit_history(manifest,r,json.loads(raw),raw)
            one["c27_raw_history_gate"]=c27["c26_gate"]
            if not(c26["gate_pass"] and c27["gate_pass"]):
                one["source_history_pass"]=False
            else:
                one["source_history_pass"]=True
                # Run the already verified c32 ONE-CASE independent gate
                # on an isolated read-only symlink. Never alter the original
                # 81-case denominator or c32 audit thresholds.
                with tempfile.TemporaryDirectory(prefix="c35_isolated_") as tmp:
                    (Path(tmp)/cid).symlink_to((phys_root/cid).resolve(),target_is_directory=True)
                    try:
                        b=bracket_audit(manifest,Path(tmp),cid)
                        one["c32_sampled_bracket_status"]=b["c32_status"]
                        samples=r["background"]
                        m2=[row["m2_over_H2"] for row in samples]
                        occup=[row["s"] for row in samples]
                        if any(not math.isfinite(v) for v in m2+occup):
                            raise ValueError("Bad sampled mass or occupancy")
                        one["native_z0to3_rows"]=len(samples)
                        one["native_sample_m2H2_min"]=min(m2)
                        one["native_max_Xi"]=math.sqrt(max(m2)) if min(m2)>=0 else None
                        one["native_beta_span"]=[
                            c["alpha_U"]*(1-max(occup)),c["alpha_U"]*(1-min(occup))]
                        one["native_occupation_span"]=[min(occup),max(occup)]
                        one["physical_observational_promotion"]=False
                    except ValueError as e:
                        one["c32_sampled_bracket_failure"]=str(e)[:500]
        elif old["status"]=="SOLVER_FAILED":
            one["scientific_status"]="SOLVER_FAILED_IS_RETAINED"
        else:
            one["scientific_status"]="NONPROMOTABLE_UNEXPECTED_NATIVE_STATE"
            valid_provenance=False
        results.append(one)
    return {"schema":"rims-c35-two-frozen-physical-attempts-audit-v1",
      "frozen_sha256":manifest["freeze_hash"],
      "prior_c32_reference_sha256":design["historic_reference"]["original_real_c32_zip_sha256"],
      "only_new_case_ids":list(CASES),
      "new_attempts_with_source_receipts":len(results),
      "other_79_absent_from_new_run":True,
      "previous_rims_000_original_not_rerun":True,
      "total_frozen_81_physically_attempted_after_pair_if_completed":3,
      "unattempted_after_pair_if_completed":78,
      "all_provenance_gates_clean":valid_provenance,
      "all_both_physically_bracketed":all(bool(x["c32_sampled_bracket_status"]) for x in results),
      "case_outcomes":results,
      "is_81_background_scan":False,
      "physical_viability_theorem":False,
      "independent_perturbation_solver":False,
      "production_likelihood_or_Bayes_factor":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--results",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    frozen=json.loads(a.manifest.read_text());verify(frozen)
    result=audit_pair(frozen,a.results)
    if a.out.exists():raise FileExistsError("Refusing to overwrite contrast audit")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("c35 exact 2 new native cases",result["all_provenance_gates_clean"],
          "source-bracketed cases",[x["case_id"] for x in result["case_outcomes"] if x["c32_sampled_bracket_status"]])
    if not result["all_provenance_gates_clean"]:
        raise SystemExit("Provenance defect; archive is evidence, NOT result promotion")

if __name__=="__main__":main()
