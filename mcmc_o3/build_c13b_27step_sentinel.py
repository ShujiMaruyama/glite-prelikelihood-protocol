#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import yaml

MANIFEST_SHA="9af4ade6c9c40d8c81f299d239eaae27019bdbc12ff94e139af528ed8fd35da4"
RIDGE_COV_SHA="543c014fa0ba20d0219afeca339b34e473661940d8ff0fde8b9fe2b1c270da9b"
SCALES=[4.0,4.8,5.7]
SLOW=["q_H","omega_b","omega_dm","logA","n_s","tau_reio","Omega_scf","rims_alpha_U","rims_shell_u_i"]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify(root):
    m=root/"SHA256SUMS.txt"
    assert sha(m)==MANIFEST_SHA
    for line in m.read_text().splitlines():
        if not line.strip(): continue
        h, rel=line.split(None,1)
        p=root/rel.strip().lstrip("*").lstrip("./")
        assert p.exists() and sha(p)==h, p

def target_view(d):
    keep=["prior","value","min","max","derived","periodic","drop"]
    return {"likelihood":d["likelihood"],"theory":d["theory"],
            "params":{k:({x:v[x] for x in keep if x in v} if isinstance(v,dict) else v)
                      for k,v in d["params"].items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--c13-dir",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    src=Path(a.c13_dir); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    verify(src)
    assert sha(src/"rims_c13_ridge_preserving.covmat")==RIDGE_COV_SHA
    assert (src/"c13_5p7_exit_code.txt").read_text().strip()=="124"

    cov=out/"rims_c13b_ridge_preserving.covmat"
    cov.write_bytes((src/"rims_c13_ridge_preserving.covmat").read_bytes())
    base=yaml.safe_load((src/"rims_c13_full_drag_5p7.yaml").read_text())
    frozen=target_view(base)
    for scale in SCALES:
        tag=str(scale).replace(".","p")
        y=json.loads(json.dumps(base))
        y["output"]=f"chains_c13b/rims_c13b_27step_{tag}"
        m=y["sampler"]["mcmc"]
        m["covmat"]=str(cov)
        m["proposal_scale"]=float(scale)
        m["learn_proposal"]=False
        m["drag"]=True
        m["blocking"]=[[1,SLOW],[243,["A_planck"]]]
        m["oversample_power"]=0.4
        m["oversample_thin"]=True
        m["measure_speeds"]=True
        assert target_view(y)==frozen
        (out/f"rims_c13b_27step_{tag}.yaml").write_text(
            yaml.safe_dump(y,sort_keys=False,allow_unicode=True,width=160)
        )

    meta={
      "schema":"rims-phaseii-o3-c13b-27step-preflight-v1",
      "source_run_id":37887669578,
      "source_artifact_id":11597154860,
      "source_eligible_for_inference":False,
      "target_distribution_changed":False,
      "coordinate_map_changed":False,
      "proposal_covariance_changed":False,
      "target_drag_steps":27,
      "manual_blocking":[[1,SLOW],[243,["A_planck"]]],
      "tested_scales":SCALES,
      "minutes_per_scale":18,
      "automatic_follow_on":False,
      "automatic_long_run":False,
      "samples_eligible_for_inference":False,
      "production_gate":{"GetDist_Rminus1_lt":0.01,"minimum_headline_ESS_ge":1000.0}
    }
    (out/"C13B_27STEP_PREFLIGHT.json").write_text(json.dumps(meta,indent=2,sort_keys=True))
    lines=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS.txt":
            lines.append(f"{sha(p)}  {p.name}")
    (out/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n")
    print(json.dumps(meta,indent=2,sort_keys=True))
if __name__=="__main__": main()
