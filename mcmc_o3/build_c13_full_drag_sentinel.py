#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import yaml

C12_RUN_ID=37874107719
C12_ARTIFACT_ID=11593256251
C12_ARTIFACT_DIGEST="sha256:85f5fa21630d9827295bd3b8279a732638996dddcd2ba9752f52f5e953912a81"
C12_MANIFEST_SHA="cb75d10c7f5e5ea7f755963fdf274c9d7327dc199f7ce52adc34771712d79def"
C12_AUDIT_SHA="796b317ee12835c8cd2a5e1fb6b574a1551076cfcc6106c45139eed7954b997e"
C12_PREFLIGHT_SHA="141961df8ec9c6479293fd8a34ae2186dd20d320464a3892e99f3a9b826e4ca4"
RIDGE_COV_SHA="543c014fa0ba20d0219afeca339b34e473661940d8ff0fde8b9fe2b1c270da9b"
SCALES=[5.7,7.0,8.2]
SLOW=["q_H","omega_b","omega_dm","logA","n_s","tau_reio","Omega_scf","rims_alpha_U","rims_shell_u_i"]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_manifest(root:Path):
    m=root/"SHA256SUMS.txt"
    assert sha(m)==C12_MANIFEST_SHA
    for line in m.read_text().splitlines():
        if not line.strip(): continue
        h, rel=line.split(None,1); rel=rel.strip().lstrip("*").lstrip("./")
        p=root/rel
        assert p.exists() and sha(p)==h, rel

def target_view(d):
    keep=["prior","value","min","max","derived","periodic","drop"]
    return {"likelihood":d["likelihood"],"theory":d["theory"],
            "params":{k:({x:v[x] for x in keep if x in v} if isinstance(v,dict) else v)
                      for k,v in d["params"].items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--c12-dir",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    src=Path(a.c12_dir); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    verify_manifest(src)
    assert sha(src/"C12_DRAG_RIDGE_AUDIT.json")==C12_AUDIT_SHA
    assert sha(src/"C12_DRAG_RIDGE_PREFLIGHT.json")==C12_PREFLIGHT_SHA
    assert sha(src/"rims_c12_ridge_preserving.covmat")==RIDGE_COV_SHA
    audit=json.loads((src/"C12_DRAG_RIDGE_AUDIT.json").read_text())
    assert audit["eligible_for_inference"] is False
    assert audit["log_audit"]["fatal_markers"]==[]
    assert audit["production_gate"]["GetDist_Rminus1_lt"]==0.01
    assert audit["production_gate"]["minimum_headline_ESS_ge"]==1000.0

    cov=out/"rims_c13_ridge_preserving.covmat"
    cov.write_bytes((src/"rims_c12_ridge_preserving.covmat").read_bytes())
    base=yaml.safe_load((src/"rims_c12_drag_ridge.yaml").read_text())
    frozen=target_view(base)
    yamls=[]
    for scale in SCALES:
        tag=str(scale).replace(".","p")
        y=json.loads(json.dumps(base))
        y["output"]=f"chains_c13/rims_c13_full_drag_{tag}"
        m=y["sampler"]["mcmc"]
        m["covmat"]=str(cov)
        m["proposal_scale"]=float(scale)
        m["learn_proposal"]=False
        m["drag"]=True
        m["oversample_power"]=1.0
        m["blocking"]=[[1,SLOW],[27,["A_planck"]]]
        m["oversample_thin"]=True
        m["measure_speeds"]=True
        assert target_view(y)==frozen
        p=out/f"rims_c13_full_drag_{tag}.yaml"
        p.write_text(yaml.safe_dump(y,sort_keys=False,allow_unicode=True,width=160))
        yamls.append(p.name)

    meta={
      "schema":"rims-phaseii-o3-c13-full-drag-preflight-v1",
      "role":"bounded_nonproduction_full_drag_scale_sentinel",
      "source":{"run_id":C12_RUN_ID,"artifact_id":C12_ARTIFACT_ID,"digest":C12_ARTIFACT_DIGEST},
      "source_samples_eligible_for_inference":False,
      "target_distribution_changed":False,
      "coordinate_map_changed":False,
      "proposal_covariance_changed_from_c12_drag_ridge":False,
      "tested_scales":SCALES,
      "oversample_power":1.0,
      "manual_blocking":[[1,SLOW],[27,["A_planck"]]],
      "required_runtime_drag_marker":"* 27 : (['A_planck'],)",
      "minutes_per_scale":18,
      "selection_rule":{
        "aggregate_acceptance":[0.20,0.50],
        "per_chain_acceptance":[0.10,0.65],
        "minimum_distinct_rows_per_chain":10,
        "choose":"among passing scales, minimize |aggregate_acceptance-0.30|; tie -> lower scale; if none pass -> stop"
      },
      "automatic_follow_on":False,
      "automatic_long_run":False,
      "samples_eligible_for_inference":False,
      "production_gate":{"GetDist_Rminus1_lt":0.01,"minimum_headline_ESS_ge":1000.0},
      "claim_boundary":{"production_posterior":False,"Bayes_factor":False,"model_preference":False,"LambdaCDM_competitiveness_verified":False},
      "c12_context":{
        "aggregate_acceptance":audit["aggregate_acceptance"],
        "worst_rank_Rhat":audit["worst_rank_Rhat"],
        "minimum_bulk_ESS":audit["minimum_bulk_ESS"],
        "minimum_tail_ESS":audit["minimum_tail_ESS"],
        "leading_between_within_generalized_eigenvalue":audit["leading_between_within_generalized_eigenvalue"],
        "observed_drag_marker":audit["log_audit"]["blocking_markers"]
      }
    }
    (out/"C13_FULL_DRAG_PREFLIGHT.json").write_text(json.dumps(meta,indent=2,sort_keys=True))
    lines=[]
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS.txt":
            lines.append(f"{sha(p)}  {p.name}")
    (out/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n")
    print(json.dumps(meta,indent=2,sort_keys=True))
if __name__=="__main__": main()
