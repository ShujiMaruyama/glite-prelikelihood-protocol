#!/usr/bin/env python3
"""Read-only c33 evidence audit. No CLASS/MCMC execution, and no physics promotion."""
import argparse,hashlib,json,math,zipfile
from pathlib import Path

RUN_ID=40247625798
ORIGINAL_SHA="5263f9489ada68adcc76c6d5e756ea95b3dfff40dec2448d2f87cea0efbe85dd"
FREEZE="0893eb71e09208c2579652d405f54277647f92ce1de33ee8a0e492ce2547cda0"

def sha(x):return hashlib.sha256(x).hexdigest()
def obj(z,p):return json.loads(z.read(p))

def analyse(path,expected_sha=ORIGINAL_SHA):
    if sha(Path(path).read_bytes())!=expected_sha:raise ValueError("Source c32 archive SHA mismatch")
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError("Damaged original c32 artifact")
        names=set(z.namelist());attested=set()
        for line in z.read("SHA256SUMS.txt").decode().splitlines():
            sig,name=line.split(None,1);name=name.removeprefix("./")
            if name not in names or name in attested or sig!=sha(z.read(name)):
                raise ValueError("Interior artifact SHA mismatch "+name)
            attested.add(name)
        if attested!=names-{"SHA256SUMS.txt"}:raise ValueError("Unattested ZIP content")
        m=obj(z,"C23_FROZEN_81.json")
        r=obj(z,"native/rims_000/receipt.json")
        old=obj(z,"c24_audit.json")
        a26=obj(z,"c26_occupancy_audit.json")
        a27=obj(z,"c27_full_history_audit.json")
        a32=obj(z,"c32_native_bracket_audit.json")
        log=z.read("native/rims_000/native_compute.log")
        hist=z.read("native/rims_000/c27_full_history_z_phi.json")
    cases=m.get("cases",[])
    if m.get("freeze_hash")!=FREEZE or len(cases)!=81 or len({c["input_sha256"] for c in cases})!=81:
        raise ValueError("Frozen c23 grid mismatch")
    c=cases[0]
    if (c["id"]!="rims_000" or r.get("case_sha256")!=c["input_sha256"] or
        r.get("source_freeze_hash")!=FREEZE or r.get("synthetic_fixture") is not False or
        r.get("MCMC") is not False or r.get("run_status")!="solver_completed"):
        raise ValueError("Pilot CLASS source case not authenticated")
    if sha(log)!=r.get("log_sha256") or sha(hist)!=r.get("c27_native_history_sha256"):
        raise ValueError("Raw log/history SHA mismatch")
    first=next(x for x in old["cases"] if x["id"]=="rims_000")
    if (first["status"]!="PHYSICAL_REJECT" or first["issues"]!=["z_0to3_coverage_failed"]
        or old["statuses"].get("NO_RECEIPT")!=80):
        raise ValueError("Historical strict physical decision has changed")
    if (a26.get("gate_pass") is not True or a27.get("gate_pass") is not True or
        a32.get("c32_status")!="NATIVE_GRID_BRACKETED_SAMPLED_PASS" or
        a32.get("other_80_cases_unattempted") is not True or
        a32["z3_boundary_estimate"].get("is_exact_native_mesh_sample") is not False):
        raise ValueError("Underlying independent source/gate not verified")
    sample=r["background"]
    if len(sample)!=1721 or r.get("native_z_total_rows")!=40000:raise ValueError("Native row count differs")
    z=[a["z"] for a in sample];s=[a["s"] for a in sample];q=[a["m2_over_H2"] for a in sample]
    if (not all(math.isfinite(v) for v in z+s+q) or
        not all(z[i]<z[i+1] for i in range(len(z)-1)) or
        not all(0<=v<=3 for v in z) or not all(0<v<1 for v in s) or min(q)<-1e-10):
        raise ValueError("Invalid or unstable sampled background")
    if not math.isclose(min(q),r["native_min_m2_over_H2"],abs_tol=1e-13):
        raise ValueError("Native sampled stability minimum inconsistent")
    if not math.isclose(z[-1],a32["native_z_bracket"][0],abs_tol=1e-12):
        raise ValueError("Native final z lower bracket disagrees")
    xi_max=max(math.sqrt(max(v,0)) for v in q)
    xi_min=min(math.sqrt(max(v,0)) for v in q)
    lo,hi=min(s),max(s)
    umin,umax=math.sqrt(lo),math.sqrt(hi)
    h=(umax-umin)/2;uc=(umax+umin)/2
    sagitta=c["alpha_U"]*h*h
    relative=h*h/(1-uc*uc)
    verdict="shielded" if xi_max<1 else ("transitional" if xi_max<10 else "resolved_QS")
    return {
        "schema":"rims-c33-real-c32-pilot-identifiability-no-likelihood-v1",
        "original_github_run":RUN_ID,"original_zip_sha256":expected_sha,
        "frozen_81_sha256":FREEZE,"physically_attempted_cases":1,"unattempted_cases":80,
        "case_id":"rims_000","input_sha256":c["input_sha256"],
        "potential":c["potential"],"alpha_U":c["alpha_U"],
        "omega_phi0":c["omega_phi0"],"s_i":c["s_i"],
        "native_sample_count":len(sample),"native_history_rows":r["native_z_total_rows"],
        "min_Xi_native":xi_min,"max_Xi_native":xi_max,
        "visibility_native_only":verdict,
        "s_span_native":hi-lo,"s_min_native":lo,"s_max_native":hi,
        "intrinsic_W_sagitta":sagitta,
        "intrinsic_fractional_W_sagitta":relative,
        "ideal_three_node_5sigma_50pctpower_relative_intrinsic_W_noise_ceiling":
            2*relative/(5*math.sqrt(1.5)),
        "actual_survey_noise_forecast":False,"fifth_force_detected":False,
        "legacy_c24_status":"PHYSICAL_REJECT",
        "separate_c32_status":"NATIVE_GRID_BRACKETED_SAMPLED_PASS",
        "continuous_stability_proved":False,
        "independent_second_solver_proved":False,
        "production_posterior":False,
        "fixed_case_ledger":[{
            "case_id":x["id"],"input_sha256":x["input_sha256"],
            "potential":x["potential"],"alpha_U":x["alpha_U"],
            "omega_phi0":x["omega_phi0"],"s_i":x["s_i"],
            "source_status":"SAMPLED_C32_AUDITED" if x["id"]=="rims_000" else "NOT_ATTEMPTED",
            "observational_promotion":False} for x in cases],
        "production_Rminus1_strict_lt":0.01,"production_min_headline_ESS_ge":1000
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise SystemExit("Refusing to overwrite c33 output")
    d=analyse(a.source_zip)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("C33_ONLY_NATIVE_PILOT",d["visibility_native_only"],"Xi_max",d["max_Xi_native"],
          "unattempted",d["unattempted_cases"])
if __name__=="__main__":main()
